"""Roda os extratores e calcula as métricas.
  python avaliar.py rodar <metodo> <conjunto>    metodo: regex | gliner | gemini_ent | gemini_e2e
  python avaliar.py metricas <conjunto>          tabelas em results/ (+ IC 95% bootstrap por documento)"""
import json, sys, time, pathlib, csv, random, re
from collections import Counter
from pipeline import extrair_texto, extrair_regex, para_fhir, norm

BASE = pathlib.Path(__file__).parent.parent
RES = BASE / "results"
METODOS = ["regex", "gliner", "gliner_hib", "gemini_ent", "gemini_e2e"]
NOME = {"regex": "Regex + dicionário", "gliner": "GLiNER zero-shot", "gliner_hib": "GLiNER (exame) + regras", "gemini_ent": "Gemini (entidades) + ligação",
        "gemini_e2e": "Gemini FHIR direto"}
B, SEED = 1000, 12345

def docs(conj):
    return sorted((BASE / "data" / conj).glob("laudo_*.pdf"))

def rodar(metodo, conj):
    out_f = RES / "fhir" / metodo / conj; out_f.mkdir(parents=True, exist_ok=True)
    preds = {}
    for pdf in docs(conj):
        texto = extrair_texto(pdf, RES / "texto" / conj)
        meta = {"chamadas": 0, "tokens": 0}
        t0 = time.time()
        if metodo == "regex": ext = extrair_regex(texto); bundle = para_fhir(ext, pdf.stem)
        elif metodo == "gliner":
            from extrator_gliner import extrair_gliner
            ext = extrair_gliner(texto); bundle = para_fhir(ext, pdf.stem)
        elif metodo == "gliner_hib":
            from extrator_gliner import extrair_gliner_hib
            ext = extrair_gliner_hib(texto); bundle = para_fhir(ext, pdf.stem)
        elif metodo == "gemini_ent":
            from extrator_gemini import extrair_gemini_ent
            ext, r = extrair_gemini_ent(texto, pdf.stem, conj); bundle = para_fhir(ext, pdf.stem)
        elif metodo == "gemini_e2e":
            from extrator_gemini import extrair_gemini_e2e
            ext, bundle, r = extrair_gemini_e2e(texto, pdf.stem, conj)
        lat = time.time() - t0
        if metodo.startswith("gemini"):  # latência = da chamada registrada (cache não distorce)
            lat = r["latencia_s"] + (lat if lat < r["latencia_s"] else 0)
            meta = {"chamadas": r["tentativas"], "tokens": r.get("tokens_total") or 0, "modelo": r.get("modelo")}
        (out_f / f"{pdf.stem}.json").write_text(json.dumps(bundle, ensure_ascii=False, indent=1), encoding="utf-8")
        preds[pdf.stem] = {**ext, "latencia_s": lat, **meta}
        print(f"{metodo} {conj} {pdf.stem} obs={len(ext['observacoes'])} {lat:.2f}s", flush=True)
    (RES / "pred").mkdir(parents=True, exist_ok=True)
    (RES / "pred" / f"{metodo}_{conj}.json").write_text(json.dumps(preds, ensure_ascii=False, indent=1), encoding="utf-8")

# ---------- métricas ----------
def nt(s): return re.sub(r"[^0-9a-z%/*^]", "", norm(str(s))) if s not in (None, "") else None
def r4(x):
    try: return None if x is None else round(float(x), 4)
    except (TypeError, ValueError): return None

def chaves(obs, gold=False):
    c = {k: Counter() for k in ("exame", "valor", "unidade", "faixa", "completa", "s_exame", "s_valor", "s_unidade", "s_faixa")}
    for o in obs:
        l = o.get("loinc")
        c["exame"][l] += 1; c["valor"][(l, r4(o.get("valor")))] += 1; c["unidade"][(l, o.get("unidade"))] += 1
        c["faixa"][(l, r4(o.get("ref_low")), r4(o.get("ref_high")))] += 1
        c["completa"][(l, r4(o.get("valor")), o.get("unidade"), r4(o.get("ref_low")), r4(o.get("ref_high")))] += 1
        for k, campo in (("s_exame", "texto_exame"), ("s_valor", "texto_valor"), ("s_unidade", "texto_unidade"), ("s_faixa", "texto_faixa")):
            v = o.get("rotulo" if gold and k == "s_exame" else campo)
            if v not in (None, ""): c[k][nt(v)] += 1
    return c

