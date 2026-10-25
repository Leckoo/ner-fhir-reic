# ner-fhir: laudos laboratoriais em PDF (pt-BR) → HL7 FHIR R5

Benchmark sintético + pipeline do artigo REIC. Tudo roda com `./run_all.sh` (ou `./run_all.sh --sem-gemini`).

## Dados
- `data/REGRAS_VARIACAO.md`: regras de variação (4 layouts, sinônimos, vírgula/ponto, unidades alternativas, faixas
  "a"/"-"/"–"/"Até"/"<", ruído de digitalização **simulado (hipótese)** com OCR Tesseract `por`). Escritas antes dos dados.
- `data/fontes-referencias.md`: links e citações das fontes públicas consultadas (sem cópia de conteúdo de terceiros).
- `data/variantes-reais-fontes.md` → `src/rotulos_ocultos.py`: 39 rótulos reais fora do dicionário, usados **só no teste**
  (RDW-SD excluído: LOINC 21000-5). Nenhum extrator importa essa lista (teste automatizado garante).
- `data/dev/`: 60 laudos, seed 1 (único conjunto usado para ajustes).
- `data/teste/`: 150 laudos, seed 2026, **congelado**. `SHA256SUMS` (sha256 do próprio arquivo:
  `c3c25703cb5e0773d7002405bbb0f4c171563e0e33164cd8369b204600f31d79`), `REGRAS_SHA256` com o hash das regras/gerador
  (o hash de `gerar_laudos.py` foi atualizado em 25/10/2026: a única mudança depois do congelamento foi gravar o JSON com
  `encoding="utf-8"`, commit "Ler e gravar arquivos em UTF-8"; o hash original era `807abb1e…`).
  O `run_all.sh` não regenera o teste, só confere o hash (o ReportLab grava data de criação no PDF, então regenerar não
  daria bytes idênticos).
- `data/adicional_lab_br/`: **conjunto adicional** (5º layout `lab_br`), 50 laudos, seed 2027, gerado por
  `src/gerar_lab_br.py` (o `gerar_laudos.py` e os 4 layouts não mudam). Segue o padrão comum de laudos de laboratórios
  brasileiros (`data/layout-lab_br-estrutura.md`): cabeçalho em grade, título
  sublinhado, Material/Método, Eritrograma, Leucograma (% e absoluto; diferencial fora do catálogo LOINC, logo fora do
  gabarito), Plaquetas, Bioquímica, Conclusão/Observações, rodapé com assinatura e responsável técnico. Tudo fictício,
  sem logotipo nem nome de instituição real; vírgula decimal sempre. Mesmas regras de variação do teste (incl. rótulos
  não vistos). Hash próprio em `SHA256SUMS`; NÃO entra no teste de 150. Métricas: `results/*_adicional_lab_br.csv`
  (`cd src && ../.venv/bin/python avaliar.py metricas adicional_lab_br`).
- Histórico: (1) uma versão do teste sem rótulos fora do dicionário (hash `102e496e…`) foi substituída, ver R2b;
  (2) em 20/10 os `display` LOINC foram corrigidos para os nomes oficiais (conferência local) só nos gabaritos JSON, sem mudar os PDFs; os Bundles em `results/fhir/` foram regenerados.

## Pipeline e métodos (`src/`)
- `pipeline.py`: texto (pdfplumber; OCR se o PDF for imagem), normalização (UCUM, números, faixas), ligação LOINC
  (dicionário de `exames.py` + correspondência aproximada difflib ≥0,85), baseline **regex**, montagem do Bundle R5
  (`Patient`, `Observation` com LOINC, `valueQuantity` UCUM e `referenceRange`, `DiagnosticReport`).
- `extrator_gliner.py`: **gliner** (GLiNER `urchade/gliner_multi-v2.1` zero-shot com 4 rótulos) e **gliner_hib**
  (GLiNER só para o nome do exame + regras posicionais para valor/unidade/faixa). O gliner puro usa os rótulos em inglês
  "analyte", "measured value", "unit", "reference values", inferência linha a linha (linhas não vazias, lote 16, flat_ner),
  limiar 0,3; o híbrido usa só "analyte" com limiar 0,1 (varredura no dev).
