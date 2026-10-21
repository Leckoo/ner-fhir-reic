"""Baselines com LLM (Gemini, plano gratuito). Duas variantes:
 - gemini_e2e: o LLM gera o Bundle FHIR R5 direto do texto (LOINC pela memória do modelo).
 - gemini_ent: o LLM só extrai os trechos (exame, valor, unidade, faixa) e passa pela MESMA
   normalização e ligação LOINC do pipeline (comparação justa com o GLiNER).
Respostas ficam em cache (results/gemini/<variante>/<conjunto>/<id>.json) para reprodutibilidade
sem novas chamadas. A chave vem de GEMINI_API_KEY e nunca é impressa nem gravada."""
import os, json, time, pathlib, re
from pipeline import ligar_loinc, montar_obs, cabecalho, dedup

MODELO = "gemini-3.1-flash-lite"   # fixo: não trocar no meio da rodada
TEMPERATURA = 0.0
INTERVALO_S = 4.2                   # ~14 req/min (limite gratuito ~15 req/min)
_ult = [0.0]; _cli = [None]

PROMPT_E2E = """Você recebe o texto extraído de um laudo laboratorial brasileiro em PDF.
Gere um Bundle HL7 FHIR R5 (type "collection") contendo: um Patient (name.text, birthDate se houver),
uma Observation por exame (status "final", category laboratory, code com sistema http://loinc.org, código LOINC e display,
subject, effectiveDateTime = data do exame, valueQuantity com sistema http://unitsofmeasure.org e código UCUM,
referenceRange com low/high quando houver) e um DiagnosticReport (status "final", code LOINC 11502-2) referenciando as Observations.
Use fullUrl "urn:uuid:..." e referências por esses fullUrl. Converta valores para a unidade UCUM usual
(ex.: contagens por mm³ para 10*3/uL). Responda SOMENTE com o JSON do Bundle.

TEXTO DO LAUDO:
"""
PROMPT_ENT = """Você recebe o texto extraído de um laudo laboratorial brasileiro em PDF (pode ter erros de OCR).
Liste cada resultado de exame. Para cada um, copie EXATAMENTE como aparecem no texto:
"exame" (nome do exame), "valor" (resultado numérico), "unidade" e "faixa" (valor de referência).
Use null se não houver. Responda SOMENTE com JSON: {"exames": [{"exame": ..., "valor": ..., "unidade": ..., "faixa": ...}]}

TEXTO DO LAUDO:
"""

def _cliente():
    if _cli[0] is None:
        from google import genai
        from google.genai import types
        _cli[0] = genai.Client(http_options=types.HttpOptions(timeout=90_000))   # lê GEMINI_API_KEY do ambiente
    return _cli[0]

def chamar(prompt, tentativas=8):
    from google.genai import types
    espera = 10
    for t in range(tentativas):
        dt = time.time() - _ult[0]
        if dt < INTERVALO_S: time.sleep(INTERVALO_S - dt)
        _ult[0] = time.time(); t0 = time.time()
        try:
            r = _cliente().models.generate_content(model=MODELO, contents=prompt,
                config=types.GenerateContentConfig(temperature=TEMPERATURA, response_mime_type="application/json"))
            u = r.usage_metadata
            return {"texto": r.text, "latencia_s": time.time() - t0, "tentativas": t + 1,
                    "modelo": getattr(r, "model_version", None) or MODELO,
                    "tokens_entrada": getattr(u, "prompt_token_count", None), "tokens_saida": getattr(u, "candidates_token_count", None),
                    "tokens_total": getattr(u, "total_token_count", None)}
        except Exception as e:  # 503/429: espera e tenta de novo, mesmo modelo
            msg = re.sub(r"key=[^&\s]+", "key=***", str(e))[:200]
            print(f"  [gemini] tentativa {t+1} falhou: {msg}", flush=True)
            time.sleep(espera); espera = min(espera * 2, 120)
    raise RuntimeError("Gemini falhou após várias tentativas")

def _cache(variante, conj, doc_id, prompt):
    c = pathlib.Path(__file__).parent.parent / "results" / "gemini" / variante / conj / f"{doc_id}.json"
    if c.exists(): return json.loads(c.read_text())
    r = chamar(prompt); c.parent.mkdir(parents=True, exist_ok=True); c.write_text(json.dumps(r, ensure_ascii=False, indent=1))
    return r

def _json(txt):
    try: return json.loads(txt)
    except Exception:
        m = re.search(r"\{.*\}", txt or "", re.S)
        try: return json.loads(m.group(0)) if m else None
        except Exception: return None

def extrair_gemini_e2e(texto, doc_id, conj):
    """Retorna (extração para métricas, Bundle gerado pelo LLM como está, meta da chamada)."""
    r = _cache("e2e", conj, doc_id, PROMPT_E2E + texto)
    b = _json(r["texto"]) or {}
    obs = []
    for e in b.get("entry", []) if isinstance(b, dict) else []:
        res = e.get("resource", {}) if isinstance(e, dict) else {}
        if res.get("resourceType") != "Observation": continue
        cods = [c for c in res.get("code", {}).get("coding", []) if "loinc" in str(c.get("system", ""))]
        vq = res.get("valueQuantity", {}) or {}
        rr = (res.get("referenceRange") or [{}])[0]
        g = lambda k: (rr.get(k) or {}).get("value")
        obs.append({"loinc": cods[0].get("code") if cods else None, "display": cods[0].get("display") if cods else None,
                    "valor": vq.get("value"), "unidade": vq.get("code") or vq.get("unit"),
                    "ref_low": g("low"), "ref_high": g("high"), "texto_exame": res.get("code", {}).get("text")})
    return {**cabecalho(texto), "observacoes": obs}, b, r

def extrair_gemini_ent(texto, doc_id, conj):
    r = _cache("ent", conj, doc_id, PROMPT_ENT + texto)
    j = _json(r["texto"]) or {}
    obs = []
    for e in j.get("exames", []) if isinstance(j, dict) else []:
        if not isinstance(e, dict) or not e.get("exame") or e.get("valor") in (None, ""): continue
        s = lambda k: None if e.get(k) is None else str(e.get(k))
        obs.append(montar_obs(ligar_loinc(s("exame")), s("valor"), s("unidade"), s("faixa"), s("exame")))
    return {**cabecalho(texto), "observacoes": dedup(obs)}, r
