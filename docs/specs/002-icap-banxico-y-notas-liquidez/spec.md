# Spec: ICAP de Banco de México y notas de liquidez — V1

Extensión de la spec 001 (`docs/specs/001-libro-indicadores-banca-multiple/spec.md`),
que ya entrega el libro de 7 hojas, 54 bancos, corte 2025–2026 y cifras en
millones de pesos. Esta spec agrega una fuente nueva (PDF de Banco de México) y
notas explicativas; no cambia la lógica mensual/trimestral del libro.

## Objective

1. **Lector del PDF de ICAP.** Nuevo módulo `banca_multiple/pdf_icap.py` con
   `pypdf`, genérico para cualquier `ICAP_BM_YYYYMM.pdf` en `entradas/`. Extrae
   para los 54 bancos y el Total Banca Múltiple: ICAP, CCB, CCF y categoría de
   alertas tempranas. El mes del corte se deriva del nombre del archivo
   (`202608` con el PDF actual). Ruta configurable en `config.PDF_ICAP` y
   sobreescribible por CLI (`--pdf-icap`).

   - Documento actual: *Indicadores de capitalización — cifras al 31 de agosto
     de 2026* (Banco de México, publicado 12-oct-2026),
     `entradas/ICAP_BM_202608.pdf`.
   - Definiciones del documento: ICAP = Capital Neto / Activos Ponderados
     Sujetos a Riesgo Total; CCB = (Capital Fundamental + Capital no
     Fundamental) / Activos Ponderados Sujetos a Riesgo Total; CCF = Capital
     Fundamental / Activos Ponderados Sujetos a Riesgo Total; la categoría
     (todas `I` en el PDF) corresponde al artículo 220 de las Disposiciones.
   - El texto del PDF trae espacios entre caracteres (`B a n c o   B i n e o`).
     Normalizar y mapear por **nombre de banco** contra las claves `040xxx` del
     catálogo de la hoja `Evaluación Calidad Detallada` del BE (mismo mapa
     clave↔nombre que ya usa `main.py`).
   - El Total Banca Múltiple se extrae para validación contra el tablero, no se
     escribe como fila en las hojas (coherente con la spec 001: el total `5` y
     los grupos `59`–`64` solo validan).

2. **Columnas nuevas en `Datos Fuente`.** Agregar `CCB (%)`, `CCF (%)` y
   `Categoría` después de la columna `ICAP (%)`. Solo llevan dato del PDF en
   las filas del mes del corte (`202608` con el archivo actual); en los demás
   meses va `ND` (`n.d.`). No se agregan columnas nuevas a `Indicadores`.

3. **Validación contra el PDF.** En `validacion_datos.py`, comparar para el mes
   del corte los ICAP, CCB y CCF del tablero (conceptos `4021750`, `4021754`,
   `4021755`) contra los valores del PDF, por banco y para el Total. Al subir
   el PDF de septiembre solo cambia `PDF_ICAP` (o `--pdf-icap`) y la validación
   apunta automáticamente al mes nuevo del nombre del archivo.

   - Verificado con el PDF actual: ICAP del tablero y del PDF coinciden
     (BBVA 20.4192 → 20.42, Banorte 21.9080 → 21.91, Santander 18.9503 →
     18.95, Total 20.7680 → 20.77). El tablero 202608 ya publica CCB y CCF con
     los mismos valores (BBVA 16.9318 / 16.9318, Banorte 21.4910 / 13.0538,
     Total 18.7453 / 17.2230).
   - Tolerancia de 0.02 puntos porcentuales, igual que la validación de ICAP
     de la spec 001.

4. **Notas de liquidez.** Agregar una nota en `Datos Fuente` (junto a las
   columnas `CCL`/`CFEN`), en `Indicadores` (junto a `CCL/LCR`) y en `README.md`
   (sección `Fuentes`) con este contenido:

   - **CCL/LCR** = Cobertura de Liquidez = Activos líquidos de alta calidad /
     Salidas netas de efectivo a 30 días.
   - **CFEN/NSFR** = Financiamiento Estable Neto = Financiación estable
     disponible / Financiación estable requerida (1 año).
   - Se publican solo en cierres trimestrales (mar/jun/sep/dic), con desfase
     de un trimestre. Último dato disponible en el tablero: `202606` → `n.d.`
     en septiembre de 2026.

