import sys, pathlib, json, hashlib, ast
RAIZ = pathlib.Path(__file__).parent.parent; sys.path.insert(0, str(RAIZ / "src"))
from pipeline import extrair_regex, para_fhir, unidade_ucum, faixa, DIC, norm, ligar_loinc

def test_linha_tabela():
    e = extrair_regex("Paciente: Ana Souza Nascimento: 1990-01-01\nData: 2026-01-02\nHb 13,5 g/dL 12,0 a 16,0")
    o = e["observacoes"][0]
    assert (o["loinc"], o["valor"], o["unidade"], o["ref_low"], o["ref_high"]) == ("718-7", 13.5, "g/dL", 12.0, 16.0)
    assert e["paciente"] == "Ana Souza" and e["data"] == "2026-01-02"

def test_legado_milhar_e_ate():
    e = extrair_regex("PLAQUETAS ...........: 250.000 /mm3   (VR: 150.000 - 450.000)\nTGO ......: 35 U/L (VR: ATE 40)")
    p, t = e["observacoes"]
    assert (p["valor"], p["unidade"], p["ref_low"], p["ref_high"]) == (250.0, "10*3/uL", 150.0, 450.0)
    assert (t["loinc"], t["ref_low"], t["ref_high"]) == ("1920-8", None, 40.0)

def test_blocos():
    e = extrair_regex("SÓDIO\nMaterial: Sangue   Método: Automatizado\nResultado: 140 mEq/L\nValor de referência: 136 – 145")
    o = e["observacoes"][0]; assert (o["loinc"], o["valor"], o["unidade"], o["ref_high"]) == ("2951-2", 140.0, "mmol/L", 145.0)

def test_unidades_faixas():
    assert unidade_ucum("x10³/µL") == ("10*3/uL", 1) and unidade_ucum("µUI/mL") == ("u[IU]/mL", 1)
    assert faixa("< 190") == (None, 190.0) and faixa("4.20 – 5.40") == (4.2, 5.4)

def test_bundle_r5():
    e = extrair_regex("Data: 2026-01-02\nGlicose 90 mg/dL 70 a 99")
    b = para_fhir(e, "t"); tipos = [x["resource"]["resourceType"] for x in b["entry"]]
    assert tipos == ["Patient", "Observation", "DiagnosticReport"]
    obs = b["entry"][1]["resource"]
    assert obs["referenceRange"][0]["low"]["code"] == "mg/dL" and obs["valueQuantity"]["system"] == "http://unitsofmeasure.org"
    assert "null" not in json.dumps(b)

def test_rotulos_ocultos_fora_do_dicionario():
    from rotulos_ocultos import OCULTOS
    for loinc, rs in OCULTOS.items():
        for r in rs: assert norm(r) not in DIC, r
    for f in ["pipeline.py", "extrator_gliner.py", "extrator_gemini.py", "ligacao_llm.py", "avaliar.py"]:
        assert "rotulos_ocultos" not in (RAIZ / "src" / f).read_text(encoding="utf-8")

def test_teste_congelado():
    d = RAIZ / "data" / "teste"
    for l in (d / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        h, nome = l.split(); assert hashlib.sha256((d / nome).read_bytes()).hexdigest() == h, nome

def test_lab_br_adicional():
    """5º layout (conjunto adicional): hash próprio confere, layout correto, sem nomes de instituições reais."""
    d = RAIZ / "data" / "adicional_lab_br"
    for l in (d / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        h, nome = l.split(); assert hashlib.sha256((d / nome).read_bytes()).hexdigest() == h, nome
    g = json.loads((d / "laudo_000.json").read_text(encoding="utf-8")); assert g["layout"] == "lab_br"
    src = (RAIZ / "src" / "gerar_lab_br.py").read_text(encoding="utf-8").lower()
    for proibido in ("hospital", "einstein", "fleury", "dasa", "pardini"):
        assert proibido not in src, proibido
    e = extrair_regex("Hemácias 4,47 milhões/mm³ 4,20 a 5,40 milhões/mm³")["observacoes"][0]
    assert (e["loinc"], e["valor"], e["ref_low"], e["ref_high"]) == ("789-8", 4.47, 4.2, 5.4)

def test_pos_processamento_e2e_display_uuid():
    from sensibilidade_e2e import corrigir_display, corrigir_uuid, RE_UUID
    b = {"resourceType": "Bundle", "entry": [
        {"fullUrl": "urn:uuid:obs-1", "resource": {"resourceType": "Observation", "id": "obs-1",
         "code": {"coding": [{"system": "http://loinc.org", "code": "718-7", "display": "Hemoglobina"}]},
         "subject": {"reference": "urn:uuid:pat-1"}}},
        {"fullUrl": "urn:uuid:pat-1", "resource": {"resourceType": "Patient", "id": "pat-1"}}]}
    b = corrigir_uuid(corrigir_display(b), "x")
    assert b["entry"][0]["resource"]["code"]["coding"][0]["display"] == "Hemoglobin [Mass/volume] in Blood"
    assert all(RE_UUID.match(e["fullUrl"]) for e in b["entry"])
    assert b["entry"][0]["resource"]["subject"]["reference"] == b["entry"][1]["fullUrl"]
