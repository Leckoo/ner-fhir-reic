# Referências reais para as regras de variação dos laudos sintéticos

Levantamento feito em 20/10/2026 (horário de Brasília). Só entraram fontes públicas. Nenhum dado de paciente real foi baixado.
Legenda: **[V]** verificado no texto da fonte; **[?]** incerto, ou visto só em trecho de busca.

## 1. Arquivos nesta pasta

| Arquivo | Fonte (URL) | Licença/termos | O que mostra |
|---|---|---|---|
| `pop_hemograma_hcuftm.pdf` / `.txt` | https://www.gov.br/hubrasil/pt-br/hospitais-universitarios/regiao-sudeste/hc-uftm/documentos/procedimentos-e-rotinas-operacionais-padrao/pops/POP.HCUFTMUACAP.004RealizacaodeHemogramanoServicoLaboratorialdeHematologiaversao2.pdf | Documento público do governo (Ebserh/HC-UFTM). Não traz licença explícita **[?]**. Citar sem redistribuir fora do projeto. | POP de hemograma de hospital universitário. Siglas (VCM, HCM, CHCM, RDW, RDW-SD/CV, HGB, PLT, NRBC, RET), unidades (g/dL, g/dl, fL, fl, x 10³/μL, x 106/μL, mmol/L, mm3) e tabela de valores de referência por faixa etária (Tabela 4). Mistura vírgula e ponto decimal ("30.00", "0,20"). **[V]** |
| `rdc_978_2025_anvisa.pdf` / `.txt` | https://visa.jundiai.sp.gov.br/wp-content/uploads/2025/06/RDC-No-978_2025-funcionamento-das-EAC.pdf (cópia do DOU) | Norma federal. Ato oficial, sem proteção de direito autoral (Lei 9.610/98, art. 8º, IV). | Arts. 166–167: campos **obrigatórios** do laudo (CNES, endereço, RT e conselho, paciente, idade/DN, data de coleta, exame, material, método, resultado com unidade, valores de referência, data de emissão, assinatura). Serve de base para o cabeçalho e o rodapé sintéticos. **[V]** |
| `modelo_laudo_hematologia_trabalhosgratuitos.txt` | https://www.trabalhosgratuitos.com/Biol%C3%B3gicas/Bioqu%C3%ADmica/Modelo-de-Laudo-de-Laborat%C3%B3rio-de-An%C3%A1lises-Cl%C3%ADnicas-1110330.html | Texto de usuário (2016) em site de trabalhos. Sem licença clara **[?]**. Aqui ficou só um trecho para análise. Paciente fictícia ("Maria da Silva"). | Modelo de laudo de hemograma completo em colunas alinhadas por espaços: Resultado, unidade, Valores de Referência; leucograma com % e /mm3 lado a lado; "Até 500"; "4,20 a 5,40". **[V]** |

## 2. Fontes consultadas mas NÃO baixadas (têm dados reais de pacientes)

Laudos reais de Dasa, Hermes Pardini, GSE/Laboratório Carvalho e outros foram postados no Scribd com nome, CPF, RG e endereço dos pacientes. Pela LGPD, **não foram baixados**, e as URLs não estão listadas aqui. Só as observações de layout, sem nenhum dado pessoal, foram anotadas abaixo como "[?] observado em trecho de busca". Não as use como fonte citável no artigo.

