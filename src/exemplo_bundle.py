"""Gera results/exemplo_bundle.json (Listagem 1): Bundle do gabarito de um laudo do teste, com referenceRange."""
import json, pathlib
from pipeline import para_fhir
B = pathlib.Path(__file__).parent.parent
g = json.loads((B / "data" / "teste" / "laudo_000.json").read_text())
b = para_fhir({**g, "observacoes": g["observacoes"][:2]}, "laudo_000")
(B / "results" / "exemplo_bundle.json").write_text(json.dumps(b, ensure_ascii=False, indent=2))
