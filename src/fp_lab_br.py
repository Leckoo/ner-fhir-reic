"""Decomposição dos falsos positivos (observação completa) no conjunto exploratório lab_br, por origem da linha:
cabeçalho/rodapé administrativo, seções de texto livre, diferencial do leucograma (distrator), linha de resultado do
gabarito (erro de valor/unidade/faixa/ligação) e outros (ruído de OCR etc.). A linha de origem é a primeira linha do texto
extraído que contém o trecho de exame e o valor previstos (ou só o valor, se não houver trecho).
Uso: python fp_lab_br.py [conj]  ->  results/fp_origem_<conj>.csv"""
import json, sys, re, csv
from collections import Counter
from pipeline import norm
from avaliar import METODOS, docs, r4, RES
from erros_nao_vistos import tupla
from gerar_lab_br import DIFERENCIAL

ADM = re.compile(r"^(NOME|CONV[EÊ]NIO|DR\.\(A\)|CRM|DATA|EXAME|IDADE|DN|ID)\b|CIDADE EXEMPLO|DIRETOR T[EÉ]CNICO|LABORAT[OÓ]RIO CL[IÍ]NICO|^DR\(A\)|RQE|\b1 DE 1\b", re.I)
LIVRE = re.compile(r"^(Material|M[ée]todo|Dados cl[íi]nicos|Observa[çc][õo]es|Nota|Valores de refer[êe]ncia)\s*:", re.I)
DIF = tuple(norm(n) for n, _, _ in DIFERENCIAL)
CATS = ["cabecalho_rodape", "texto_livre", "diferencial_leucograma", "linha_de_resultado", "outros"]

def categoria(linha, rotulos):
    if LIVRE.search(linha.strip()): return "texto_livre"
    if ADM.search(linha.strip()): return "cabecalho_rodape"
    n = norm(linha)
    if n.startswith(DIF): return "diferencial_leucograma"
    if any(r and r in n for r in rotulos): return "linha_de_resultado"
    return "outros"

def main(conj="adicional_lab_br"):
    gabs = {p.stem: json.loads(p.with_suffix(".json").read_text(encoding="utf-8")) for p in docs(conj)}
    L = [["metodo", "fp_total", *CATS]]
    for m in METODOS:
        pf = RES / "pred" / f"{m}_{conj}.json"
        if not pf.exists(): continue
        P = json.loads(pf.read_text(encoding="utf-8")); c = Counter()
        for i, g in gabs.items():
            linhas = (RES / "texto" / conj / f"{i}.txt").read_text(encoding="utf-8").splitlines()
            rot = {norm(o["rotulo"]) for o in g["observacoes"]}
            resta = Counter(tupla(o) for o in g["observacoes"])
            for o in P[i]["observacoes"]:
                t = tupla(o)
                if resta[t] > 0: resta[t] -= 1; continue
                te, tv = o.get("texto_exame") or "", o.get("texto_valor") or str(o.get("valor") or "")
                ln = next((l for l in linhas if te and te in l and tv in l), None) or next((l for l in linhas if te and te in l), None) \
                     or next((l for l in linhas if tv and tv in l), "")
                c[categoria(ln, rot)] += 1
        L.append([m, sum(c.values()), *[c[k] for k in CATS]])
    with open(RES / f"fp_origem_{conj}.csv", "w", newline="", encoding="utf-8") as fh: csv.writer(fh).writerows(L)
    for l in L: print(*l)

if __name__ == "__main__":
    main(*sys.argv[1:])