Não encontrei modelos/exemplos oficiais de laudo publicados por Fleury, Dasa, Pardini ou Sabin. Também não encontrei um template de laudo do GAL/LACEN. O manual do LACEN-PA (http://www.saude.pa.gov.br/wp-content/uploads/2022/03/MANUAL-DE-COLETA-DBM_4%C2%B0-Ed_2021.pdf) só diz que os resultados saem pelo sistema GAL, e o download estourou o tempo limite.

## 3. LOINC pt-BR

- A tradução existe: variante linguística **pt-BR, LOINC LV ID 11**, feita pelo **Instituto HL7 Brasil**. Fonte: https://loinc.org/translations/pt-br e https://loinc.org/international **[V via busca; loinc.org retornou 403 ao curl]**
- O arquivo é `AccessoryFiles/LinguisticVariants/ptBR11LinguisticVariant.csv`, que vem no `Loinc_2.82.zip` (lançado em 04/03/2026). O download é gratuito, mas **exige login LOINC gratuito**: http://loinc.org/downloads/accessory-files/ **[V]**
- Também dá para acessar pela Search API (`language=11`, com autenticação) e pelo FHIR Terminology Service do LOINC (designations).
- Licença: termos de uso do LOINC (arquivo `LoincLicense_5.8.txt` no zip). É gratuita e permite uso em pesquisa com atribuição. **[?] Ler o texto da licença antes de redistribuir trechos do CSV no repositório público.** O CSV não foi baixado porque precisa da conta do usuário.

## 4. Sinônimos, abreviações e unidades (vistos nas fontes)

| Conceito (LOINC sugerido **[?]** conferir) | Variações no texto | Unidades vistas | Fonte |
|---|---|---|---|
| Hemoglobina (718-7) | Hemoglobina; HB; HGB; "DOSAGEM DA HEMOGLOBINA" **[?]** | g/dL, g/dl, g/ dL, mmol/L | POP UFTM [V]; modelo [V]; trecho Dasa [?] |
| Hemácias / eritrócitos (789-8) | Hemácias; Eritrócitos; RBC; "CONTAGEM DE HEMACIAS" [?] | milhões/mm3, x 10⁶/μL (às vezes "x 106/μL" na extração), 10^6/µL, u³ (erro) [?], 5.400.000/mm3 [?] | POP [V]; modelo [V] |
| Hematócrito (4544-3) | Hematócrito; HCT/Ht [?]; "AVALIACAO DO HEMATOCRITO" [?] | % | modelo [V] |
| VCM (787-2) | VCM; VGM [?]; "VOLUME GLOBULAR MEDIO" [?]; MCV | fL, fl, pL (erro) [?] | POP [V]; modelo [V] |
| HCM (785-6) | HCM; HGM [?]; MCH | pg | POP [V]; modelo [V] |
| CHCM (786-4) | CHCM; CHGM [?]; MCHC | g/dL, % (em alguns laudos) [?] | POP [V]; modelo [V] |
| RDW (788-0) | RDW; RDW-CV; RDW-SD; "INDICE DE ANISOCITOSE (RDW)" [?] | %, fL | POP [V]; modelo [V] |
| Leucócitos (6690-2) | Leucócitos; "Leucócitos - Global"; WBC | /mm3, /mm³, /µL, mil/mm3 [?], x 10³/μL | POP [V]; modelo [V] |
| Diferencial | Segmentados, Bastonetes/Bastões [?], Linfócitos (típicos/atípicos) [?], Monócitos, Eosinófilos, Basófilos, Mielócitos, Metamielócitos | % **e** absoluto na mesma linha | modelo [V] |
| Plaquetas (777-3) | Plaquetas; PLT; "CONTAGEM DE PLAQUETAS" [?] | /mm3, mil/mm3 [?], x 10³/μL | POP [V] |
| Glicose, creatinina, TGO/AST, TGP/ALT, GGT, ureia/uréia | "Transaminase oxalacética - TGO (Aspartato amino transferase)", "Uréia" (grafia antiga) [?] | — | trecho de laudo Dasa [?] |

### Formatos de número e de referência
- Vírgula decimal ("14,4") e ponto de milhar ("3.800", "10.240") [V modelo]. Também aparece ponto decimal ("30.00", "13.5-22.0") [V POP].
- Intervalos escritos como "4,20 a 5,40" [V], "12 - 15.5" [V POP], "0,0 – 22,5" [V POP], "Até 500" [V], "< 11,0" e "> 100,0" [V POP], "ATE 840/mm3" sem acento, em caixa alta [?].
- Referência estratificada por sexo (colunas Homens/Mulheres) [?] ou por faixa etária (Tabela 4 do POP) [V].
- Texto sem acento e em CAIXA ALTA, típico de sistema legado [?]. Separador "Nome :valor" [?].

## 5. Padrões de layout observados

1. **Colunas alinhadas por espaço** (texto monoespaçado): Analito | Resultado | Unidade | Referência. [V modelo]
2. **Tabela com cabeçalho** RESULTADO / INTERVALO DE REFERÊNCIA e legenda de cores (abaixo/dentro/acima) [?].
3. **Leucograma em duas subcolunas** (relativo % e absoluto /mm3), cada uma com a sua referência. [V modelo]
4. **Bloco por exame:** título (HEMOGRAMA COMPLETO), depois "Material:", "Método:" e "Coletado em/Liberado em". [V modelo; exigido pela RDC 978, art. 167 V-VIII]
5. **Cabeçalho repetido em cada página** (laboratório, CNES, RT, paciente, solicitante) e **rodapé** com assinatura digital, hash ou QR code, "Pág. 1 de 9" e aviso de interpretação médica [? trechos; campos exigidos pela RDC 978 V].
6. Laudo com **vários exames e páginas** (hemograma + bioquímica) [?]. Em uma página, a tabela de referência vem separada no fim do bloco (Dasa) [?].
7. Escaneado/foto: não encontrei exemplo público sem dados pessoais. **Recomendação:** simular com ruído (rotação, blur, JPEG) e marcar como hipótese.

## 6. Datasets relacionados (para trabalhos relacionados, não para laudos)
- SemClinBr / BioBERTpt NER Laboratory: https://huggingface.co/pucpr/clinicalnerpt-laboratory (narrativas clínicas, não PDFs de laudo).
- AnonyMED-BR: https://github.com/venturusbr/AnonyMED-BR (anonimização; 1.887 registros sintéticos).
- Neuralmed: https://github.com/tayh/neuralmed (laudos radiológicos em texto) [? origem e licença dos dados não verificadas].
- LIAAD/ER_NER: https://github.com/LIAAD/ER_NER (notas sintéticas de pronto-socorro, PT-PT/PT? [?]).
Nenhum deles traz PDFs de laudos laboratoriais brasileiros. Pelo que encontrei, isso é uma lacuna que reforça a contribuição do benchmark.
