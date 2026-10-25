"""(c) Tabela de erros por rótulo NÃO visto: para cada rótulo (normalizado: sem acento/caixa) e cada método,
acertos da observação completa / ocorrências no gabarito e quantas vezes o código LOINC ficou certo (obs. prevista
pareada pelo valor). Também conta os cortes de prefixo "Dosagem de X": o trecho de exame previsto (pareado pelo valor)
perdeu o prefixo e virou só "X".
Uso: python erros_nao_vistos.py <conj>  ->  results/erros_nao_vistos_<conj>.csv, results/erros_nao_vistos_resumo_<conj>.csv"""
import json, sys, csv, pathlib
from collections import defaultdict
from pipeline import norm
from avaliar import METODOS, docs, r4, RES

def tupla(o): return (o.get("loinc"), r4(o.get("valor")), o.get("unidade"), r4(o.get("ref_low")), r4(o.get("ref_high")))

def familia(r):
    n = norm(r)
    if n.startswith("dosagem de"): return "prefixo 'Dosagem de'"
    if len(n.replace(" ", "")) <= 4: return "sigla"
    return "sinônimo/descritivo"

def main(conj):
    gabs = {p.stem: json.loads(p.with_suffix(".json").read_text(encoding="utf-8")) for p in docs(conj)}
    ms = [m for m in METODOS if (RES / "pred" / f"{m}_{conj}.json").exists()]
    P = {m: json.loads((RES / "pred" / f"{m}_{conj}.json").read_text(encoding="utf-8")) for m in ms}
    T = defaultdict(lambda: {"n": 0, "loinc": None, "ex": None, **{m: [0, 0] for m in ms}})
    corte = {m: [0, 0, 0] for m in ms}  # [rotulos 'Dosagem de' com par por valor, trecho sem prefixo, trecho com prefixo]
    for i, g in gabs.items():
        for o in g["observacoes"]:
            if o.get("rotulo_visto", True): continue
            k = norm(o["rotulo"]); t = T[k]; t["n"] += 1; t["loinc"] = o["loinc"]; t["ex"] = t["ex"] or o["rotulo"]
            for m in ms:
                pobs = P[m][i]["observacoes"]
                t[m][0] += tupla(o) in {tupla(p) for p in pobs}
                cand = [p for p in pobs if r4(p.get("valor")) == r4(o["valor"])]
                if len(cand) == 1:
                    t[m][1] += cand[0].get("loinc") == o["loinc"]
                    if k.startswith("dosagem de") and cand[0].get("texto_exame"):
                        te = norm(cand[0]["texto_exame"]); corte[m][0] += 1
                        corte[m][1] += not te.startswith("dosagem"); corte[m][2] += te.startswith("dosagem")
    L = [["rotulo", "familia", "loinc", "ocorrencias", *[f"{m}_{c}" for m in ms for c in ("obs_completa", "loinc_certo")], "zero_em_todos"]]
    for k, t in sorted(T.items(), key=lambda x: (-x[1]["n"], x[0])):
        zero = all(t[m][0] == 0 and t[m][1] == 0 for m in ms)
        L.append([t["ex"], familia(k), t["loinc"], t["n"], *[x for m in ms for x in t[m]], int(zero)])
    with open(RES / f"erros_nao_vistos_{conj}.csv", "w", newline="", encoding="utf-8") as fh: csv.writer(fh).writerows(L)
    R = [["familia", "rotulos", "ocorrencias", *[f"{m}_recall_obs_completa" for m in ms], *[f"{m}_loinc_certo" for m in ms], "rotulos_zero_em_todos"]]
    for fam in ("prefixo 'Dosagem de'", "sigla", "sinônimo/descritivo"):
        ts = [t for k, t in T.items() if familia(k) == fam]; n = sum(t["n"] for t in ts)
        R.append([fam, len(ts), n, *[f"{sum(t[m][0] for t in ts)/n:.3f}" for m in ms], *[f"{sum(t[m][1] for t in ts)/n:.3f}" for m in ms],
                  sum(all(t[m][0] == 0 and t[m][1] == 0 for m in ms) for t in ts)])
    for m in ms: R.append([f"corte_prefixo_{m}", "", corte[m][0], corte[m][1], corte[m][2]] + [""] * (len(R[0]) - 5))
    with open(RES / f"erros_nao_vistos_resumo_{conj}.csv", "w", newline="", encoding="utf-8") as fh: csv.writer(fh).writerows(R)
    for l in R: print(*l)
    print("zero em todos os métodos:", [l[0] for l in L[1:] if l[-1]])

if __name__ == "__main__":
    main(sys.argv[1])