## Tech Stack

- Python ≥ 3.11, `openpyxl` ≥ 3.1 y < 4, `pypdf` (dependencia nueva),
  `pytest` y `pyflakes` (dev).
- Entradas: `entradas/ICAP_BM_202608.pdf` (no versionada),
  `entradas/BE BM 202609.xlsx` y `entradas/tablero/sh_datos_csv_40_i/040_TO.csv`.
- Salida: `salidas/Bancos_Multiples_Indicadores_Datos.xlsx` (sin cambios de
  nombre ni de hojas).

## Commands

- Generar: `.venv/bin/python generar_banca_multiple.py`
- Generar con otro PDF: `.venv/bin/python generar_banca_multiple.py --pdf-icap RUTA`
- Generar (ruta exacta): `.venv/bin/python generar_banca_multiple.py --out RUTA`
- Wrapper equivalente: `python -m banca_multiple`
- Ayuda: `.venv/bin/python generar_banca_multiple.py --help`
- Pruebas: `.venv/bin/pytest`
- Lint: `.venv/bin/pyflakes banca_multiple/ tests generar_banca_multiple.py`
- Comparación: `.venv/bin/python scripts/comparar.py --xlsx-a A --xlsx-b B`
- Verificación completa: ver `AGENTS.md` § "Verificar un cambio".

## Project Structure

```
generar_banca_multiple.py        # wrapper (sin cambios)
banca_multiple/
  config.py                      # editar: PDF_ICAP, códigos CCB/CCF
  pdf_icap.py                    # nuevo: lector del PDF con pypdf
  main.py                        # editar: --pdf-icap, pasar datos del PDF
  filas.py                       # editar: campos ccb/ccf/categoria por mes
  validacion_datos.py            # editar: ICAP/CCB/CCF PDF vs tablero
  estilos.py                     # editar: encabezados nuevos de Datos Fuente
  hojas/datos_fuente.py          # editar: columnas + nota de liquidez
  hojas/indicadores.py           # editar: nota de liquidez
pyproject.toml                   # editar: dependencia pypdf
README.md                        # editar: nota de liquidez en Fuentes
entradas/README.md               # editar: describir ICAP_BM_YYYYMM.pdf
tests/
  test_pdf_icap.py               # nuevo
  test_validacion_datos.py       # editar
  test_cli.py                    # editar: --pdf-icap
docs/specs/002-icap-banxico-y-notas-liquidez/
  spec.md, plan.md, task.md      # este ciclo (plan/task tras aprobación)
```

## Code Style

- Español; seguir los patrones de la spec 001: configuración central en
  `config.py`, módulos pequeños por responsabilidad, docstrings solo cuando
  aporten, `ND = "n.d."` para datos no disponibles.
- Funciones nombradas como las existentes (`leer_universo`, `leer_tablero`,
  `preparar_filas`): `leer_icap(ruta_pdf, nombres)`.
- Reutilizar `_norm` de `utilidades.py` para normalizar nombres; `pypdf`
  solo dentro de `pdf_icap.py`. Formato de retorno esperado:

```python
{
    "fecha": "202608",
    "bancos": {
        "040xxx": {
            "icap": 20.4192, "ccb": 16.9318,
            "ccf": 16.9318, "categoria": "I",
        },
    },
    "total": {"icap": 20.7680, "ccb": 18.7453,
              "ccf": 17.2230, "categoria": "I"},
}
```

- Porcentajes con `FMT_PORC` y notas con `_notas` (igual que las hojas
  actuales). Categoría como texto. Si cambia el formato del PDF, lanzar
  `SystemExit` con mensaje claro (archivo, columna faltante y fila).
- `pyflakes` limpio sobre `banca_multiple/`.

## Testing Strategy