def por_doc(gab, pred, metodo):
    """Contagens (tp, fp, fn) por campo + pares para acurácia LOINC + recall vistos/não vistos."""
    G, P = chaves(gab["observacoes"], True), chaves(pred["observacoes"])
    d = {}
    for k in G:
        if k.startswith("s_") and metodo == "gemini_e2e": continue
        tp = sum((G[k] & P[k]).values()); d[k] = (tp, sum(P[k].values()) - tp, sum(G[k].values()) - tp)
    # acurácia LOINC: observações previstas pareadas ao gabarito pelo valor canônico
    pv = Counter(r4(o.get("valor")) for o in pred["observacoes"])
    ok = n = 0; sub = {True: [0, 0, 0, 0], False: [0, 0, 0, 0]}  # [n_gold, rec_exame, n_pares, loinc_ok]
    pl = {(o.get("loinc"), r4(o.get("valor")), o.get("unidade"), r4(o.get("ref_low")), r4(o.get("ref_high"))) for o in pred["observacoes"]}
    for g in gab["observacoes"]:
        s = sub[g["rotulo_visto"] if "rotulo_visto" in g else True]; s[0] += 1
        s[1] += (g["loinc"], r4(g["valor"]), g["unidade"], r4(g["ref_low"]), r4(g["ref_high"])) in pl
        cand = [o for o in pred["observacoes"] if r4(o.get("valor")) == r4(g["valor"])]
        if cand and pv[r4(g["valor"])] == 1:
            n += 1; s[2] += 1; c = cand[0].get("loinc") == g["loinc"]; ok += c; s[3] += c
    d["loinc"] = (ok, n); d["sub"] = sub
    return d

def f1(t):
    tp, fp, fn = t; p = tp / (tp + fp) if tp + fp else 0; r = tp / (tp + fn) if tp + fn else 0
    return p, r, (2 * p * r / (p + r) if p + r else 0)

def soma(ds, k): return tuple(map(sum, zip(*[d[k] for d in ds])))

def ic(ds, fn):
    rng = random.Random(SEED); vals = sorted(fn([rng.choice(ds) for _ in ds]) for _ in range(B))
    return vals[int(0.025 * B)], vals[int(0.975 * B) - 1]

def validacao(metodo, conj):
    f = RES / "validacao" / f"{metodo}_{conj}.csv"
    if not f.exists(): return None
    return {r["doc"]: r["valido"] == "1" for r in csv.DictReader(open(f, encoding="utf-8"))}

PARES = [("gliner_hib", "regex"), ("gliner_hib", "gemini_ent"), ("regex", "gemini_ent"), ("gemini_e2e", "gliner_hib")]

def diferencas(conj, gabs):
    """Bootstrap PAREADO (mesmos laudos reamostrados para os dois métodos) da diferença de acurácia LOINC e de F1."""
    ids = sorted(gabs); D = {}
    for m in {x for p in PARES for x in p}:
        pf = RES / "pred" / f"{m}_{conj}.json"
        if pf.exists(): pr = json.loads(pf.read_text(encoding="utf-8")); D[m] = [por_doc(gabs[i], pr[i], m) for i in ids]
    acc = lambda ds: (lambda t: t[0] / t[1] if t[1] else 0)(soma(ds, "loinc"))
    fc = lambda ds: f1(soma(ds, "completa"))[2]
    def rnv(ds):  # recall da observação completa nos rótulos NÃO vistos
        n = sum(d["sub"][False][0] for d in ds); return sum(d["sub"][False][1] for d in ds) / n if n else 0
    L = []
    for a, b in PARES:
        if a not in D or b not in D: continue
        for nome, fn in (("acuracia_loinc", acc), ("f1_obs_completa", fc), ("recall_nao_vistos", rnv)):
            obs = fn(D[a]) - fn(D[b]); rng = random.Random(SEED); n = len(ids); bs = []
            for _ in range(B):
                ix = [rng.randrange(n) for _ in range(n)]
                bs.append(fn([D[a][i] for i in ix]) - fn([D[b][i] for i in ix]))
            bs.sort(); pv = min(1.0, 2 * min(sum(x <= 0 for x in bs), sum(x >= 0 for x in bs)) / B)
            L.append([a, b, nome, f"{obs:+.3f}", f"{bs[25]:+.3f}", f"{bs[974]:+.3f}", f"{pv:.3f}"])
    csv.writer(open(RES / f"diferencas_{conj}.csv", "w", newline="", encoding="utf-8")).writerows(
        [["metodo_a", "metodo_b", "metrica", "diferenca_a_menos_b", "ic95_inf", "ic95_sup", "p_bootstrap_bilateral"]] + L)
    return L

