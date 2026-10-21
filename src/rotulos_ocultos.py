"""Rótulos NÃO VISTOS: gerado de data/variantes-reais-fontes.md (levantamento de fontes, 20/10/2026), só linhas com
fora_do_dicionario = sim (RDW-SD excluído: LOINC 21000-5, fora do catálogo). Usado SÓ pelo gerador no teste.
NUNCA importar em pipeline/extratores."""
OCULTOS = {
 "4544-3": [
  "Determinação do hematócrito"
 ],
 "789-8": [
  "Contagem de eritrócitos"
 ],
 "785-6": [
  "Hemoglobina corpuscular média"
 ],
 "786-4": [
  "Concentração de hemoglobina corpuscular média"
 ],
 "788-0": [
  "Amplitude de distribuição dos eritrócitos"
 ],
 "6690-2": [
  "Contagem de leucócitos"
 ],
 "777-3": [
  "Plaquetograma"
 ],
 "2345-7": [
  "Glicemia",
  "Glicose no soro",
  "Dosagem de glicose"
 ],
 "2160-0": [
  "Creatininemia",
  "Dosagem de creatinina",
  "CRE"
 ],
 "3091-6": [
  "URE",
  "Uréia no soro",
  "Dosagem de ureia"
 ],
 "2093-3": [
  "Colesterolemia",
  "Colesterol sérico",
  "Dosagem de colesterol total"
 ],
 "2571-8": [
  "TGL",
  "Dosagem de triglicerídeos"
 ],
 "2823-3": [
  "Calemia",
  "Kalemia",
  "Potássio no soro",
  "Dosagem de potássio"
 ],
 "2951-2": [
  "Natremia",
  "Sódio no soro",
  "Dosagem de sódio"
 ],
 "3016-3": [
  "Hormônio tireoestimulante",
  "Hormônio tirotrófico",
  "Tirotropina",
  "TSH ultra sensível"
 ],
 "1920-8": [
  "Transaminase glutâmico oxalacética",
  "Aspartato aminotransferase",
  "SGOT",
  "Transaminase glutâmico-oxaloacética"
 ],
 "1742-6": [
  "Transaminase glutâmico pirúvica",
  "Alanina aminotransferase",
  "SGPT"
 ]
}
P_OCULTO_TESTE = 0.35
