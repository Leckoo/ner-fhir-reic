# ner-fhir: laudos laboratoriais em PDF (pt-BR) → HL7 FHIR R5

Benchmark sintético de laudos laboratoriais em português e pipeline de extração (regex, GLiNER, GLiNER híbrido,
Gemini) com montagem de Bundles FHIR R5 e validação pelo validador oficial HL7.

## Instalação

Requisitos: Python 3.13, Java 17+ (validador HL7), `tesseract-ocr` e `tesseract-ocr-por` (OCR dos PDFs escaneados).

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

O `run_all.sh` baixa o validador HL7 7.0.2 para `tools/validator_cli.jar`. A chave do Gemini (`GEMINI_API_KEY`)
só é lida do ambiente (ou de um `.env` local, fora do repositório) e só é necessária para laudos sem resposta em cache.

## Uso

```bash
./run_all.sh               # tudo: extração, validação HL7, métricas, tabelas e figuras
./run_all.sh --sem-gemini  # só regex, GLiNER e GLiNER híbrido
.venv/bin/python -m pytest -q tests
```

Métodos individuais (a partir de `src/`): `../.venv/bin/python avaliar.py rodar <método> <conjunto>` e
`../.venv/bin/python validar.py <método> <conjunto>`, com método em `regex`, `gliner`, `gliner_hib`, `gliner_llm`,
`gemini_ent`, `gemini_e2e` e conjunto em `dev`, `teste`, `adicional_lab_br`.

## Dados

- `data/REGRAS_VARIACAO.md`: regras de geração dos laudos sintéticos (layouts, sinônimos, números, unidades, faixas,
  ruído de digitalização simulado).
- `data/variantes-reais-fontes.md` → `src/rotulos_ocultos.py`: rótulos fora do dicionário, usados só no teste.
- `data/fontes-referencias.md`: fontes públicas citadas (só links e citações).
- `data/layout-lab_br-estrutura.md`: estrutura do 5.º layout (`lab_br`).
- `data/dev/` (60 laudos, seed 1), `data/teste/` (150 laudos, seed 2026, congelado) e `data/adicional_lab_br/`
  (50 laudos, seed 2027). Todos os laudos são fictícios, gerados por código.

## Reprodução

Os conjuntos congelados são conferidos por hash (o `run_all.sh` não os regenera):

```bash
(cd data/teste && sha256sum -c SHA256SUMS)              # sha256 do SHA256SUMS: c3c25703cb5e0773d7002405bbb0f4c171563e0e33164cd8369b204600f31d79
(cd data/adicional_lab_br && sha256sum -c SHA256SUMS)   # sha256 do SHA256SUMS: 317bedf7b76095b7f2a55afdfb41766b04a7beebda2041703e97540015eac3b8
(cd data && sha256sum -c teste/REGRAS_SHA256)
(cd data/adicional_lab_br && sha256sum -c REGRAS_SHA256)
```

As predições estão em `results/pred/` e as respostas do Gemini em cache em `results/gemini/`. Para recalcular
métricas, IC 95% por bootstrap, diferenças pareadas, `results/tabelas*.tex` e figuras sem chamar a API:

```bash
cd src
../.venv/bin/python avaliar.py metricas teste
../.venv/bin/python avaliar.py metricas adicional_lab_br
../.venv/bin/python avaliar.py metricas dev
```

A conferência dos códigos e nomes LOINC usados é `python scripts/conferir_loinc.py` (tx.fhir.org), com saída em
`results/loinc_conferencia.csv`.

**Nota (26/10/2026).** Comentários de proveniência foram neutralizados em todo o histórico do repositório. Só
comentários mudaram (por isso os hashes em `REGRAS_SHA256` foram atualizados); as regras de geração e os conjuntos de
teste são os mesmos (os `SHA256SUMS` não mudaram).

## Citação

Se usar este código ou os dados, cite o artigo associado e este repositório:
https://github.com/Leckoo/ner-fhir-reic

## Licença

- Código: MIT (`LICENSE`), © 2026 Leonardo Antonio Patatt.
- Dados sintéticos (`data/`) e resultados (`results/`): CC-BY 4.0 (https://creativecommons.org/licenses/by/4.0/).