def metricas(conj):
    gabs = {p.stem: json.loads(p.with_suffix(".json").read_text(encoding="utf-8")) for p in docs(conj)}
    campos = ["exame", "valor", "unidade", "faixa", "completa", "s_exame", "s_valor", "s_unidade", "s_faixa"]
    linhas_c, linhas_f, linhas_v, linhas_cond = [], [], [], []
    for m in METODOS:
        pf = RES / "pred" / f"{m}_{conj}.json"
        if not pf.exists(): continue
        preds = json.loads(pf.read_text(encoding="utf-8")); ids = sorted(gabs)
        ds = [por_doc(gabs[i], preds[i], m) for i in ids]
        for k in campos:
            if k not in ds[0]: continue
            p, r, f = f1(soma(ds, k)); lo, hi = ic(ds, lambda s: f1(soma(s, k))[2])
            linhas_c.append([m, k, len(ids), f"{p:.3f}", f"{r:.3f}", f"{f:.3f}", f"{lo:.3f}", f"{hi:.3f}"])
        acc = lambda s: (lambda t: t[0] / t[1] if t[1] else 0)(soma(s, "loinc"))
        lo, hi = ic(ds, acc)
        val = validacao(m, conj)
        if val:
            vv = [val.get(i, False) for i in ids]; pv = sum(vv) / len(vv)
            rng = random.Random(SEED); bs = sorted(sum(rng.choice(vv) for _ in vv) / len(vv) for _ in range(B))
            vtxt = [f"{100*pv:.1f}", f"{100*bs[25]:.1f}", f"{100*bs[974]:.1f}"]
        else: vtxt = ["NA", "NA", "NA"]
        lat = [preds[i]["latencia_s"] for i in ids]
        cham = sum(preds[i].get("chamadas", 0) for i in ids); tok = sum(preds[i].get("tokens", 0) for i in ids)
        modelo = next((preds[i].get("modelo") for i in ids if preds[i].get("modelo")), "")
        linhas_f.append([m, len(ids), f"{acc(ds):.3f}", f"{lo:.3f}", f"{hi:.3f}", *vtxt, f"{sum(lat)/len(lat):.3f}",
                         f"{cham/len(ids):.2f}", f"{tok/len(ids):.0f}", modelo])
        for visto in (True, False):
            s = [sum(d["sub"][visto][j] for d in ds) for j in range(4)]
            if s[0]: linhas_v.append([m, "visto" if visto else "nao_visto", s[0], f"{s[1]/s[0]:.3f}", s[2], f"{s[3]/s[2]:.3f}" if s[2] else "NA"])
        for nome, sel in [("layout=" + l, lambda g, l=l: g["layout"] == l) for l in ("tabela", "colunas", "blocos", "legado", "lab_br")] + \
                         [("escaneado", lambda g: g["escaneado"]), ("digital", lambda g: not g["escaneado"])]:
            sd = [d for i, d in zip(ids, ds) if sel(gabs[i])]
            if sd: linhas_cond.append([m, nome, len(sd), f"{f1(soma(sd, 'completa'))[2]:.3f}"])
    w = lambda n, h, L: csv.writer(open(RES / n, "w", newline="", encoding="utf-8")).writerows([h] + L)
    w(f"campos_{conj}.csv", ["metodo", "campo", "docs", "precisao", "recall", "f1", "ic95_inf", "ic95_sup"], linhas_c)
    w(f"fhir_custo_{conj}.csv", ["metodo", "docs", "acuracia_loinc", "ic95_inf", "ic95_sup", "pct_validos_hl7", "ic95_inf", "ic95_sup",
                                 "latencia_media_s", "chamadas_por_laudo", "tokens_por_laudo", "modelo"], linhas_f)
    w(f"vistos_naovistos_{conj}.csv", ["metodo", "rotulo", "obs_gabarito", "recall_obs_completa", "pares_por_valor", "acuracia_loinc"], linhas_v)
    w(f"por_condicao_{conj}.csv", ["metodo", "condicao", "docs", "f1_obs_completa"], linhas_cond)
    ldif = diferencas(conj, gabs)
    tabelas_tex(conj, linhas_c, linhas_f, linhas_v, ldif); figura(conj, linhas_c)
    for L in (linhas_c, linhas_f, linhas_v, linhas_cond, ldif):
        for l in L: print(*l)

