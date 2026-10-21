"""PDF -> texto (pdfplumber; OCR Tesseract se o PDF for só imagem) -> extração -> FHIR R5
(Bundle collection com Patient, Observation [LOINC, valueQuantity UCUM, referenceRange] e DiagnosticReport).
Este módulo traz o texto, a normalização compartilhada (números, unidades, faixas, ligação LOINC),
o baseline regex+dicionário e a montagem do Bundle."""
import re, unicodedata, uuid, difflib, pathlib, shutil
import pdfplumber
from exames import EXAMES

def norm(s):
    s = "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s).strip()

DIC = {}  # rótulo normalizado -> (loinc, display, ucum)
for nome, sin, loinc, disp, un, *_ in EXAMES:
    for t in [nome] + sin: DIC[norm(t)] = (loinc, disp, un)
CHAVES = sorted(DIC, key=len, reverse=True)

def ligar_loinc(rotulo, fuzzy=True):
    """Ligação ao LOINC por dicionário de nomes/sinônimos (exato; depois aproximado, corte 0,85)."""
    r = norm(re.sub(r"[.:\s]+$", "", rotulo))
    if r in DIC: return DIC[r]
    if fuzzy:
        m = difflib.get_close_matches(r, CHAVES, n=1, cutoff=0.85)
        if m: return DIC[m[0]]
    return None

# ---------- unidades ----------
def unidade_ucum(u):
    """Texto da unidade -> (UCUM canônico, divisor do valor) ou None."""
    if not u: return None
    k = norm(u).replace(" ", "").replace("µ", "u").replace("μ", "u").replace("³", "3").replace("⁶", "6")
    k = k.rstrip(").,;")
    # grafias corrompidas por OCR observadas no dev
    k = re.sub(r"mm[º°o]$", "mm3", k)
    k = k.replace("meqg", "meq").replace("meg/", "meq/").replace("hui/", "uui/").replace("pui/", "uui/")
    tab = {"g/dl": ("g/dL", 1), "%": ("%", 1), "fl": ("fL", 1), "pg": ("pg", 1), "mg/dl": ("mg/dL", 1),
           "mmol/l": ("mmol/L", 1), "meq/l": ("mmol/L", 1), "u/l": ("U/L", 1),
           "uui/ml": ("u[IU]/mL", 1), "mui/l": ("u[IU]/mL", 1), "u[iu]/ml": ("u[IU]/mL", 1),
           "mil/mm3": ("10*3/uL", 1), "/mm3": ("10*3/uL", 1000), "milhoes/mm3": ("10*6/uL", 1),
           "10*3/ul": ("10*3/uL", 1), "10*6/ul": ("10*6/uL", 1), "x10^3/ul": ("10*3/uL", 1), "x10^6/ul": ("10*6/uL", 1),
           "x103/ul": ("10*3/uL", 1), "x106/ul": ("10*6/uL", 1)}
    if k in tab: return tab[k]
    if re.fullmatch(r"x?10[\^*]?3/ul", k): return ("10*3/uL", 1)
    if re.fullmatch(r"x?10[\^*]?6/ul", k): return ("10*6/uL", 1)
    return None

def numero(s, milhar=False):
    s = s.strip().replace(" ", "")
    if milhar: s = s.replace(".", "").replace(",", ".")
    else: s = s.replace(",", ".")
    try: return float(s)
    except ValueError: return None

NUM = r"\d+(?:[.,]\d+)*"
RE_FAIXA = re.compile(rf"(?:(?P<lo>{NUM})\s*(?:a|-|–|—)\s*(?P<hi>{NUM}))|(?:(?:at[eé]|<|<=|≤|inferior a)\s*(?P<ate>{NUM}))", re.I)

def faixa(texto, milhar=False, div=1):
    """Texto da faixa -> (low, high) na unidade canônica; None se não reconhecida."""
    if not texto: return None
    m = RE_FAIXA.search(texto)
    if not m: return None
    if m.group("ate"):
        hi = numero(m.group("ate"), milhar); return (None, hi / div) if hi is not None else None
    lo, hi = numero(m.group("lo"), milhar), numero(m.group("hi"), milhar)
    return (lo / div, hi / div) if lo is not None and hi is not None else None

