# ner-fhir: laudos laboratoriais em PDF (pt-BR) → HL7 FHIR R5

Benchmark sintético + pipeline do artigo REIC. Tudo roda com `./run_all.sh` (ou `./run_all.sh --sem-gemini`).

## Dados
- `data/REGRAS_VARIACAO.md`: regras de variação (4 layouts, sinônimos, vírgula/ponto, unidades alternativas, faixas
  "a"/"-"/"–"/"Até"/"<", ruído de digitalização **simulado (hipótese)** com OCR Tesseract `por`). Escritas antes dos dados.
- `data/variantes-reais-fontes.md` → `src/rotulos_ocultos.py`: 39 rótulos reais fora do dicionário, usados **só no teste**
  (RDW-SD excluído: LOINC 21000-5). Nenhum extrator importa essa lista (teste automatizado garante).
- `data/dev/`: 60 laudos, seed 1 (único conjunto usado para ajustes).
- `data/teste/`: 150 laudos, seed 2026, **congelado**. `SHA256SUMS` (sha256 do próprio arquivo:
  `c3c25703cb5e0773d7002405bbb0f4c171563e0e33164cd8369b204600f31d79`), `REGRAS_SHA256` com o hash das regras/gerador.
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
  (GLiNER só para o nome do exame + regras posicionais para valor/unidade/faixa).
- `extrator_gemini.py`: `gemini-3.1-flash-lite`, temperatura 0, saída JSON. **gemini_e2e** gera o Bundle FHIR direto
  (LOINC pela memória do modelo); **gemini_ent** extrai trechos e passa pela MESMA ligação do pipeline.
  Respostas em cache em `results/gemini/` (rodar de novo não gasta cota). ~14 req/min, retry em 503, modelo fixo.
- `validar.py`: validador oficial HL7 (`tools/validator_cli.jar`, `-version 5.0`, terminologia via tx.fhir.org).
  Válido = sem issue `error`/`fatal`.
- `avaliar.py`: P/R/F1 por campo (ligado: exame/LOINC, valor, unidade, faixa, observação completa; trechos: exame,
  valor, unidade, faixa por texto normalizado), acurácia LOINC (pares pelo valor), vistos × não vistos, por layout e
  digital × escaneado, latência, chamadas e tokens; IC 95% por bootstrap (1000 reamostragens de laudos, seed 12345).

## Saídas (`results/`)
`campos_teste.csv`, `fhir_custo_teste.csv`, `vistos_naovistos_teste.csv`, `por_condicao_teste.csv`, `tabelas.tex`,
`f1_campos_teste.png/.pdf`, `exemplo_bundle.json` (Listagem 1), `validacao/`, `fhir/<método>/<conjunto>/`, `pred/`.
Os mesmos arquivos com sufixo `_dev` são do conjunto de desenvolvimento.

Latência: tempo de extração a partir do texto já extraído (a extração de texto/OCR é comum a todos os métodos e não entra).

## Regerar tabelas sem chamar a API do Gemini

As predições de todos os métodos já estão salvas em `results/pred/` e o cache do Gemini em `results/gemini/`. Para recalcular métricas, diferenças pareadas, `tabelas.tex` e figuras sem nenhuma chamada à API (e sem `GEMINI_API_KEY`):

```bash
cd src
../.venv/bin/python avaliar.py metricas teste   # e/ou: metricas dev
```

Rodar `avaliar.py rodar gemini_* ...` também reaproveita o cache e só chama a API para laudos ainda não processados.