- `pytest` sobre `tests/` y `pyflakes` sobre los archivos tocados.
- `tests/test_pdf_icap.py`:
  - normalización de nombres con espacios entre caracteres y mapeo a `040xxx`;
  - extracción de ICAP/CCB/CCF/categoría para 54 bancos + Total y fecha
    derivada de `ICAP_BM_YYYYMM.pdf`;
  - error claro si faltan columnas o cambia el orden del PDF (fixture de
    texto, sin depender de `entradas/`);
  - meses sin PDF → `n.d.` en `filas.py` (`tests/test_filas.py`).
- `tests/test_validacion_datos.py`: comparación PDF vs tablero en el mes del
  corte, por banco y Total, con tolerancia de 0.02 pts; sin comparaciones en
  otros meses.
- `tests/test_cli.py`: acepta `--pdf-icap RUTA` y `--help` lo documenta.
- `scripts/comparar.py`: en esta spec los diffs esperados son las 3 columnas
  nuevas, las notas y la nueva sección de validación en `stdout`; documentarlos
  en la verificación en vez de exigir `IDÉNTICO` ciego. El resto del libro
  (hojas, filas, fórmulas, semáforos) debe quedar sin cambios.

## Boundaries

- **Always:** ejecutar `pytest` y `pyflakes` antes de cerrar; usar el PDF como
  fuente principal de CCB/CCF y el tablero como respaldo/validación; derivar el
  mes del corte del nombre del archivo; `n.d.` en meses sin dato del PDF;
  fallar con mensaje claro si el formato del PDF cambia; documentar cualquier
  diferencia del libro frente a la referencia.
- **Ask first:** añadir dependencias nuevas (en esta spec: `pypdf`, ya
  aprobada); cambiar el universo de 54 bancos, el total `5` o los grupos;
  cambiar hojas, umbrales o tolerancias de validación.
- **Never:** hacer `git commit` ni `git push`; editar `entradas/`; hardcodear
  rutas absolutas; inventar CCL/CFEN en meses que el tablero no publica;
  cambiar la lógica mensual/trimestral; escribir el Total del PDF como fila de
  las hojas.

## Success Criteria

- `pypdf` figura en `pyproject.toml` y `.venv/bin/pytest` pasa; `pyflakes`
  sale limpio; `--help` muestra `--pdf-icap`.
- `leer_icap` devuelve 54 bancos + Total con ICAP, CCB, CCF y categoría para
  `202608`, con nombres normalizados y mapeados a claves `040xxx`; si el
  formato cambia, falla con mensaje claro.
- `Datos Fuente` tiene las columnas `CCB (%)`, `CCF (%)` y `Categoría` con
  valores solo en `202608` y `n.d.` en los demás meses; el número de filas y
  las columnas previas no cambian.
- La validación imprime una sección de ICAP/CCB/CCF PDF vs tablero para
  `202608` (bancos y Total), con peor diferencia ≤ 0.02 pts; la corrida
  default termina con `Validación general: OK` y exit 0.
- Las notas de CCL/LCR y CFEN/NSFR aparecen en `Datos Fuente`, `Indicadores` y
  `README.md`, con la explicación de publicación trimestral, desfase de un
  trimestre y `n.d.` en septiembre 2026.
- `scripts/comparar.py` entre la referencia (spec 001) y el libro nuevo
  muestra únicamente los diffs esperados: 3 columnas, notas y la sección de
  validación en `stdout`.

## Out of Scope (Deferred)

- Llenar ICAP de septiembre: el PDF disponible es de agosto; el de septiembre
  se subirá después y solo cambiará `PDF_ICAP` / `--pdf-icap`.
- Cambiar la lógica mensual/trimestral del libro ni la cantidad de hojas.
- Agregar CCL/CFEN en meses distintos de los que publica el tablero.
- Semáforo o umbrales propios para CCB, CCF o la categoría: solo se muestran
  como información y se validan.

## Open Questions

- ¿La categoría se muestra como texto (`"I"`) o como número? (asumir texto).
- ¿El PDF de septiembre vendrá con el mismo formato (columnas y orden)?
  (asumir sí; el lector debe fallar con mensaje claro si cambia).
- ¿CCB/CCF se toman del PDF o del tablero? (usar PDF como fuente principal y
  tablero como respaldo/validación).
