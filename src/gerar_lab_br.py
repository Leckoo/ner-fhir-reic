"""5º layout sintético `lab_br` (CONJUNTO ADICIONAL, separado do teste congelado de 150).
Segue o padrão comum de laudos de laboratórios brasileiros (data/layout-lab_br-estrutura.md e síntese no fim de
data/laudos-publicos-br.md), sem copiar nenhum laudo real, sem logotipo e sem nome de instituição real.
Estrutura (organização apenas; nenhum texto/nome copiado): cabeçalho em grade de 2 colunas com rótulos em negrito
(NOME/CONVENIO/DR.(a)/CRM/DATA/EXAME | IDADE/DN/ID/LOGIN), título centralizado sublinhado ('HEMOGRAMA COMPLETO' só com hemograma; senão 'EXAMES LABORATORIAIS', igual no campo EXAME), 'Material:'/'Método:'
sublinhados, Eritrograma/Leucograma (% e absoluto)/Plaquetas/Bioquímica em tabela, 'Dados clínicos:' (50%) e 'Observações:'/'Nota:' (60%) com
frases fixas sorteadas (texto livre, sem números, FORA do gabarito), nota sobre a origem dos valores de referência,
fonte serifada; mesma UF do CRM no cabeçalho e no rodapé; rodapé com assinatura à direita (médico fictício, CRM/UF, RQE), 'Cidade Exemplo, DD de mês de AAAA.',
Diretor Técnico à esquerda e linha final com razão social genérica fictícia, '1 de 1' e hora. Vírgula decimal e ponto de milhar; faixas "x a y unidade" e "Até y unidade".
Mesmas regras de variação do teste (sorteio de 4-8 exames, sinônimos, unidades alternativas, rótulos não vistos com
P_OCULTO_TESTE, 30% escaneado simulado). NÃO altera gerar_laudos.py nem os layouts existentes.
Uso: python gerar_lab_br.py [conjunto=adicional_lab_br] [n=50] [seed=2027]"""
import json, random, sys, pathlib
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from exames import EXAMES
from rotulos_ocultos import OCULTOS, P_OCULTO_TESTE
from gerar_laudos import NOMES, P_ESCANEADO, fmt, escanear

LAYOUT = "lab_br"
ERITRO = {"718-7", "4544-3", "789-8", "787-2", "785-6", "786-4", "788-0"}
LEUCO, PLAQ = "6690-2", "777-3"
# diferencial do leucograma: impresso em % e /mm³, FORA do catálogo LOINC => não entra no gabarito (distrator)
DIFERENCIAL = [("Neutrófilos", 40, 70), ("Bastonetes", 0, 5), ("Segmentados", 40, 65), ("Eosinófilos", 1, 5),
               ("Basófilos", 0, 2), ("Linfócitos", 20, 40), ("Monócitos", 2, 10)]
MEDICOS = ["Dr(a). Fulano de Tal", "Dr(a). Beltrano Exemplo", "Dr(a). Ciclana Fictícia"]  # fictícios
CONVENIOS = ["Particular", "Convênio Exemplo", "Plano Fictício Saúde"]
UFS = ["RS", "SC", "PR", "SP", "MG"]
# Seções de texto livre (DISTRATORES, fora do gabarito): frases fixas, sem números, sorteadas pela seed (sem API).
DADOS_CLINICOS = ["Check-up anual.", "Jejum informado pelo paciente.", "Controle de diabetes.", "Investigação de anemia.",
                  "Acompanhamento ambulatorial.", "Uso de medicação contínua informado."]
NOTAS_GERAIS = ["Valores de referência conforme idade e sexo.", "Resultados liberados após conferência.",
                "Resultado confirmado em nova dosagem."]
NOTAS_HEMO = ["Eritrograma sem alterações morfológicas.", "Plaquetas com morfologia normal ao esfregaço.",
              "Série branca sem atipias ao esfregaço."]
NOTAS_BIOQ = ["Amostra lipêmica.", "Amostra levemente hemolisada.", "Confirmar resultado a critério médico."]
NOTA_REF = "Valores de referência: bula do fabricante dos reagentes e literatura técnica vigente."
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro"]

def faixa_br(lo, hi, dec, fator, milhar, un, rng):
    f = lambda x: fmt(x * fator, dec, ",", milhar)
    if lo is None: return f"Até {f(hi)} {un}"
    return f"{f(lo)} a {f(hi)} {un}"

