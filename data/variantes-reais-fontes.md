# Variantes reais de nomes de exames (pt-BR) com fonte

Levantamento 20/10/2026 (horário de Brasília). Comparação com `src/exames.py` normalizada igual ao pipeline (minúsculas, sem acento). Só nomes que aparecem literalmente na fonte; nada derivado de erros da regex.
Excluídos de propósito: palavras-chave de busca do Fleury ("INFARTO DO MIOCARDIO, TGO", "Rim, creatinina"), exames derivados (CKD-EPI, TFG, lipidograma) e HbA1c (não está no exames.py; SIGTAP usa "DOSAGEM DE HEMOGLOBINA GLICOSILADA", 02.02.01.050-3).

| exame | variante | fonte | trecho | fora_do_dicionario |
|---|---|---|---|---|
| Hemoglobina | Hemoglobina | referencias-reais/modelo_laudo_hematologia_trabalhosgratuitos.txt | "Hemoglobina:  14,4  g/dL" | não |
| Hemoglobina | HGB | referencias-reais/pop_hemograma_hcuftm.txt (HC-UFTM/Ebserh; URL no README) | "Hemoglobina: HGB dentro de ±2%" | não |
| Hemoglobina | HB | referencias-reais/pop_hemograma_hcuftm.txt (HC-UFTM/Ebserh; URL no README) | "HB (g/dL) 13.5-22.0 / Hemoglobina (HB) <7,0 g/dL" | não |
| Hemoglobina | Dosagem de hemoglobina | referencias-reais/pop_hemograma_hcuftm.txt (HC-UFTM/Ebserh; URL no README) | "dosagem de hemoglobina" | não |
| Hematócrito | Hematócrito | referencias-reais/modelo_laudo_hematologia_trabalhosgratuitos.txt | "Hematócrito: 42,4 %" | não |
| Hematócrito | HCT | referencias-reais/pop_hemograma_hcuftm.txt (HC-UFTM/Ebserh; URL no README) | "Hematócrito: HCT dentro de ±3%" | não |
| Hematócrito | HT | referencias-reais/pop_hemograma_hcuftm.txt (HC-UFTM/Ebserh; URL no README) | "HT (%) 42 - 60" | não |
| Hematócrito | Determinação do hematócrito | referencias-reais/pop_hemograma_hcuftm.txt (HC-UFTM/Ebserh; URL no README) | "determinação do hematócrito" | sim |
| Hemácias | Hemácias | referencias-reais/modelo_laudo_hematologia_trabalhosgratuitos.txt | "Hemácias: 4,47 milhões/mm3" | não |
| Hemácias | RBC | referencias-reais/pop_hemograma_hcuftm.txt (HC-UFTM/Ebserh; URL no README) | "Hemácias (RBC) 0,0 – 7,0 x 106/μl" | não |
| Hemácias | Contagem de eritrócitos | referencias-reais/pop_hemograma_hcuftm.txt (HC-UFTM/Ebserh; URL no README) | "contagem de eritrócitos, dosagem de hemoglobina" | sim |
| VCM | VCM | referencias-reais/modelo_laudo_hematologia_trabalhosgratuitos.txt | "VCM: 94,9 fL" | não |
| VCM | Volume corpuscular médio | referencias-reais/pop_hemograma_hcuftm.txt (HC-UFTM/Ebserh; URL no README) | "volume corpuscular médio (VCM)" | não |
| HCM | HCM | referencias-reais/modelo_laudo_hematologia_trabalhosgratuitos.txt | "HCM 32,2 pg" | não |
| HCM | Hemoglobina corpuscular média | referencias-reais/pop_hemograma_hcuftm.txt (HC-UFTM/Ebserh; URL no README) | "hemoglobina corpuscular média (HCM)" | sim |
| CHCM | CHCM | referencias-reais/modelo_laudo_hematologia_trabalhosgratuitos.txt | "CHCM: 34,0 g/dL" | não |
| CHCM | Concentração de hemoglobina corpuscular média | referencias-reais/pop_hemograma_hcuftm.txt (HC-UFTM/Ebserh; URL no README) | "concentração de hemoglobina corpuscular média (CHCM)" | sim |
| RDW | RDW | referencias-reais/modelo_laudo_hematologia_trabalhosgratuitos.txt | "RDW: 12,9 %" | não |
| RDW | RDW-CV | referencias-reais/pop_hemograma_hcuftm.txt (HC-UFTM/Ebserh; URL no README) | "RDW-CV > 15,9 fL Anisocitose" | não |
| RDW | RDW-SD | referencias-reais/pop_hemograma_hcuftm.txt (HC-UFTM/Ebserh; URL no README) | "RDW-SD > 55,0 fL Anisocitose (obs.: RDW-SD é outro LOINC, 21000-5)" | sim |
| RDW | Amplitude de distribuição dos eritrócitos | referencias-reais/pop_hemograma_hcuftm.txt (HC-UFTM/Ebserh; URL no README) | "amplitude de distribuição dos eritrócitos (RDW)" | sim |
| Leucócitos | Leucócitos - Global | referencias-reais/modelo_laudo_hematologia_trabalhosgratuitos.txt | "Leucócitos - Global: 3.800 /mm3" | não |
| Leucócitos | WBC | referencias-reais/pop_hemograma_hcuftm.txt (HC-UFTM/Ebserh; URL no README) | "Leucócitos (WBC) <1,00 x 10³/ μl" | não |
| Leucócitos | Contagem de leucócitos | referencias-reais/pop_hemograma_hcuftm.txt (HC-UFTM/Ebserh; URL no README) | "contagem de leucócitos e fórmula leucocitária" | sim |
| Plaquetas | Plaquetas | referencias-reais/pop_hemograma_hcuftm.txt (HC-UFTM/Ebserh; URL no README) | "Plaquetas (PLT) <20,00 x 10³/ μl" | não |
| Plaquetas | PLT | referencias-reais/pop_hemograma_hcuftm.txt (HC-UFTM/Ebserh; URL no README) | "PLT < 150 x 103 Trombocitopenia" | não |
| Plaquetas | Contagem de plaquetas | SIGTAP 02.02.02 (mesma URL) | "02.02.02.002-9 CONTAGEM DE PLAQUETAS" | não |
| Plaquetas | Plaquetograma | DB Diagnósticos https://gde.diagnosticosdobrasil.com.br/exam/PLAQ | "PLAQ - CONTAGEM DE PLAQUETAS | Sinônimos: CBHPM 4030436, PLAQUETOGRAMA" | sim |
| Glicose | Glicemia | Fleury https://www.fleury.com.br/exames/glicose-soro (cópia: referencias-reais/fleury/glicose-soro.txt) | "Outros nomes: GLICEMIA., GLICOSE NO SORO., GLICEMIA DE JEJUM." | sim |
| Glicose | Glicose no soro | Fleury https://www.fleury.com.br/exames/glicose-soro (cópia: referencias-reais/fleury/glicose-soro.txt) | "GLICOSE NO SORO." | sim |
| Glicose | Dosagem de glicose | SIGTAP 02.02.01 (https://www.itapetininga.sp.gov.br/licitacao/download/2202/) | "02.02.01.047-3 DOSAGEM DE GLICOSE" | sim |
| Glicemia de jejum | Glicemia de jejum | Fleury https://www.fleury.com.br/exames/glicose-soro (cópia: referencias-reais/fleury/glicose-soro.txt) | "GLICEMIA DE JEJUM." | não |
| Creatinina | Creatininemia | Fleury https://www.fleury.com.br/exames/creatinina-soro (cópia: referencias-reais/fleury/creatinina-soro.txt) | "Outros nomes: Creatinina, Creatininemia, Dosagem de creatinina, ..., CRE, CREA" | sim |
| Creatinina | Dosagem de creatinina | SIGTAP 02.02.01 (https://www.itapetininga.sp.gov.br/licitacao/download/2202/) | "02.02.01.031-7 DOSAGEM DE CREATININA" | sim |
| Creatinina | CRE | Fleury https://www.fleury.com.br/exames/creatinina-soro (cópia: referencias-reais/fleury/creatinina-soro.txt) | "CRE, CREA" | sim |
| Creatinina | CREA | Fleury https://www.fleury.com.br/exames/creatinina-soro (cópia: referencias-reais/fleury/creatinina-soro.txt) | "CRE, CREA" | não |
| Ureia | Uréia | Fleury https://www.fleury.com.br/exames/ureia-soro (cópia: referencias-reais/fleury/ureia-soro.txt) | "Dosagem uréia soro, ..., Uréia plasma, URE, Azotemia, Uréia no soro" | não |
| Ureia | URE | Fleury https://www.fleury.com.br/exames/ureia-soro (cópia: referencias-reais/fleury/ureia-soro.txt) | "URE" | sim |
| Ureia | Uréia no soro | Fleury https://www.fleury.com.br/exames/ureia-soro (cópia: referencias-reais/fleury/ureia-soro.txt) | "Uréia no soro" | sim |
| Ureia | Dosagem de ureia | SIGTAP 02.02.01 (https://www.itapetininga.sp.gov.br/licitacao/download/2202/) | "02.02.01.069-4 DOSAGEM DE UREIA" | sim |
| Colesterol total | Colesterol total | Fleury https://www.fleury.com.br/exames/colesterol-soro (cópia: referencias-reais/fleury/colesterol-soro.txt) | "Outros nomes: Colesterol, Colesterolemia, Colesterol total, Colesterol sérico, ..." | não |
| Colesterol total | Colesterolemia | Fleury https://www.fleury.com.br/exames/colesterol-soro (cópia: referencias-reais/fleury/colesterol-soro.txt) | "Colesterolemia" | sim |
| Colesterol total | Colesterol sérico | Fleury https://www.fleury.com.br/exames/colesterol-soro (cópia: referencias-reais/fleury/colesterol-soro.txt) | "Colesterol sérico" | sim |
| Colesterol total | Dosagem de colesterol total | SIGTAP 02.02.01 (https://www.itapetininga.sp.gov.br/licitacao/download/2202/) | "02.02.01.029-5 DOSAGEM DE COLESTEROL TOTAL" | sim |
| Triglicerídeos | Triglicérides | Fleury https://www.fleury.com.br/exames/triglicerides-soro (cópia: referencias-reais/fleury/triglicerides-soro.txt) | "Outros nomes: TRIGLICERIDES, TGL, TRIGLICERIDEOS SORO, ..." | não |
| Triglicerídeos | TGL | Fleury https://www.fleury.com.br/exames/triglicerides-soro (cópia: referencias-reais/fleury/triglicerides-soro.txt) | "TGL" | sim |
| Triglicerídeos | Dosagem de triglicerídeos | SIGTAP 02.02.01 (https://www.itapetininga.sp.gov.br/licitacao/download/2202/) | "02.02.01.067-8 DOSAGEM DE TRIGLICERIDEOS" | sim |
| Potássio | Calemia | Fleury https://www.fleury.com.br/exames/potassio-soro (cópia: referencias-reais/fleury/potassio-soro.txt) | "Outros nomes: Calemia, Kalemia, Potássio no soro, K no soro" | sim |
| Potássio | Kalemia | Fleury https://www.fleury.com.br/exames/potassio-soro (cópia: referencias-reais/fleury/potassio-soro.txt) | "Kalemia" | sim |
| Potássio | Potássio no soro | Fleury https://www.fleury.com.br/exames/potassio-soro (cópia: referencias-reais/fleury/potassio-soro.txt) | "Potássio no soro" | sim |
| Potássio | Dosagem de potássio | SIGTAP 02.02.01 (https://www.itapetininga.sp.gov.br/licitacao/download/2202/) | "02.02.01.060-0 DOSAGEM DE POTASSIO" | sim |
| Sódio | Natremia | Fleury https://www.fleury.com.br/exames/sodio-soro (cópia: referencias-reais/fleury/sodio-soro.txt) | "Outros nomes: Sódio, Natremia, Sódio no soro, ..., NA serico, NA soro" | sim |
| Sódio | Sódio no soro | Fleury https://www.fleury.com.br/exames/sodio-soro (cópia: referencias-reais/fleury/sodio-soro.txt) | "Sódio no soro" | sim |
| Sódio | Dosagem de sódio | SIGTAP 02.02.01 (https://www.itapetininga.sp.gov.br/licitacao/download/2202/) | "02.02.01.063-5 DOSAGEM DE SODIO" | sim |
| TSH | Hormônio tireoestimulante | Fleury https://www.fleury.com.br/exames/hormonio-tireoestimulante-soro (cópia: referencias-reais/fleury/hormonio-tireoestimulante-soro.txt) | "Hormônio Tireoestimulante, HORMONIO TIREOTROFICO, ..., TIROTROPINA" | sim |
| TSH | Hormônio tirotrófico | Fleury https://www.fleury.com.br/exames/hormonio-tireoestimulante-soro (cópia: referencias-reais/fleury/hormonio-tireoestimulante-soro.txt) | "Hormônio Tirotrófico / HORMONIO TIREOTROFICO" | sim |
| TSH | Tirotropina | Fleury https://www.fleury.com.br/exames/hormonio-tireoestimulante-soro (cópia: referencias-reais/fleury/hormonio-tireoestimulante-soro.txt) | "TIROTROPINA" | sim |
| TSH | TSH ultra sensível | Fleury https://www.fleury.com.br/exames/hormonio-tireoestimulante-soro (cópia: referencias-reais/fleury/hormonio-tireoestimulante-soro.txt) | "TSH ultra sensível" | sim |
| TGO | Transaminase glutâmico oxalacética | Fleury https://www.fleury.com.br/exames/transaminase-glutamico-oxalacetica-soro (cópia: referencias-reais/fleury/transaminase-glutamico-oxalacetica-soro.txt) | "Outros nomes: TGO, Transaminase glutâmico oxalacética, TGO sérico, ..., AST, Aspartato aminotransferase" | sim |
| TGO | Aspartato aminotransferase | Fleury https://www.fleury.com.br/exames/transaminase-glutamico-oxalacetica-soro (cópia: referencias-reais/fleury/transaminase-glutamico-oxalacetica-soro.txt) | "Aspartato aminotransferase" | sim |
| TGO | SGOT | Fleury https://www.fleury.com.br/exames/transaminase-glutamico-oxalacetica-soro (cópia: referencias-reais/fleury/transaminase-glutamico-oxalacetica-soro.txt) | "Sgot TGO" | sim |
| TGO | Transaminase glutâmico-oxaloacética | DB Diagnósticos https://gde.diagnosticosdobrasil.com.br/exam/TGO | "também conhecida como Transaminase glutâmico-oxaloacética (TGO)" | sim |
| TGO | AST | Fleury https://www.fleury.com.br/exames/transaminase-glutamico-oxalacetica-soro (cópia: referencias-reais/fleury/transaminase-glutamico-oxalacetica-soro.txt) | "AST" | não |
| TGP | Transaminase glutâmico pirúvica | Fleury https://www.fleury.com.br/exames/transaminase-glutamico-piruvica-soro (cópia: referencias-reais/fleury/transaminase-glutamico-piruvica-soro.txt) | "Outros nomes: TGP, Transaminase glutâmico pirúvica, SGPT, Alanina aminotransferase, ALT, ..." | sim |
| TGP | Alanina aminotransferase | Fleury https://www.fleury.com.br/exames/transaminase-glutamico-piruvica-soro (cópia: referencias-reais/fleury/transaminase-glutamico-piruvica-soro.txt) | "Alanina aminotransferase" | sim |
| TGP | SGPT | Fleury https://www.fleury.com.br/exames/transaminase-glutamico-piruvica-soro (cópia: referencias-reais/fleury/transaminase-glutamico-piruvica-soro.txt) | "SGPT" | sim |
| TGP | ALT | Fleury https://www.fleury.com.br/exames/transaminase-glutamico-piruvica-soro (cópia: referencias-reais/fleury/transaminase-glutamico-piruvica-soro.txt) | "ALT" | não |

## Contagem

| exame | variantes | fora |
|---|---|---|
| Hemoglobina | 4 | 0 |
| Hematócrito | 4 | 1 |
| Hemácias | 3 | 1 |
| VCM | 2 | 0 |
| HCM | 2 | 1 |
| CHCM | 2 | 1 |
| RDW | 4 | 2 |
| Leucócitos | 3 | 1 |
| Plaquetas | 4 | 1 |
| Glicose | 3 | 3 |
| Glicemia de jejum | 1 | 0 |
| Creatinina | 4 | 3 |
| Ureia | 4 | 3 |
| Colesterol total | 4 | 3 |
| Triglicerídeos | 3 | 2 |
| Potássio | 4 | 4 |
| Sódio | 3 | 3 |
| TSH | 4 | 4 |
| TGO | 5 | 4 |
| TGP | 4 | 3 |
| **total** | 67 | 40 |