def montar_obs(lig, vtxt, utxt, ftxt, etxt=None):
    """Normaliza valor/unidade/faixa impressos para a forma canônica (UCUM). lig=None => exame sem LOINC."""
    loinc, disp, un_cat = lig or (None, None, None)
    uc = unidade_ucum(utxt)
    ucum, div = uc if uc else (None, 1)
    milhar = div == 1000
    v = numero(vtxt, milhar) if vtxt else None
    if v is not None: v = round(v / div, 6)
    fx = faixa(ftxt, milhar, div)
    return {"loinc": loinc, "display": disp, "valor": v, "unidade": ucum,
            "ref_low": None if not fx or fx[0] is None else round(fx[0], 6),
            "ref_high": None if not fx or fx[1] is None else round(fx[1], 6),
            "texto_exame": etxt, "texto_valor": vtxt, "texto_unidade": utxt, "texto_faixa": ftxt}

# ---------- texto ----------
def extrair_texto(pdf, cache_dir=None):
    pdf = pathlib.Path(pdf)
    if cache_dir:
        c = pathlib.Path(cache_dir) / (pdf.stem + ".txt")
        if c.exists(): return c.read_text()
    with pdfplumber.open(pdf) as p:
        txt = "\n".join(pg.extract_text() or "" for pg in p.pages)
    if len(txt.strip()) < 20:  # PDF só imagem (escaneado) -> OCR
        txt = ocr(pdf)
    if cache_dir:
        pathlib.Path(cache_dir).mkdir(parents=True, exist_ok=True); c.write_text(txt)
    return txt

def ocr(pdf):
    if not shutil.which("tesseract"): raise RuntimeError("tesseract não instalado: necessário para PDFs escaneados")
    import pymupdf, pytesseract
    from PIL import Image
    doc = pymupdf.open(pdf); out = []
    for pg in doc:
        pix = pg.get_pixmap(dpi=300, colorspace=pymupdf.csGRAY)
        img = Image.frombytes("L", (pix.width, pix.height), pix.samples)
        out.append(pytesseract.image_to_string(img, lang="por", config="--psm 6"))
    return "\n".join(out)

def cabecalho(texto):
    pac = re.search(r"paciente\s*:\s*(.+?)(?:\s{2,}|\s+nascimento|\s*$)", texto, re.I | re.M)
    dat = re.search(r"\bdata\s*:\s*(\d{4}-\d{2}-\d{2})", texto, re.I)
    nas = re.search(r"nascimento\s*:\s*(\d{4}-\d{2}-\d{2})", texto, re.I)
    return {"paciente": pac.group(1).strip() if pac else None, "data": dat.group(1) if dat else None,
            "nascimento": nas.group(1) if nas else None}

# ---------- baseline regex + dicionário (regras ajustadas só no dev) ----------
UNID = r"(?P<u>[^\s(]+)"
RE_LINHA = re.compile(rf"^(?P<v>{NUM})\s+{UNID}\s*\(?\s*(?:VR\s*:)?\s*(?P<f>.*?)\)?\s*$", re.I)
RE_RES = re.compile(rf"resultado\s*:\s*(?P<v>{NUM})\s+(?P<u>.+?)\s*$", re.I)
RE_REF = re.compile(r"valor(?:es)? de refer[eê]ncia\s*:\s*(?P<f>.+)$", re.I)

RE_GEN = re.compile(rf"^(?P<r>[^\d]*?[^\d\s.:])[\s.:]+(?P<resto>{NUM}\s.*)$")

def achar_rotulo(linha):
    """Prefixo da linha que está no dicionário -> ((loinc, display, ucum), rótulo, resto)."""
    l = linha.strip(); n = norm(l)
    for k in CHAVES:
        if n.startswith(k) and (len(n) == len(k) or not n[len(k)].isalnum()):
            return DIC[k], l[:len(k)], l[len(k):]
    return None, None, None

