"""Método (a): GLiNER híbrido + LLM como RESERVA da ligação LOINC.
Só para exames extraídos pelo híbrido cujo rótulo NÃO casa no dicionário (ligar_loinc -> None), o Gemini (mesmo modelo
do e2e, temperatura 0) escolhe UM código entre os 20 do catálogo do projeto (src/exames.py) ou "nenhum", com saída JSON
restrita por esquema (enum). O display e a unidade UCUM vêm do catálogo e a montagem FHIR continua determinística
(pipeline.para_fhir). O LLM recebe só o rótulo impresso (como o dicionário), sem o laudo.
Cache por conjunto e rótulo normalizado em results/gemini/link/<conjunto>/<sha1>.json (sem chave de API)."""
import json, hashlib, pathlib
from exames import EXAMES, POR_LOINC
from pipeline import norm

CATALOGO = "\n".join(f"- {loinc} | {nome} | sinônimos: {', '.join(sin)} | {disp}" for nome, sin, loinc, disp, *_ in EXAMES)
CODIGOS = [e[2] for e in EXAMES]
PROMPT_LINK = """Você recebe o nome de um exame como foi impresso num laudo laboratorial brasileiro (pode ter erros de OCR,
abreviações ou sinônimos). Escolha o código LOINC do catálogo abaixo que corresponde a esse
exame. Se nenhum corresponder (por exemplo, não é um exame, é um campo administrativo ou um exame fora do catálogo),
responda "nenhum". Use SOMENTE códigos do catálogo.

CATÁLOGO (código | nome | sinônimos | nome LOINC):
""" + CATALOGO + """

Responda SOMENTE com JSON: {"loinc": "<código do catálogo ou nenhum>"}

NOME IMPRESSO: """
ESQUEMA = {"type": "object", "properties": {"loinc": {"type": "string", "enum": CODIGOS + ["nenhum"]}}, "required": ["loinc"]}
RES = pathlib.Path(__file__).parent.parent / "results" / "gemini" / "link"
CHAMADAS_API = [0]  # requisições lógicas feitas nesta execução (cache miss)

def ligar_llm(rotulo, conj):
    """-> ((loinc, display, ucum) ou None, registro da chamada). Rótulos iguais após norm() reaproveitam o cache."""
    from extrator_gemini import chamar, MODELO
    chave = norm(rotulo)
    c = RES / conj / (hashlib.sha1(chave.encode("utf-8")).hexdigest()[:16] + ".json")
    if c.exists():
        r = json.loads(c.read_text(encoding="utf-8"))
    else:
        r = chamar(PROMPT_LINK + rotulo, schema=ESQUEMA); r["rotulo"] = rotulo; r["rotulo_norm"] = chave
        c.parent.mkdir(parents=True, exist_ok=True); c.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
        CHAMADAS_API[0] += 1
    try: cod = json.loads(r["texto"]).get("loinc")
    except Exception: cod = None
    r["loinc_escolhido"] = cod
    if cod in POR_LOINC:
        e = POR_LOINC[cod]; return (e[2], e[3], e[4]), r
    return None, r
