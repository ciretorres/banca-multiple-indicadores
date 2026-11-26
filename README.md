# banca-multiple-indicadores

Generador del libro Excel de indicadores de la Banca Múltiple supervisada por la CNBV.

## Uso

```bash
.venv/bin/python generar_banca_multiple.py
.venv/bin/python generar_banca_multiple.py --out RUTA
.venv/bin/python generar_banca_multiple.py --pdf-icap RUTA
python -m banca_multiple
.venv/bin/python generar_banca_multiple.py --help
```

En Windows usar `.venv\Scripts\python.exe` en lugar de `.venv/bin/python`
(equivalente en esta sección y en la siguiente).

## Libro compañero para Copilot

`generar_vista_copilot.py` crea
`salidas/Bancos_Multiples_Cortes_Trimestrales.xlsx`: una vista compacta para que
Copilot Cloud lea los indicadores completos. Tiene los 7 cortes trimestrales
(`2025 Q1` a `2026 Q3`) con 54 bancos cada uno y los 11 indicadores escritos como
valores (números o `n.d.`/`n.a.`), sin fórmulas ni celdas vacías por falta de
valor cacheado; termina con una hoja `Leyenda`. El libro principal no se modifica.

```bash
.venv/bin/python generar_vista_copilot.py
.venv/bin/python generar_vista_copilot.py --out RUTA
.venv/bin/python generar_vista_copilot.py --help
```

En Windows: `.venv\Scripts\python.exe generar_vista_copilot.py` (ídem para las
variantes `--out RUTA` y `--help`).

## Verificación

```bash
.venv/bin/pytest
.venv/bin/pyflakes banca_multiple/ tests generar_banca_multiple.py generar_vista_copilot.py
.venv/bin/python scripts/comparar.py --xlsx-a A --xlsx-b B
```

## Fuentes

- `entradas/BE BM 202609.xlsx`
- `entradas/tablero/sh_datos_csv_40_i/040_TO.csv`
- `entradas/ICAP_BM_YYYYMM.pdf`: indicadores de capitalización de Banco de México
  (ICAP, CCB, CCF y categoría de alertas tempranas). La ruta está en
  `config.PDF_ICAP` y se puede sobreescribir con `--pdf-icap RUTA`. El mes del
  corte se deriva del nombre del archivo: con `ICAP_BM_202608.pdf`, las columnas
  nuevas de `Datos Fuente` (`CCB`, `CCF`, `Categoría`) llevan dato en agosto de
  2026 y `n.d.` en los demás meses.

Notas de liquidez:

- **CCL/LCR** = Cobertura de Liquidez = activos líquidos de alta calidad /
  salidas netas de efectivo a 30 días.
- **CFEN/NSFR** = Financiamiento Estable Neto = financiación estable disponible /
  financiación estable requerida a 1 año.
- Se publican solo en cierres trimestrales (mar/jun/sep/dic), con desfase de un
  trimestre. Último dato disponible en el tablero: `202606` → `n.d.` en
  septiembre de 2026.

## Entorno

```bash
python -m venv .venv
.venv/bin/pip install -e ".[dev]"
```