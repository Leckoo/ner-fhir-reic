"""AJUSTE PÓS-HOC, separado do protocolo: leitura do cabeçalho em grade do lab_br (NOME:/DN:/DATA:).
Motivo: no lab_br o cabeçalho não usa "Paciente:/Nascimento:/Data: AAAA-MM-DD", então cabecalho() devolve tudo None,
o Patient sai vazio ({"resourceType": "Patient"}) e o validador HL7 rejeita o Bundle (bdl-3a/bdl-5). 0/50 válidos.
O ajuste NÃO reextrai nada: lê as predições já gravadas (results/pred/<m>_<conj>.json, mesmas observações), completa só
paciente/nascimento/data com pipeline.cabecalho_grade() e remonta o Bundle em results/fhir/<m>_cabgrade/<conj>/.
Como as métricas de extração não usam o cabeçalho, F1/acurácia LOINC/recall ficam idênticos; muda só a validade.
  python ajuste_cabecalho_grade.py montar <conj> [metodos...]
  python validar.py <m>_cabgrade <conj>
  python ajuste_cabecalho_grade.py resumo <conj> [metodos...]"""
import json, sys, csv, random, pathlib
from pipeline import para_fhir, completar_cabecalho
from avaliar import RES, BASE, B, SEED, I_LO, I_HI, validacao, docs

METODOS = ["regex", "gliner_hib", "gliner_llm"]

def montar(conj, metodos):
    for m in metodos:
        preds = json.loads((RES / "pred" / f"{m}_{conj}.json").read_text(encoding="utf-8"))
        out = RES / "fhir" / f"{m}_cabgrade" / conj; out.mkdir(parents=True, exist_ok=True); n = 0
        for i, p in sorted(preds.items()):
            texto = (RES / "texto" / conj / f"{i}.txt").read_text(encoding="utf-8")
            ext = completar_cabecalho({k: p.get(k) for k in ("paciente", "data", "nascimento")} | {"observacoes": p["observacoes"]}, texto)
            assert ext["observacoes"] is p["observacoes"]
            antes = json.loads((RES / "fhir" / m / conj / f"{i}.json").read_text(encoding="utf-8"))
            b = para_fhir(ext, i)
            # mesmas Observations/DiagnosticReport a menos de effectiveDateTime (data do laudo) e do Patient
            limpa = lambda bb: [{k: v for k, v in e["resource"].items() if k != "effectiveDateTime"} for e in bb["entry"][1:]]
            assert limpa(antes) == limpa(b), i
            (out / f"{i}.json").write_text(json.dumps(b, ensure_ascii=False, indent=1), encoding="utf-8"); n += 1
        print(f"{m} {conj}: {n} Bundles remontados em {out.relative_to(BASE)}")

def ic_prop(vv):
    rng = random.Random(SEED); bs = sorted(sum(rng.choice(vv) for _ in vv) / len(vv) for _ in range(B))
    return bs[I_LO], bs[I_HI]

def resumo(conj, metodos):
    ids = [p.stem for p in docs(conj)]
    gabs = {i: json.loads((BASE / "data" / conj / f"{i}.json").read_text(encoding="utf-8")) for i in ids}
    L = []
    for m in metodos:
        a, d = validacao(m, conj), validacao(f"{m}_cabgrade", conj)
        va, vd = [a.get(i, False) for i in ids], [d.get(i, False) for i in ids]
        (alo, ahi), (dlo, dhi) = ic_prop(va), ic_prop(vd)
        # conferência a posteriori do cabeçalho lido (o gabarito NÃO foi usado para escrever o parser)
        ac = {k: 0 for k in ("paciente", "nascimento", "data")}
        for i in ids:
            t = (RES / "texto" / conj / f"{i}.txt").read_text(encoding="utf-8")
            e = completar_cabecalho({"paciente": None, "data": None, "nascimento": None, "observacoes": []}, t)
            for k in ac: ac[k] += e.get(k) == gabs[i][k]
        L.append([m, len(ids), sum(va), f"{100*sum(va)/len(ids):.1f}", f"{100*alo:.1f}", f"{100*ahi:.1f}",
                  sum(vd), f"{100*sum(vd)/len(ids):.1f}", f"{100*dlo:.1f}", f"{100*dhi:.1f}", ac["paciente"], ac["nascimento"], ac["data"]])
    f = RES / f"ajuste_cabecalho_grade_{conj}.csv"
    csv.writer(open(f, "w", newline="", encoding="utf-8")).writerows([["metodo", "docs", "validos_antes", "pct_antes", "ic95_inf", "ic95_sup",
        "validos_depois", "pct_depois", "ic95_inf", "ic95_sup", "nome_igual_gabarito", "nascimento_igual_gabarito", "data_igual_gabarito"]] + L)
    for l in L: print(*l)

if __name__ == "__main__":
    cmd, conj, ms = sys.argv[1], sys.argv[2], sys.argv[3:] or METODOS
    (montar if cmd == "montar" else resumo)(conj, ms)
