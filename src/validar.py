"""Roda o validador oficial do HL7 (validator_cli.jar, -version 5.0) em todos os Bundles de um método/conjunto.
Válido = nenhuma issue com severidade error ou fatal. Saída: results/validacao/<metodo>_<conj>.csv (+ OperationOutcomes)."""
import json, sys, subprocess, pathlib, csv
BASE = pathlib.Path(__file__).parent.parent
JAR = BASE / "tools" / "validator_cli.jar"

def validar(metodo, conj):
    d = BASE / "results" / "fhir" / metodo / conj; arqs = sorted(d.glob("*.json"))
    out = BASE / "results" / "validacao"; out.mkdir(parents=True, exist_ok=True)
    oo = out / f"{metodo}_{conj}_operationoutcomes.json"
    cmd = ["java", "-jar", str(JAR), *map(str, arqs), "-version", "5.0", "-output", str(oo)]
    log = subprocess.run(cmd, capture_output=True, text=True)
    (out / f"{metodo}_{conj}.log").write_text(log.stdout[-20000:] + log.stderr[-5000:], encoding="utf-8")
    b = json.loads(oo.read_text(encoding="utf-8")); rs = [e["resource"] for e in b.get("entry", [])] if b.get("resourceType") == "Bundle" else [b]
    linhas = []
    for r in rs:
        f = next((x["valueString"] for x in r.get("extension", []) if x["url"].endswith("operationoutcome-file")), "?")
        erros = [i for i in r.get("issue", []) if i["severity"] in ("error", "fatal")]
        linhas.append([pathlib.Path(f).stem, int(not erros), len(erros),
                       " | ".join(sorted({i.get("details", {}).get("text", i.get("diagnostics", ""))[:150] for i in erros}))[:600]])
    with open(out / f"{metodo}_{conj}.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["doc", "valido", "n_erros", "erros"]); w.writerows(sorted(linhas))
    print(f"{metodo} {conj}: {sum(l[1] for l in linhas)}/{len(linhas)} válidos")

if __name__ == "__main__":
    validar(sys.argv[1], sys.argv[2])
