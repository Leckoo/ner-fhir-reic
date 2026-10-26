"""Confere os 20 códigos LOINC do catálogo (src/exames.py) no servidor de terminologia tx.fhir.org.

Uso: python scripts/conferir_loinc.py  -> grava results/loinc_conferencia.csv
Para cada código chama CodeSystem/$lookup (system=http://loinc.org) e compara o display oficial
com o display usado no catálogo. Só lê; não altera dados nem resultados."""
import csv, json, sys, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
from exames import EXAMES  # noqa: E402

TX = "https://tx.fhir.org/r5/CodeSystem/$lookup"

def lookup(code):
    q = urllib.parse.urlencode({"system": "http://loinc.org", "code": code})
    req = urllib.request.Request(f"{TX}?{q}", headers={"Accept": "application/fhir+json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        p = json.load(r)
    d = {x["name"]: x.get("valueString") for x in p.get("parameter", []) if "valueString" in x}
    return d.get("display"), d.get("version")

def main():
    linhas, ok = [], 0
    for e in EXAMES:
        code, disp = e[2], e[3]
        try:
            oficial, versao = lookup(code)
        except Exception as ex:  # código inexistente ou falha de rede
            oficial, versao = f"ERRO: {ex}", ""
        igual = oficial == disp
        ok += igual
        linhas.append([e[0], code, disp, oficial, versao, "sim" if igual else "nao"])
    out = RAIZ / "results" / "loinc_conferencia.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["exame", "loinc", "display_catalogo", "display_tx_fhir_org", "versao_loinc", "confere"])
        w.writerows(linhas)
    print(f"{ok}/{len(linhas)} códigos com display igual ao oficial; consulta em "
          f"{datetime.now(timezone.utc).isoformat(timespec='seconds')} -> {out}")
    return 0 if ok == len(linhas) else 1

if __name__ == "__main__":
    sys.exit(main())
