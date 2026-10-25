#!/usr/bin/env bash
# Reproduz tudo. Requisitos: python3, Java 17+, tesseract-ocr + tesseract-ocr-por, GEMINI_API_KEY (só se não houver cache).
# Validador FHIR fixado na versão 7.0.2 (resultados do artigo).
# Uso: ./run_all.sh [--sem-gemini]
set -euo pipefail; cd "$(dirname "$0")"
PY=.venv/bin/python
[ -x "$PY" ] || { python3 -m venv .venv && .venv/bin/pip install -r requirements.txt; }
[ -f tools/validator_cli.jar ] || { mkdir -p tools && curl -sSL -o tools/validator_cli.jar https://github.com/hapifhir/org.hl7.fhir.core/releases/download/7.0.2/validator_cli.jar; }
# 1) dados: dev (seed 1) é regenerável; o teste (seed 2026) é CONGELADO e só é conferido pelo hash.
[ -d data/dev ] || (cd src && ../$PY gerar_laudos.py dev 60 1)
[ -d data/teste ] || (cd src && ../$PY gerar_laudos.py teste 150 2026)
(cd data/teste && sha256sum -c --quiet SHA256SUMS) || { echo "ERRO: conjunto de teste difere do congelado"; exit 1; }
# 2) extratores (Gemini usa o cache em results/gemini/ se existir; sem cache faz chamadas a ~14 req/min)
# gliner_llm = gliner_hib + Gemini como reserva da ligação LOINC (cache em results/gemini/link/)
METODOS="regex gliner gliner_hib gliner_llm gemini_ent gemini_e2e"; LABBR="regex gliner_hib gliner_llm"
[ "${1:-}" = "--sem-gemini" ] && { METODOS="regex gliner gliner_hib"; LABBR="regex gliner_hib"; }
cd src
for c in dev teste; do for m in $METODOS; do ../$PY avaliar.py rodar $m $c > ../results/log_${m}_${c}.txt; done; done
# 3) validador oficial HL7 (R5) em cada Bundle
for c in dev teste; do for m in $METODOS; do ../$PY validar.py $m $c; done; done
# 2b) conjunto adicional lab_br (50 laudos, seed 2027; conferido pelo hash)
(cd ../data/adicional_lab_br && sha256sum -c --quiet SHA256SUMS) || { echo "ERRO: lab_br difere do congelado"; exit 1; }
for m in $LABBR; do ../$PY avaliar.py rodar $m adicional_lab_br > ../results/log_${m}_adicional_lab_br.txt; ../$PY validar.py $m adicional_lab_br; done
# 3b) sensibilidade da validade do gemini_e2e a pós-processamento (sem API): display do catálogo + UUIDs; + UCUM
if [ "${1:-}" != "--sem-gemini" ]; then
  ../$PY sensibilidade_e2e.py preparar teste
  for v in gemini_e2e_pp_display_uuid gemini_e2e_pp_ucum; do ../$PY validar.py $v teste; done
  ../$PY sensibilidade_e2e.py resumo teste
fi
# 4) métricas, IC 95% bootstrap, tabelas e figura
../$PY avaliar.py metricas dev > ../results/metricas_dev.txt
../$PY avaliar.py metricas teste > ../results/metricas_teste.txt
../$PY avaliar.py metricas adicional_lab_br > ../results/metricas_adicional_lab_br.txt
# 5) análises de erro: rótulos não vistos (tabela por família) e origem dos FP no lab_br
../$PY erros_nao_vistos.py teste; ../$PY erros_nao_vistos.py adicional_lab_br; ../$PY fp_lab_br.py
../$PY exemplo_bundle.py
cd .. && $PY -m pytest -q tests
