"""Catálogo de exames: nome, sinônimos, LOINC, display, UCUM, faixa de sorteio, referência, casas, unidades impressas.
LOINC dos 12 exames originais + 1558-6 conferidos pelo Scraper (paper-reic/loinc-verificacao.md, 20/10/2026);
789-8, 787-2, 785-6, 786-4, 788-0, 1920-8, 1742-6 conferidos depois (displays oficiais, 20/10/2026).
unidades impressas: (texto, fator) com valor_impresso = valor_canonico * fator.
ref: (low, high); low ou high = None => 'Até'/'<' ou '>'."""
EXAMES = [
    ("Hemoglobina", ["Hb", "HGB", "Dosagem de hemoglobina"], "718-7", "Hemoglobin [Mass/volume] in Blood", "g/dL", (9.0, 18.0), (12.0, 16.0), 1, [("g/dL", 1), ("g/dl", 1), ("g/ dL", 1)]),
    ("Hematócrito", ["Ht", "HCT"], "4544-3", "Hematocrit [Volume Fraction] of Blood by Automated count", "%", (28.0, 55.0), (36.0, 48.0), 1, [("%", 1)]),
    ("Hemácias", ["Eritrócitos", "RBC"], "789-8", "Erythrocytes [#/volume] in Blood by Automated count", "10*6/uL", (3.0, 6.5), (4.2, 5.4), 2, [("x10^6/µL", 1), ("milhões/mm³", 1)]),
    ("VCM", ["MCV", "Volume corpuscular médio"], "787-2", "MCV [Entitic mean volume] in Red Blood Cells by Automated count", "fL", (70.0, 105.0), (80.0, 100.0), 1, [("fL", 1), ("fl", 1)]),
    ("HCM", ["MCH"], "785-6", "MCH [Entitic mass] by Automated count", "pg", (24.0, 36.0), (27.0, 32.0), 1, [("pg", 1)]),
    ("CHCM", ["MCHC"], "786-4", "MCHC [Entitic Mass/volume] in Red Blood Cells by Automated count", "g/dL", (30.0, 37.0), (32.0, 36.0), 1, [("g/dL", 1), ("g/dl", 1)]),
    ("RDW", ["RDW-CV"], "788-0", "Erythrocyte [DistWidth] in Blood by Automated count", "%", (11.0, 18.0), (11.5, 14.5), 1, [("%", 1)]),
    ("Leucócitos", ["WBC", "Leucócitos - Global"], "6690-2", "Leukocytes [#/volume] in Blood by Automated count", "10*3/uL", (2.0, 18.0), (4.0, 11.0), 1, [("x10³/µL", 1), ("mil/mm³", 1), ("/mm³", 1000)]),
    ("Plaquetas", ["PLT", "Contagem de plaquetas"], "777-3", "Platelets [#/volume] in Blood by Automated count", "10*3/uL", (80.0, 500.0), (150.0, 450.0), 0, [("x10³/µL", 1), ("mil/mm³", 1), ("/mm³", 1000)]),
    ("Glicose", ["GLI"], "2345-7", "Glucose [Mass/volume] in Serum or Plasma", "mg/dL", (60.0, 250.0), (70.0, 99.0), 0, [("mg/dL", 1), ("mg/dl", 1)]),
    ("Glicemia de jejum", ["Glicose de jejum", "Glicose em jejum"], "1558-6", "Fasting glucose [Mass/volume] in Serum or Plasma", "mg/dL", (60.0, 250.0), (70.0, 99.0), 0, [("mg/dL", 1), ("mg/dl", 1)]),
    ("Creatinina", ["CREA"], "2160-0", "Creatinine [Mass/volume] in Serum or Plasma", "mg/dL", (0.4, 3.0), (0.6, 1.2), 2, [("mg/dL", 1), ("mg/dl", 1)]),
    ("Ureia", ["Uréia", "UR"], "3091-6", "Urea [Mass/volume] in Serum or Plasma", "mg/dL", (10.0, 90.0), (15.0, 45.0), 0, [("mg/dL", 1), ("mg/dl", 1)]),
    ("Colesterol total", ["CT", "Colesterol"], "2093-3", "Cholesterol [Mass/volume] in Serum or Plasma", "mg/dL", (120.0, 320.0), (None, 190.0), 0, [("mg/dL", 1), ("mg/dl", 1)]),
    ("Triglicerídeos", ["TG", "Triglicérides"], "2571-8", "Triglyceride [Mass/volume] in Serum or Plasma", "mg/dL", (40.0, 400.0), (None, 150.0), 0, [("mg/dL", 1), ("mg/dl", 1)]),
    ("Potássio", ["K"], "2823-3", "Potassium [Moles/volume] in Serum or Plasma", "mmol/L", (2.8, 6.5), (3.5, 5.1), 1, [("mmol/L", 1), ("mEq/L", 1)]),
    ("Sódio", ["Na"], "2951-2", "Sodium [Moles/volume] in Serum or Plasma", "mmol/L", (125.0, 155.0), (136.0, 145.0), 0, [("mmol/L", 1), ("mEq/L", 1)]),
    ("TSH", ["Tireotrofina"], "3016-3", "Thyrotropin [Units/volume] in Serum or Plasma", "u[IU]/mL", (0.1, 10.0), (0.4, 4.0), 2, [("µUI/mL", 1), ("mUI/L", 1)]),
    ("TGO", ["AST", "Transaminase oxalacética"], "1920-8", "Aspartate aminotransferase [Enzymatic activity/volume] in Serum or Plasma", "U/L", (8.0, 120.0), (None, 40.0), 0, [("U/L", 1)]),
    ("TGP", ["ALT", "Transaminase pirúvica"], "1742-6", "Alanine aminotransferase [Enzymatic activity/volume] in Serum or Plasma", "U/L", (5.0, 150.0), (None, 41.0), 0, [("U/L", 1)]),
]
POR_LOINC = {e[2]: e for e in EXAMES}
