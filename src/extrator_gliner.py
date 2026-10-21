"""Extrator GLiNER zero-shot (sem ajuste fino) + pós-processamento + ligação LOINC por dicionário de sinônimos.
Ajustes feitos SÓ no dev: rótulos em inglês ('analyte', ...), limiar 0,3 (GLiNER puro) e 0,1 (híbrido; varredura no dev: 0,1→F1 0,80; 0,2→0,76; 0,3→0,74), inferência por linha, e
pós-processamento que expande cada trecho até os espaços (o tokenizador do GLiNER parte '12,9' em '12' ',' '9')
e junta trechos vizinhos do mesmo tipo."""
import os, re
from pipeline import ligar_loinc, montar_obs, cabecalho, dedup, RE_FAIXA

MODELO = os.environ.get("GLINER_MODEL", "urchade/gliner_multi-v2.1")
ROTULOS = {"analyte": "exame", "measured value": "valor", "unit": "unidade", "reference values": "faixa"}
LIMIAR = float(os.environ.get("GLINER_LIMIAR", "0.3"))
LIMIAR_HIB = float(os.environ.get("GLINER_LIMIAR_HIB", "0.1"))
_m = None

def modelo():
    global _m
    if _m is None:
        from gliner import GLiNER
        _m = GLiNER.from_pretrained(MODELO); _m.eval()
    return _m

def _expande(l, s, e):
    while s > 0 and not l[s - 1].isspace(): s -= 1
    while e < len(l) and not l[e].isspace(): e += 1
    return s, e

def entidades_linha(l, preds):
    es = []
    for p in sorted(preds, key=lambda p: p["start"]):
        tipo = ROTULOS[p["label"]]
        s, e = (p["start"], p["end"]) if tipo == "exame" else _expande(l, p["start"], p["end"])
        if es and es[-1][2] == tipo and not l[es[-1][1]:s].strip(" .,:;"):
            es[-1] = (es[-1][0], max(e, es[-1][1]), tipo)
        elif es and s < es[-1][1]: continue
        else: es.append((s, e, tipo))
    out = []
    for s, e, tipo in es:
        if tipo == "faixa":
            m = RE_FAIXA.search(l, max(0, s - 6))
            if m and m.start() <= e: s, e = min(s, m.start()), max(e, m.end())
        out.append((tipo, l[s:e].strip(" .:;()")))
    return out

def extrair_gliner(texto):
    linhas = [l for l in texto.splitlines() if l.strip()]
    preds = modelo().inference(linhas, list(ROTULOS), threshold=LIMIAR, flat_ner=True, batch_size=16)
    obs, atual = [], None
    def fecha():
        if atual and atual.get("valor"):
            obs.append(montar_obs(atual["lig"], atual["valor"], atual.get("unidade"), atual.get("faixa"), atual["exame"]))
    for l, ps in zip(linhas, preds):
        for tipo, txt in entidades_linha(l, ps):
            if tipo == "exame":
                fecha(); atual = {"lig": ligar_loinc(txt), "exame": txt}
            elif atual is not None and tipo not in atual:
                if tipo == "valor" and not re.search(r"\d", txt): continue
                atual[tipo] = txt
    fecha()
    return {**cabecalho(texto), "observacoes": dedup(obs)}

# ---------- variante híbrida: GLiNER só para o NOME do exame + regras posicionais para valor/unidade/faixa ----------
from pipeline import RE_LINHA, RE_RES, RE_REF

def extrair_gliner_hib(texto):
    """No dev, o GLiNER acerta nomes de exames mas erra tipos de números/unidades; aqui ele só marca o 'analyte'
    e o resto da linha (ou do bloco 'Resultado:'/'Valor de referência:') é lido com as mesmas regras da regex."""
    linhas = [l for l in texto.splitlines() if l.strip()]
    preds = modelo().inference(linhas, ["analyte"], threshold=LIMIAR_HIB, flat_ner=True, batch_size=16)
    obs, atual = [], None
    for l, ps in zip(linhas, preds):
        m = RE_RES.search(l)
        if m and atual: atual["v"], atual["u"] = m.group("v"), m.group("u"); continue
        m = RE_REF.search(l)
        if m and atual and atual.get("v"):
            obs.append(montar_obs(atual["lig"], atual["v"], atual["u"], m.group("f"), atual["r"])); atual = None; continue
        ex = [p for p in ps if p["start"] < 3] or ps[:1]
        if not ex: continue
        p = ex[0]; rot = l[p["start"]:p["end"]]
        resto = re.sub(r"^[^\d]*?(?=\d)", "", l[p["end"]:]); resto = re.sub(r"/\s+", "/", resto)
        mm = RE_LINHA.match(resto.strip())
        if mm: obs.append(montar_obs(ligar_loinc(rot), mm.group("v"), mm.group("u"), mm.group("f"), rot)); atual = None
        elif not re.search(r"\d", l): atual = {"lig": ligar_loinc(rot), "r": rot}
    return {**cabecalho(texto), "observacoes": dedup(obs)}