def extrair_regex(texto):
    obs, atual, titulo = [], None, None
    for linha in texto.splitlines():
        l = linha.strip()
        if not l: continue
        m = RE_RES.search(l)
        if m:
            if atual is None and titulo:  # título de bloco fora do dicionário: ligação aproximada
                atual = {"lig": ligar_loinc(titulo), "r": titulo}
            if atual: atual["v"], atual["u"] = m.group("v"), m.group("u")
            continue
        m = RE_REF.search(l)
        if m and atual:
            obs.append(montar_obs(atual["lig"], atual.get("v"), atual.get("u"), m.group("f"), atual["r"])); atual = None; continue
        lig, rot, resto = achar_rotulo(l)
        if not lig:  # linha genérica "rótulo valor unidade faixa" com rótulo fora do dicionário
            g = RE_GEN.match(l)
            if g and not re.search(r"(?i)cnes|data|nascimento|liberado|p[aá]g|crbm|crf|t[eé]cnico|paciente|solicitante", g.group("r")):
                lig, rot, resto = ligar_loinc(g.group("r")), g.group("r"), " " + g.group("resto")
            else:
                if not re.search(r"\d|:", l): titulo, atual = l, None
                continue
        resto = re.sub(r"^[^\d]*?(?=\d)", "", resto) if re.match(r"^[\s.:]", resto or "") else resto
        resto = re.sub(r"/\s+", "/", resto)
        m = RE_LINHA.match(resto)
        if m:
            obs.append(montar_obs(lig, m.group("v"), m.group("u"), m.group("f"), rot)); atual = None
        elif not resto.strip():
            atual = {"lig": lig, "r": rot}  # título de bloco (layout 'blocos')
    return {**cabecalho(texto), "observacoes": dedup(obs)}

def dedup(obs):
    vistos, out = set(), []
    for o in obs:
        k = o["loinc"] or ("txt", o.get("texto_exame"))
        if k not in vistos: vistos.add(k); out.append(o)
    return out

# ---------- FHIR R5 ----------
def _uid(*p): return "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, "ner-fhir/" + "/".join(map(str, p))))

def _q(v, ucum):
    q = {"value": v}
    if ucum: q.update({"unit": ucum, "system": "http://unitsofmeasure.org", "code": ucum})
    return q

def para_fhir(ext, doc_id):
    pid = _uid(doc_id, "patient")
    pat = {"resourceType": "Patient"}
    if ext.get("paciente"): pat["name"] = [{"text": ext["paciente"]}]
    if ext.get("nascimento"): pat["birthDate"] = ext["nascimento"]
    entries = [{"fullUrl": pid, "resource": pat}]
    refs = []
    for k, o in enumerate(ext["observacoes"]):
        oid = _uid(doc_id, "obs", k); refs.append({"reference": oid})
        r = {"resourceType": "Observation", "status": "final",
             "category": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/observation-category", "code": "laboratory"}]}],
             "code": ({"coding": [{"system": "http://loinc.org", "code": o["loinc"], "display": o["display"]}]}
                      if o.get("loinc") else {"text": o.get("texto_exame") or "exame"}),
             "subject": {"reference": pid}}
        if ext.get("data"): r["effectiveDateTime"] = ext["data"]
        if o.get("valor") is not None: r["valueQuantity"] = _q(o["valor"], o.get("unidade"))
        rr = {}
        if o.get("ref_low") is not None: rr["low"] = _q(o["ref_low"], o.get("unidade"))
        if o.get("ref_high") is not None: rr["high"] = _q(o["ref_high"], o.get("unidade"))
        if rr: r["referenceRange"] = [rr]
        entries.append({"fullUrl": oid, "resource": r})
    dr = {"resourceType": "DiagnosticReport", "status": "final",
          "category": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/v2-0074", "code": "LAB"}]}],
          "code": {"coding": [{"system": "http://loinc.org", "code": "11502-2", "display": "Laboratory report"}]},
          "subject": {"reference": pid}}
    if ext.get("data"): dr["effectiveDateTime"] = ext["data"]
    if refs: dr["result"] = refs
    entries.append({"fullUrl": _uid(doc_id, "dr"), "resource": dr})
    return {"resourceType": "Bundle", "type": "collection", "entry": entries}
