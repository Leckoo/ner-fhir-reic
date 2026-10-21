# Regras de variação dos laudos sintéticos

Escrito em 20/10/2026, **antes** de gerar os conjuntos dev/teste. Derivado de `referencias-reais/README.md`
(POP hemograma HC-UFTM [V], RDC 978/2025 ANVISA arts. 166–167 [V], modelo de laudo de hematologia [V];
itens [?] vistos só em trecho de busca). Nenhum dado real de paciente foi usado. Estas regras ficam
**congeladas** junto com o conjunto de teste (ver `data/teste/SHA256SUMS`).

## R1. Layouts (4, sorteados com probabilidade igual)
| id | descrição | origem |
|---|---|---|
| L1 `tabela` | tabela com cabeçalho Exame / Resultado / Unidade / Referência, fonte proporcional | layout 2 do README [?] e versão original do gerador |
| L2 `colunas` | texto monoespaçado alinhado por espaços (Courier), cabeçalho "Resultado  Valores de Referência" | layout 1 [V modelo] |
| L3 `blocos` | um bloco por exame: título em caixa alta, "Material:", "Método:", linha "Resultado: v unidade" e linha "Valor de referência: ..." | layout 4 [V modelo; RDC 978 art. 167] |
| L4 `legado` | sistema legado: CAIXA ALTA sem acentos, separador `NOME .....: valor unidade (VR: ...)` | [?] README §4 |

Todos têm cabeçalho com laboratório fictício, CNES, responsável técnico (CRBM/CRF), paciente, data de nascimento,
data de coleta e rodapé com data de emissão e assinatura (RDC 978, art. 167). A data de coleta é a data efetiva.

## R2. Rótulos: nomes, sinônimos e abreviações
Rótulo sorteado entre nome e sinônimos do catálogo (`src/exames.py`), por ex. Hemoglobina/Hb/HGB/
"Dosagem de hemoglobina"; Hematócrito/Ht/HCT; Leucócitos/WBC/"Leucócitos - Global"; Plaquetas/PLT/
"Contagem de plaquetas"; Glicose/GLI; "Glicemia de jejum" é exame próprio (LOINC 1558-6); Ureia/Uréia; Triglicerídeos/Triglicérides; Potássio/K;
Sódio/Na; TSH/Tireotrofina; além de hemácias, VCM/MCV, HCM/MCH, CHCM/MCHC, RDW/RDW-CV, TGO/AST, TGP/ALT.
Em L4 o rótulo sai em caixa alta sem acento.

## R3. Números
- Decimal com vírgula (70%) ou ponto (30%), sorteado por laudo (POP mistura ambos [V]).
- Número de casas decimais conforme o exame (0 a 2).
- Contagens celulares com unidade "/mm³" usam ponto de milhar (ex.: "7.800", "250.000") [V modelo].

## R4. Unidades alternativas (gabarito sempre em UCUM canônico)
| canônico UCUM | grafias impressas |
|---|---|
| g/dL | g/dL, g/dl, g/ dL |
| fL | fL, fl |
| 10*3/uL | x10³/µL, mil/mm³ (mesmo valor), /mm³ (valor ×1000) |
| 10*6/uL | x10^6/µL (o glifo ⁶ não existe nas fontes Type 1 padrão do PDF), milhões/mm³ |
| mg/dL, mmol/L, %, pg, U/L | idem; mmol/L às vezes mEq/L para Na/K (equivalente) |
| u[IU]/mL | µUI/mL, mUI/L (equivalentes) |
O gabarito grava o valor convertido para a unidade canônica; o extrator precisa normalizar.

## R5. Faixa de referência (gabarito: low/high, um deles pode ser nulo)
"a b" com " a " [V], "a - b" [V POP], "a – b" [V POP], "Até b" / "ATE b" [V/?], "< b" [V POP], "> a" [V POP] (só onde
faz sentido clínico: ex. colesterol total "< 190"). Em L4, prefixo "VR:".

## R6. Ruído de digitalização simulado (HIPÓTESE)
Não há exemplo público de laudo escaneado sem dados pessoais (README §5.7). 30% dos laudos são "escaneados":
página renderizada a 150 dpi (PyMuPDF) → rotação uniforme ±1,5° → desfoque gaussiano (raio 0,3–0,9) →
ruído gaussiano (σ 4–12) → JPEG qualidade 35–70 → PDF só com imagem. O texto desses PDFs é obtido por OCR com
Tesseract (`por`). **Supor que esse ruído representa laudos reais digitalizados é hipótese não verificada.**

## R7. Conjuntos
- dev: 60 laudos, seed 1 — único conjunto usado para ajustar regex, rótulos/limiar do GLiNER e prompt do LLM.
- teste: 150 laudos, seed 2026 — gerado uma vez, hash em `data/teste/SHA256SUMS`, nunca usado para ajuste.
- 4 a 8 exames por laudo, sem repetição de LOINC no laudo.

## R2b. Rótulos não vistos (só no teste)
**Histórico do teste.** Uma versão anterior do teste (seed 2026, SHA-256 do SHA256SUMS
`102e496e7159be53e9710e41ea4b6ad4fd8f7db18c6cfd36d18eb8c146aa54f5`) foi **substituída** antes de qualquer modelo
rodar nela, porque 0 de 909 rótulos estavam fora do dicionário de ligação (gerador e extratores usavam a mesma
lista de sinônimos: avaliação circular). Uma lista intermediária de variantes escrita à mão também foi descartada
sem uso (não vinha de fonte). Autorizado pelo Revisor em 20/10/2026.

**Regra atual.** No teste, cada exame tem probabilidade 0,35 de receber um rótulo de `src/rotulos_ocultos.py`,
gerado automaticamente de `data/variantes-reais-fontes.md` (Scraper): só as variantes com
`fora_do_dicionario = sim`, cada uma com fonte e trecho literal (39 usadas; RDW-SD excluída por ser outro LOINC,
21000-5, fora do catálogo). As variantes **não** foram escolhidas olhando erros de nenhum extrator e **não** entram
no dicionário de nenhum extrator nem da ligação LOINC (que usa só `src/exames.py` + correspondência aproximada).
O dev não tem rótulos ocultos. O gabarito marca `rotulo_visto`; métricas saem separadas para vistos e não vistos.
