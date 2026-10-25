"""(b) Sensibilidade da validade do Gemini ponta a ponta a pós-processamento determinístico (SEM chamar a API).
Etapas cumulativas sobre os Bundles gerados pelo LLM (results/fhir/gemini_e2e/<conj>/):
  pp_display_uuid : display LOINC trocado pelo do catálogo (código fora do catálogo => display removido, pois é opcional)
                    e fullUrl/referências fora do formato urn:uuid trocados por UUIDs válidos (uuid5 determinístico).
  pp_ucum         : o anterior + código UCUM da unidade normalizado pela mesma tabela do pipeline (só quando não exige
                    conversão do valor).
Uso: python sensibilidade_e2e.py preparar <conj>   (grava results/fhir/gemini_e2e_pp_*/<conj>/)
     python validar.py gemini_e2e_pp_display_uuid <conj>; python validar.py gemini_e2e_pp_ucum <conj>
     python sensibilidade_e2e.py resumo <conj>     (results/sensibilidade_e2e_<conj>.csv)"""
import json, sys, re, uuid, copy, pathlib, csv, random
from exames import POR_LOINC
from pipeline import unidade_ucum

BASE = pathlib.Path(__file__).parent.parent; RES = BASE / "results"
DISPLAY = {k: v[3] for k, v in POR_LOINC.items()}; DISPLAY["11502-2"] = "Laboratory report"
RE_UUID = re.compile(r"^urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
ETAPAS = ["gemini_e2e", "gemini_e2e_pp_display_uuid", "gemini_e2e_pp_ucum"]

def _andar(x, f):
    if isinstance(x, dict):
        f(x)
        for v in x.values(): _andar(v, f)
    elif isinstance(x, list):
        for v in x: _andar(v, f)

def corrigir_display(b):
    def f(d):
        if "loinc" in str(d.get("system", "")) and "code" in d:
            if d["code"] in DISPLAY: d["display"] = DISPLAY[d["code"]]
            else: d.pop("display", None)
    _andar(b, f); return b

def corrigir_uuid(b, doc):
    mapa = {}
    for k, e in enumerate(b.get("entry", []) if isinstance(b, dict) else []):
        fu = e.get("fullUrl") if isinstance(e, dict) else None
        if fu and not RE_UUID.match(fu):
            mapa[fu] = "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, f"ner-fhir/pp/{doc}/{k}"))
            e["fullUrl"] = mapa[fu]
            r = e.get("resource")
            if isinstance(r, dict) and "id" in r:
                velho = f"{r.get('resourceType')}/{r['id']}"; r["id"] = mapa[fu][9:]; mapa[velho] = mapa[fu]
    def f(d):
        if isinstance(d.get("reference"), str) and d["reference"] in mapa: d["reference"] = mapa[d["reference"]]
    _andar(b, f); return b

def corrigir_ucum(b):
    def f(d):
        if "unitsofmeasure" in str(d.get("system", "")) and isinstance(d.get("code") or d.get("unit"), str):
            u = unidade_ucum(d.get("code") or d.get("unit")) or unidade_ucum(d.get("unit") or "")
            if u and u[1] == 1: d["code"] = d["unit"] = u[0]
    _andar(b, f); return b

def preparar(conj):
    src = RES / "fhir" / "gemini_e2e" / conj
    for nome in ETAPAS[1:]: (RES / "fhir" / nome / conj).mkdir(parents=True, exist_ok=True)
    for f in sorted(src.glob("*.json")):
        b = json.loads(f.read_text(encoding="utf-8"))
        b1 = corrigir_uuid(corrigir_display(copy.deepcopy(b)), f.stem)
        b2 = corrigir_ucum(copy.deepcopy(b1))
        for nome, x in zip(ETAPAS[1:], (b1, b2)):
            (RES / "fhir" / nome / conj / f.name).write_text(json.dumps(x, ensure_ascii=False, indent=1), encoding="utf-8")

def categorias(oo_file):
    """Categorias de erro por Bundle a partir dos OperationOutcomes do validador."""
    b = json.loads(oo_file.read_text(encoding="utf-8"))
    rs = [e["resource"] for e in b.get("entry", [])] if b.get("resourceType") == "Bundle" else [b]
    out = {}
    for r in rs:
        f = next((x["valueString"] for x in r.get("extension", []) if x["url"].endswith("operationoutcome-file")), "?")
        cats = set()
        for i in r.get("issue", []):
            if i["severity"] not in ("error", "fatal"): continue
            t = i.get("details", {}).get("text", i.get("diagnostics", ""))
            if "Wrong Display Name" in t: cats.add("display")
            elif "UUIDs must be valid" in t: cats.add("uuid")
            elif "unitsofmeasure" in t: cats.add("ucum")
            elif "Unknown code" in t and "loinc" in t: cats.add("loinc_inexistente")
            else: cats.add("outros")
        out[pathlib.Path(f).stem] = cats
    return out

def resumo(conj):
    from avaliar import por_doc, soma, f1, docs, B, SEED, I_LO, I_HI
    from extrator_gemini import obs_de_bundle
    gabs = {p.stem: json.loads(p.with_suffix(".json").read_text(encoding="utf-8")) for p in docs(conj)}; ids = sorted(gabs)
    L = [["etapa", "validos", "total", "pct_validos", "ic95_inf", "ic95_sup", "bundles_display", "bundles_ucum",
          "bundles_loinc_inexistente", "bundles_uuid", "bundles_outros", "f1_obs_completa", "acuracia_loinc"]]
    for nome in ETAPAS:
        cats = categorias(RES / "validacao" / f"{nome}_{conj}_operationoutcomes.json")
        vv = [not cats.get(i, {"sem_validacao"}) for i in ids]
        rng = random.Random(SEED); bs = sorted(sum(rng.choice(vv) for _ in vv) / len(vv) for _ in range(B))
        cont = {c: sum(c in cats.get(i, set()) for i in ids) for c in ("display", "ucum", "loinc_inexistente", "uuid", "outros")}
        preds = {i: {"observacoes": obs_de_bundle(json.loads((RES / "fhir" / nome / conj / f"{i}.json").read_text(encoding="utf-8")))} for i in ids}
        ds = [por_doc(gabs[i], preds[i], "gemini_e2e") for i in ids]
        acc = (lambda t: t[0] / t[1] if t[1] else 0)(soma(ds, "loinc"))
        L.append([nome, sum(vv), len(ids), f"{100*sum(vv)/len(ids):.1f}", f"{100*bs[I_LO]:.1f}", f"{100*bs[I_HI]:.1f}",
                  *cont.values(), f"{f1(soma(ds, 'completa'))[2]:.3f}", f"{acc:.3f}"])
    with open(RES / f"sensibilidade_e2e_{conj}.csv", "w", newline="", encoding="utf-8") as fh: csv.writer(fh).writerows(L)
    for l in L: print(*l)

if __name__ == "__main__":
    {"preparar": preparar, "resumo": resumo}[sys.argv[1]](sys.argv[2])
