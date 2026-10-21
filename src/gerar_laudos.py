"""Gera laudos laboratoriais sintéticos em PDF (pt-BR) + gabarito JSON, seguindo data/REGRAS_VARIACAO.md.
Uso: python gerar_laudos.py <conjunto> <n> <seed>   (dev 60 1 | teste 150 2026)"""
import json, random, sys, pathlib, io, unicodedata
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from exames import EXAMES
from rotulos_ocultos import OCULTOS, P_OCULTO_TESTE

NOMES = ["Ana Souza", "Bruno Lima", "Carla Dias", "Diego Rocha", "Elisa Prado", "Fábio Nunes", "Gabriela Melo",
         "Hugo Reis", "Íris Campos", "João Batista Moura", "Lúcia Ferreira", "Marcos Antônio Vieira", "Natália Gomes",
         "Otávio Pereira", "Patrícia Ramos", "Rafael Conceição", "Sílvia Araújo", "Tiago Monteiro", "Vânia Lopes"]
LABS = ["Laboratório Exemplo de Análises Clínicas", "LabSul Diagnósticos (fictício)", "Centro de Análises Vale do Rio Pardo (fictício)"]
LAYOUTS = ["tabela", "colunas", "blocos", "legado"]
P_ESCANEADO = 0.30

def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

def fmt(v, dec, sep, milhar=False):
    if milhar:
        return f"{int(round(v)):,}".replace(",", ".")
    s = f"{v:.{dec}f}"
    return s.replace(".", ",") if sep == "," else s

def faixa(lo, hi, dec, sep, fator, milhar, legado, rng):
    f = lambda x: fmt(x * fator, dec, sep, milhar)
    if lo is None:
        return rng.choice(["ATE " + f(hi), "< " + f(hi)] if legado else ["Até " + f(hi), "< " + f(hi)])
    return rng.choice([f"{f(lo)} a {f(hi)}", f"{f(lo)} - {f(hi)}", f"{f(lo)} – {f(hi)}"])

