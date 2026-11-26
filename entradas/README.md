# Entradas

Datos crudos de la CNBV. No se versionan (ver `.gitignore`).

## Estructura esperada

- `BE BM YYYYMM.xlsx`: boletín electrónico de Banca Múltiple (hojas
  `Evaluación Calidad Detallada`, `Indicadores`, etc.).
- `tablero/sh_datos_csv_40_i/040_TO.csv`: tablero de información financiera.
- `tablero/sh_datos_csv_40_i/catalogo_conceptos_040.xlsx`
- `tablero/sh_datos_csv_40_i/catalogo_instituciones_040.csv`
- `ICAP_BM_YYYYMM.pdf`: indicadores de capitalización de Banco de México para los
  54 bancos y el Total Banca Múltiple (ICAP, CCB, CCF y categoría de alertas
  tempranas). El mes del corte se toma del nombre del archivo; con
  `ICAP_BM_202609.pdf` el corte es septiembre de 2026. La ruta por defecto está
  en `config.PDF_ICAP` y se sobreescribe con `--pdf-icap RUTA`.

## Notas de liquidez

- **CCL/LCR** = Cobertura de Liquidez = activos líquidos de alta calidad /
  salidas netas de efectivo a 30 días.
- **CFEN/NSFR** = Financiamiento Estable Neto = financiación estable disponible /
  financiación estable requerida a 1 año.
- Se publican solo en cierres trimestrales (mar/jun/sep/dic), con desfase de un
  trimestre. Último dato disponible en el tablero: `202606` → `n.d.` en
  septiembre de 2026.