def data_br(rng):
    return rng.randint(1, 28), rng.randint(1, 9)

def gerar(i, rng, out):
    nome = rng.choice(NOMES); d, m = data_br(rng)
    data = f"2026-{m:02d}-{d:02d}"; nasc = f"{rng.randint(1940,2010)}-{rng.randint(1,12):02d}-{rng.randint(1,28):02d}"
    br = lambda iso: "/".join(reversed(iso.split("-")))
    secoes = {"ERITROGRAMA": [], "LEUCOGRAMA": [], "PLAQUETAS": [], "BIOQUÍMICA": []}; obs = []
    leuco_abs = None
    for nome_ex, sin, loinc, disp, ucum, (lo, hi), (rlo, rhi), dec, unids in rng.sample(EXAMES, rng.randint(4, 8)):
        rotulo = rng.choice([nome_ex] + sin); visto = True
        if loinc in OCULTOS and rng.random() < P_OCULTO_TESTE: rotulo = rng.choice(OCULTOS[loinc]); visto = False
        un_imp, fator = rng.choice(unids); milhar = fator == 1000
        v = round(rng.uniform(lo, hi), dec)
        vtxt = fmt(v * fator, dec, ",", milhar); ftxt = faixa_br(rlo, rhi, dec, fator, milhar, un_imp, rng)
        sec = "ERITROGRAMA" if loinc in ERITRO else "LEUCOGRAMA" if loinc == LEUCO else "PLAQUETAS" if loinc == PLAQ else "BIOQUÍMICA"
        secoes[sec].append((rotulo, vtxt, un_imp, ftxt))
        if loinc == LEUCO: leuco_abs = v * 1000
        obs.append({"loinc": loinc, "display": disp, "rotulo": rotulo, "rotulo_visto": visto, "valor": v, "unidade": ucum,
                    "ref_low": rlo, "ref_high": rhi, "texto_valor": vtxt, "texto_unidade": un_imp, "texto_faixa": ftxt,
                    "secao": sec})
    pdf = out / f"laudo_{i:03d}.pdf"
    c = canvas.Canvas(str(pdf), pagesize=A4); F, FB = "Times-Roman", "Times-Bold"
    def rot(x, y, r, v):  # rótulo em negrito/maiúsculas + valor
        c.setFont(FB, 9); c.drawString(x, y, r); c.setFont(F, 9); c.drawString(x + c.stringWidth(r, FB, 9) + 4, y, v)
    def sub(x, y, t, fb=FB, tam=10):  # texto sublinhado
        c.setFont(fb, tam); c.drawString(x, y, t); c.line(x, y - 2, x + c.stringWidth(t, fb, tam), y - 2)
    so_hemo = not secoes["BIOQUÍMICA"]
    so_bioq = not any(secoes[s] for s in ("ERITROGRAMA", "LEUCOGRAMA", "PLAQUETAS"))
    titulo = "HEMOGRAMA COMPLETO" if so_hemo else "EXAMES LABORATORIAIS"  # misto ou só bioquímica
    uf = rng.choice(UFS)  # mesma UF no CRM do cabeçalho e no rodapé
    esq = [("NOME:", nome), ("CONVENIO:", rng.choice(CONVENIOS)), ("DR.(a):", "Exemplo Solicitante"),
           ("CRM:", f"{rng.randint(10000, 99999)}/{uf}"), ("DATA:", br(data)), ("EXAME:", titulo)]
    dir_ = [("IDADE:", f"{2026 - int(nasc[:4])} anos"), ("DN:", br(nasc)), ("ID/LOGIN:", f"{rng.randint(100000, 999999)}")]
    for k, (r, v) in enumerate(esq): rot(50, 805 - 12 * k, r, v)
    for k, (r, v) in enumerate(dir_): rot(360, 805 - 12 * k, r, v)
    c.line(50, 732, 545, 732); y = 712
    w = c.stringWidth(titulo, FB, 12); sub(297 - w / 2, y, titulo, FB, 12); y -= 22
    mat = "Soro" if so_bioq else "Sangue total (EDTA)" + (" e soro" if secoes["BIOQUÍMICA"] else "")
    sub(50, y, "Material:"); c.setFont(F, 10); c.drawString(100, y, mat); y -= 14
    met = ("Automatizado - enzimático colorimétrico" if so_bioq else "Automatizado - citometria de fluxo e impedância"
           + ("; bioquímica por método enzimático colorimétrico" if secoes["BIOQUÍMICA"] else ""))
    sub(50, y, "Método:"); c.setFont(F, 10); c.drawString(100, y, met); y -= 14
    if rng.random() < 0.5:
        sub(50, y, "Dados clínicos:"); c.setFont(F, 10); c.drawString(125, y, rng.choice(DADOS_CLINICOS)); y -= 14
    y -= 6
    def cab_tabela(y):
        c.setFont(FB, 9)
        for x, h in zip((60, 250, 320, 390), ("Analito", "Resultado", "Unidade", "Valores de Referência")): c.drawString(x, y, h)
        return y - 14
    def linha(y, r, v, u, f):
        c.setFont(F, 10)
        for x, t in zip((60, 250, 320, 390), (r, v, u, f)): c.drawString(x, y, t)
        return y - 14
    for sec in ("ERITROGRAMA", "LEUCOGRAMA", "PLAQUETAS", "BIOQUÍMICA"):
        if not secoes[sec]: continue
        sub(50, y, sec.capitalize() + ":"); y -= 15
        y = cab_tabela(y)
        for r in secoes[sec]: y = linha(y, *r)
        if sec == "LEUCOGRAMA" and leuco_abs:  # diferencial em % e absoluto (fora do gabarito)
            pcts = [rng.randint(a, b) for _, a, b in DIFERENCIAL]
            for (nd, a, b), pc in zip(DIFERENCIAL, pcts):
                ab = fmt(leuco_abs * pc / 100, 0, ",", True)
                ra, rb = fmt(a * 40, 0, ",", True), fmt(b * 110, 0, ",", True)
                c.setFont(F, 10); c.drawString(70, y, nd); c.drawString(250, y, f"{pc} %   {ab} /mm³")
                c.drawString(390, y, f"{a} a {b} %   {ra} a {rb} /mm³"); y -= 14
        y -= 8
    if rng.random() < 0.6:
        pool = NOTAS_GERAIS + (NOTAS_HEMO if not so_bioq else []) + (NOTAS_BIOQ if secoes["BIOQUÍMICA"] else [])
        rot_n = rng.choice(["Observações:", "Nota:"]); x0 = 50 + c.stringWidth(rot_n, FB, 10) + 6
        sub(50, y, rot_n); c.setFont(F, 10); c.drawString(x0, y, " ".join(rng.sample(pool, rng.randint(1, 2)))); y -= 14
    c.setFont(F, 8); c.drawString(50, 162, NOTA_REF)
    gerar.y_min = min(getattr(gerar, "y_min", 999), y)
    medico, dt = rng.choice(MEDICOS), rng.choice(MEDICOS)
    c.setFont(F, 9)
    c.drawRightString(545, 150, medico); c.drawRightString(545, 139, f"CRM/{uf} {rng.randint(1000, 99999)} - RQE {rng.randint(1000, 99999)}")
    c.drawString(50, 118, f"Cidade Exemplo, {d:02d} de {MESES[m - 1]} de 2026.")
    c.drawString(50, 100, f"Diretor Técnico - CRM/{uf} {rng.randint(1000, 99999)} - RQE {rng.randint(1000, 99999)} - {dt}")
    c.line(50, 80, 545, 80)
    hl = f"{rng.randint(11, 18):02d}:{rng.randint(0, 59):02d}"
    c.drawString(50, 68, "LABORATÓRIO CLÍNICO EXEMPLO LTDA (fictício)"); c.drawCentredString(330, 68, "1 de 1"); c.drawRightString(545, 68, hl)
    c.save()
    esc = rng.random() < P_ESCANEADO
    if esc: escanear(pdf, rng)
    gab = {"id": pdf.stem, "paciente": nome, "nascimento": nasc, "data": data, "layout": LAYOUT,
           "separador_decimal": ",", "escaneado": esc, "observacoes": obs}
    (out / f"laudo_{i:03d}.json").write_text(json.dumps(gab, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    conj = sys.argv[1] if len(sys.argv) > 1 else "adicional_lab_br"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 50; seed = int(sys.argv[3]) if len(sys.argv) > 3 else 2027
    out = pathlib.Path(__file__).parent.parent / "data" / conj
    if conj == "teste": sys.exit("ERRO: o teste é congelado")
    out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    for i in range(n): gerar(i, rng, out)
    print(f"y mínimo do conteúdo: {gerar.y_min:.0f} (rodapé começa em 170)")
    print(f"{n} laudos {LAYOUT} em {out} (seed {seed})")
