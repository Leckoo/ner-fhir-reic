"""Prova de que o ajuste pós-hoc do cabeçalho em grade não mexe no teste congelado (150 laudos).
Reextrai em memória (sem gravar nada) regex, GLiNER+regras e reserva LLM (cache; sem chave = nenhuma chamada nova)
a partir dos textos gravados e compara, laudo a laudo, (i) a extração com results/pred/<m>_<conj>.json (sem latência)
e (ii) o Bundle serializado, byte a byte, com results/fhir/<m>/<conj>/*.json.
  python conferir_teste_inalterado.py [conj] [metodos...]"""
import json, sys
from pipeline import extrair_regex
from avaliar import RES, docs, gliner_llm

META = {"latencia_s", "chamadas", "tokens", "modelo"}
def conferir(m, conj):
    preds = json.loads((RES / "pred" / f"{m}_{conj}.json").read_text(encoding="utf-8")); ok_e = ok_b = 0
    from pipeline import para_fhir
    for pdf in docs(conj):
        i = pdf.stem; texto = (RES / "texto" / conj / f"{i}.txt").read_text(encoding="utf-8")
        if m == "regex": ext = extrair_regex(texto)
        elif m == "gliner_hib":
            from extrator_gliner import extrair_gliner_hib; ext = extrair_gliner_hib(texto)
        else: ext, _ = gliner_llm(texto, i, conj)
        ok_e += json.loads(json.dumps(ext, ensure_ascii=False)) == {k: v for k, v in preds[i].items() if k not in META}
        ok_b += json.dumps(para_fhir(ext, i), ensure_ascii=False, indent=1) == (RES / "fhir" / m / conj / f"{i}.json").read_text(encoding="utf-8")
    n = len(preds); print(f"{m} {conj}: extração idêntica {ok_e}/{n}; Bundle idêntico byte a byte {ok_b}/{n}"); return ok_e == ok_b == n

if __name__ == "__main__":
    conj = sys.argv[1] if len(sys.argv) > 1 else "teste"
    r = [conferir(m, conj) for m in (sys.argv[2:] or ["regex", "gliner_hib", "gliner_llm"])]
    sys.exit(0 if all(r) else 1)