def tabelas_tex(conj, lc, lf, lv, ld=()):
    C = {(l[0], l[1]): l for l in lc}
    fmt = lambda l: f"{float(l[5]):.2f} [{float(l[6]):.2f}; {float(l[7]):.2f}]".replace(".", ",") if l else "--"
    t = ["% Gerado por src/avaliar.py — conjunto " + conj, r"\begin{table}[ht]\centering\small",
         r"\caption{F1 por campo (normalizado e ligado ao LOINC) no teste, IC 95\% por \textit{bootstrap}.}\label{tab:campos}",
         r"\begin{tabular}{lccccc}\toprule", r"Método & Exame (LOINC) & Valor & Unidade & Faixa de ref. & Obs. completa\\\midrule"]
    for m in METODOS:
        if (m, "exame") in C: t.append(NOME[m] + " & " + " & ".join(fmt(C.get((m, k))) for k in ("exame", "valor", "unidade", "faixa", "completa")) + r"\\")
    t += [r"\bottomrule\end{tabular}\end{table}", "",
          r"\begin{table}[ht]\centering\small", r"\caption{F1 do reconhecimento de trechos (texto normalizado), antes da ligação.}\label{tab:spans}",
          r"\begin{tabular}{lcccc}\toprule", r"Método & Exame & Valor & Unidade & Faixa\\\midrule"]
    for m in METODOS:
        if (m, "s_exame") in C: t.append(NOME[m] + " & " + " & ".join(fmt(C.get((m, k))) for k in ("s_exame", "s_valor", "s_unidade", "s_faixa")) + r"\\")
    t += [r"\bottomrule\end{tabular}\end{table}", "",
          r"\begin{table}[ht]\centering\small", r"\caption{Acurácia LOINC, conformidade HL7 R5, latência e custo por laudo.}\label{tab:fhir}",
          r"\begin{tabular}{lcccc}\toprule", r"Método & Acur. LOINC & Válidos HL7 (\%) & Latência (s) & Chamadas / \textit{tokens}\\\midrule"]
    for l in lf:
        val = f"{l[5]} [{l[6]}; {l[7]}]" if l[5] != "NA" else "--"
        t.append(f"{NOME[l[0]]} & {l[2]} [{l[3]}; {l[4]}] & {val} & {l[8]} & {l[9]} / {l[10]}".replace(".", ",") + r"\\")
    t += [r"\bottomrule\end{tabular}\end{table}", "",
          r"\begin{table}[ht]\centering\small", r"\caption{Rótulos vistos vs.\ não vistos no dicionário: recall da observação completa e acurácia LOINC.}\label{tab:vistos}",
          r"\begin{tabular}{llccc}\toprule", r"Método & Rótulo & Obs. & Recall obs. & Acur. LOINC\\\midrule"]
    for l in lv: t.append(f"{NOME[l[0]]} & {l[1].replace('_', ' ')} & {l[2]} & {l[3]} & {l[5]}".replace(".", ",") + r"\\")
    t.append(r"\bottomrule\end{tabular}\end{table}")
    if ld:
        t += ["", r"\begin{table}[ht]\centering\small",
              r"\caption{Diferenças pareadas (\textit{bootstrap} pareado por laudo, 1000 reamostragens): método A $-$ método B.}\label{tab:dif}",
              r"\begin{tabular}{llccc}\toprule", r"A vs.\ B & Métrica & Diferença & IC 95\% & $p$\\\midrule"]
        for l in ld:
            t.append(f"{NOME[l[0]]} -- {NOME[l[1]]} & {l[2].replace('_', ' ')} & {l[3]} & [{l[4]}; {l[5]}] & {'$<$0.001' if l[6] == '0.000' else l[6]}".replace(".", ",") + r"\\")
        t.append(r"\bottomrule\end{tabular}\end{table}")
    (RES / ("tabelas.tex" if conj == "teste" else f"tabelas_{conj}.tex")).write_text("\n".join(t) + "\n", encoding="utf-8")

def figura(conj, lc):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    ks = ["exame", "valor", "unidade", "faixa", "completa"]; ms = [m for m in METODOS if any(l[0] == m for l in lc)]
    C = {(l[0], l[1]): l for l in lc}; fig, ax = plt.subplots(figsize=(7, 3.2)); w = 0.8 / max(len(ms), 1)
    for j, m in enumerate(ms):
        y = [float(C[(m, k)][5]) for k in ks]; e = [[y[i] - float(C[(m, k)][6]) for i, k in enumerate(ks)], [float(C[(m, k)][7]) - y[i] for i, k in enumerate(ks)]]
        ax.bar([i + j * w for i in range(len(ks))], y, w, yerr=e, capsize=2, label=NOME[m])
    ax.set_xticks([i + w * (len(ms) - 1) / 2 for i in range(len(ks))]); ax.set_xticklabels(["Exame", "Valor", "Unidade", "Faixa", "Obs. completa"])
    ax.set_ylabel("F1"); ax.set_ylim(0, 1.05); ax.legend(fontsize=7, loc="lower left"); fig.tight_layout()
    fig.savefig(RES / f"f1_campos_{conj}.png", dpi=200); fig.savefig(RES / f"f1_campos_{conj}.pdf")

if __name__ == "__main__":
    if sys.argv[1] == "rodar": rodar(sys.argv[2], sys.argv[3])
    else: metricas(sys.argv[2])