def gerar(i, rng, out, ocultos=False):
    layout = rng.choice(LAYOUTS); legado = layout == "legado"
    sep = "," if rng.random() < 0.7 else "."
    nome = rng.choice(NOMES)
    data = f"2026-{rng.randint(1,9):02d}-{rng.randint(1,28):02d}"
    nasc = f"{rng.randint(1940,2010)}-{rng.randint(1,12):02d}-{rng.randint(1,28):02d}"
    linhas, obs = [], []
    for nome_ex, sin, loinc, disp, ucum, (lo, hi), (rlo, rhi), dec, unids in rng.sample(EXAMES, rng.randint(4, 8)):
        rotulo = rng.choice([nome_ex] + sin); visto = True
        if ocultos and loinc in OCULTOS and rng.random() < P_OCULTO_TESTE: rotulo = rng.choice(OCULTOS[loinc]); visto = False
        un_imp, fator = rng.choice(unids); milhar = fator == 1000
        v = round(rng.uniform(lo, hi), dec)
        vtxt = fmt(v * fator, dec, sep, milhar)
        ftxt = faixa(rlo, rhi, dec, sep, fator, milhar, legado, rng)
        if legado: rotulo, un_imp, ftxt = sem_acento(rotulo).upper(), sem_acento(un_imp), ftxt
        linhas.append((rotulo, vtxt, un_imp, ftxt))
        obs.append({"loinc": loinc, "display": disp, "rotulo": rotulo, "rotulo_visto": visto, "valor": v, "unidade": ucum,
                    "ref_low": rlo, "ref_high": rhi, "texto_valor": vtxt, "texto_unidade": un_imp, "texto_faixa": ftxt})
    lab = rng.choice(LABS)
    pdf = out / f"laudo_{i:03d}.pdf"
    c = canvas.Canvas(str(pdf), pagesize=A4)
    font = "Courier" if layout in ("colunas", "legado") else "Helvetica"
    U = (lambda s: sem_acento(s).upper()) if legado else (lambda s: s)
    c.setFont(font + "-Bold", 13); c.drawString(50, 805, U(lab))
    c.setFont(font, 8)
    c.drawString(50, 792, U(f"CNES {rng.randint(1000000,9999999)} - Resp. Técnico: Dr(a). Fulano de Tal - CRBM {rng.randint(1000,9999)}"))
    c.setFont(font, 10)
    c.drawString(50, 770, U(f"Paciente: {nome}")); c.drawString(350, 770, U(f"Nascimento: {nasc}"))
    c.drawString(50, 755, U(f"Data: {data}")); c.drawString(350, 755, U(f"Solicitante: Dr(a). Exemplo"))
    y = 725
    if layout == "tabela":
        c.setFont("Helvetica-Bold", 10)
        for x, h in zip((50, 230, 310, 400), ("Exame", "Resultado", "Unidade", "Referência")): c.drawString(x, y, h)
        c.setFont("Helvetica", 10)
        for r in linhas:
            y -= 18
            for x, t in zip((50, 230, 310, 400), r): c.drawString(x, y, t)
    elif layout == "colunas":
        c.setFont("Courier-Bold", 9); c.drawString(50, y, f"{'':26}{'Resultado':>12}  {'':12}Valores de Referência")
        c.setFont("Courier", 9)
        for r, v, u, f in linhas:
            y -= 15; c.drawString(50, y, f"{r[:26]:<26}{v:>12}  {u:<12}{f}")
    elif layout == "blocos":
        for r, v, u, f in linhas:
            c.setFont("Helvetica-Bold", 10); c.drawString(50, y, r.upper()); y -= 13
            c.setFont("Helvetica", 8); c.drawString(50, y, "Material: Sangue   Método: Automatizado"); y -= 13
            c.setFont("Helvetica", 10); c.drawString(50, y, f"Resultado: {v} {u}"); y -= 13
            c.drawString(50, y, f"Valor de referência: {f}"); y -= 22
    else:
        c.setFont("Courier", 9)
        for r, v, u, f in linhas:
            y -= 15; c.drawString(50, y, f"{(r + ' ').ljust(28, '.')}: {v} {u}   (VR: {f})")
    c.setFont(font, 8)
    c.drawString(50, 60, U(f"Liberado em {data}. Assinado eletronicamente. Interpretação a critério médico. Pág. 1 de 1"))
    c.save()
    esc = rng.random() < P_ESCANEADO
    if esc: escanear(pdf, rng)
    gab = {"id": pdf.stem, "paciente": nome, "nascimento": nasc, "data": data, "layout": layout,
           "separador_decimal": sep, "escaneado": esc, "observacoes": obs}
    (out / f"laudo_{i:03d}.json").write_text(json.dumps(gab, ensure_ascii=False, indent=2))

def escanear(pdf, rng):
    """Ruído de digitalização SIMULADO (hipótese, REGRAS R6): render -> rotação -> blur -> ruído -> JPEG -> PDF imagem."""
    import pymupdf, numpy as np
    from PIL import Image, ImageFilter
    doc = pymupdf.open(pdf); pix = doc[0].get_pixmap(dpi=150, colorspace=pymupdf.csGRAY); doc.close()
    img = Image.frombytes("L", (pix.width, pix.height), pix.samples)
    img = img.rotate(rng.uniform(-1.5, 1.5), resample=Image.BICUBIC, fillcolor=255, expand=False)
    img = img.filter(ImageFilter.GaussianBlur(rng.uniform(0.3, 0.9)))
    a = np.asarray(img, dtype=np.float32)
    a += np.random.default_rng(rng.randint(0, 2**31)).normal(0, rng.uniform(4, 12), a.shape)
    img = Image.fromarray(a.clip(0, 255).astype("uint8"))
    buf = io.BytesIO(); img.save(buf, "JPEG", quality=rng.randint(35, 70)); buf.seek(0)
    Image.open(buf).save(pdf, "PDF", resolution=150)

if __name__ == "__main__":
    conj, n, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    out = pathlib.Path(__file__).parent.parent / "data" / conj; out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    for i in range(n): gerar(i, rng, out, ocultos=(conj == "teste"))
    print(f"{n} laudos em {out} (seed {seed})")