- `ligacao_llm.py`: **gliner_llm** = gliner_hib + Gemini como **reserva** da ligação LOINC: só quando dicionário e difflib
  não acham código, o rótulo vai ao Gemini com o catálogo dos 20 códigos e saída JSON com `enum` (20 códigos ou
  "nenhum"). Cache por rótulo normalizado em `results/gemini/link/<conjunto>/` (sem chave no repo; `GEMINI_API_KEY`
  só pelo ambiente). Método acrescentado depois da análise de erros (post hoc).
- `extrator_gemini.py`: `gemini-3.1-flash-lite`, temperatura 0, saída JSON. **gemini_e2e** gera o Bundle FHIR direto
  (LOINC pela memória do modelo); **gemini_ent** extrai trechos e passa pela MESMA ligação do pipeline.
  Respostas em cache em `results/gemini/` (rodar de novo não gasta cota). ~14 req/min, retry em 503, modelo fixo.
- `validar.py`: validador oficial HL7 **versão 7.0.2** (`tools/validator_cli.jar`, baixado pelo `run_all.sh` da release 7.0.2; `-version 5.0` = FHIR R5, terminologia via tx.fhir.org).
  Válido = sem issue `error`/`fatal`.
- `avaliar.py`: P/R/F1 por campo (ligado: exame/LOINC, valor, unidade, faixa, observação completa; trechos: exame,
  valor, unidade, faixa por texto normalizado), acurácia LOINC (pares pelo valor), vistos × não vistos, por layout e
  digital × escaneado, latência (média e mediana), chamadas e tokens; acurácia LOINC condicional (sobre pares pelo
  valor) e absoluta (sobre todas as observações do gabarito); IC 95% por bootstrap (10000 reamostragens de laudos,
  seed 12345). Diferenças pareadas (`diferencas_<conj>.csv`): família declarada de 6 pares × 3 métricas = 18 testes,
  Bonferroni α = 0,05/18 ≈ 0,0028 (p mínimo não nulo = 2/10000).
- `sensibilidade_e2e.py`: validade HL7 do gemini_e2e após pós-processamento sem API (`display` do catálogo e UUIDs
  válidos; + unidade UCUM). Saída `results/sensibilidade_e2e_teste.csv`.
- `erros_nao_vistos.py`: erros por rótulo não visto × método, por família (prefixo "Dosagem de", sigla,
  sinônimo/descritivo), cortes de prefixo. Saída `results/erros_nao_vistos[_resumo]_<conj>.csv`.
- `fp_lab_br.py`: origem dos falsos positivos no lab_br (cabeçalho/rodapé, diferencial do leucograma, linha de
  resultado...). Saída `results/fp_origem_adicional_lab_br.csv`.

## Saídas (`results/`)
`campos_teste.csv`, `fhir_custo_teste.csv`, `vistos_naovistos_teste.csv`, `por_condicao_teste.csv`, `tabelas.tex`,
`f1_campos_teste.png/.pdf`, `exemplo_bundle.json` (Listagem 1), `validacao/`, `fhir/<método>/<conjunto>/`, `pred/`.
Os mesmos arquivos com sufixo `_dev` são do conjunto de desenvolvimento.

No lab_br nenhum Bundle dos métodos determinísticos é válido (0/50): o cabeçalho em grade (`NOME:`, `DN: dd/mm/aaaa`)
não é reconhecido por `pipeline.cabecalho`, que gera `Patient` vazio (bdl-3a/bdl-5). Registrado como achado, sem ajuste.

Latência: tempo de extração a partir do texto já extraído (a extração de texto/OCR é comum a todos os métodos e não entra).

## Regerar tabelas sem chamar a API do Gemini

As predições de todos os métodos já estão salvas em `results/pred/` e o cache do Gemini em `results/gemini/`. Para recalcular métricas, diferenças pareadas, `tabelas.tex` e figuras sem nenhuma chamada à API (e sem `GEMINI_API_KEY`):

```bash
cd src
../.venv/bin/python avaliar.py metricas teste   # e/ou: metricas dev
```

Rodar `avaliar.py rodar gemini_* ...` também reaproveita o cache e só chama a API para laudos ainda não processados.

## Licença
- Código: MIT (`LICENSE`), © 2026 Leonardo Antonio Patatt.
- Dados sintéticos (`data/dev`, `data/teste`, `data/adicional_lab_br`) e resultados (`results/`): CC-BY 4.0
  (https://creativecommons.org/licenses/by/4.0/). Todos os laudos são fictícios, gerados por código; não há dado de paciente real.
