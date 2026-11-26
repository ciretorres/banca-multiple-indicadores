# Tareas: ICAP de Banco de México y notas de liquidez

Spec: `docs/specs/002-icap-banxico-y-notas-liquidez/spec.md` · Plan: `plan.md` de esta carpeta.
Orden por dependencia: T001 → T002 → T003 → T004 → T005 → T006 → T007 → T008.
El humano revisa cada checkpoint antes de seguir.

## Fase 0 · Base

- [x] **T001 — Agregar e instalar `pypdf` (multiplataforma)**
  - Acceptance: `pypdf` figura en `dependencies` de `pyproject.toml`; el import
    funciona con `.venv/bin/python` y con `.venv\Scripts\python.exe`; `pytest`
    y `pyflakes` siguen limpios.
  - Verify: `.venv/bin/pip install -e ".[dev]" && .venv/bin/python -c "import pypdf; print(pypdf.__version__)" && .venv/bin/pytest -q && .venv/bin/pyflakes banca_multiple/ tests generar_banca_multiple.py` (Windows: `.venv\Scripts\python.exe -c "import pypdf; print(pypdf.__version__)"`).
  - Files: `pyproject.toml`

- [x] **T002 — Configurar `PDF_ICAP` y los códigos CCB/CCF**
  - Acceptance: `config.PDF_ICAP` vale `ICAP_BM_202608.pdf`; `CONCEPTOS`
    incluye `4021754 → ccb_pub` y `4021755 → ccf_pub` (coherente con
    `icap_pub`); los tests de configuración pasan.
  - Verify: `.venv/bin/pytest tests/test_config.py -q && .venv/bin/pyflakes banca_multiple/config.py tests/test_config.py`
  - Files: `banca_multiple/config.py`, `tests/test_config.py`

- [x] **Checkpoint 0:** `pypdf` importable en ambos ejecutables; rutas y
  códigos nuevos presentes; sin cambios en el libro.

## Fase 1 · Lector del PDF

- [x] **T003 — Lector genérico `pdf_icap.py` con tests de fixture**
  - Acceptance: `leer_icap(ruta_pdf, nombres)` devuelve `fecha` derivada de
    `ICAP_BM_YYYYMM.pdf` y 54 bancos + `total` con `icap`, `ccb`, `ccf` y
    `categoria`; nombres con espacios entre caracteres se normalizan y se
    mapean a claves `040xxx` con el mapa recibido; si faltan encabezados,
    filas o el Total, lanza `SystemExit` con archivo, columna o fila; los
    tests usan texto sintético, no `entradas/`.
  - Verify: `.venv/bin/pytest tests/test_pdf_icap.py -q && .venv/bin/pyflakes banca_multiple/pdf_icap.py tests/test_pdf_icap.py` y una prueba rápida con `entradas/ICAP_BM_202608.pdf` que imprime 55 registros y fecha `202608`.
  - Files: `banca_multiple/pdf_icap.py` (nuevo), `tests/test_pdf_icap.py` (nuevo)

- [x] **Checkpoint 1:** lector aislado verificado; riesgo de extracción y de
  mapeo de nombres resuelto antes de tocar el libro.

## Fase 2 · El PDF entra al libro

- [x] **T004 — CLI `--pdf-icap` y campos del PDF en las filas**
  - Acceptance: `--pdf-icap RUTA` sobreescribe `DIR_ENTRADAS / PDF_ICAP` y
    `--help` lo documenta; `main.py` carga `leer_icap` con `nombres` y pasa los
    datos a `preparar_filas`; las filas del mes del PDF llevan `ccb`, `ccf` y
    `categoria` y las demás valen `ND`; si la fecha del PDF no está en el rango
    generado, falla con mensaje claro.
  - Verify: `.venv/bin/python generar_banca_multiple.py --help | grep -- --pdf-icap && .venv/bin/pytest tests/test_cli.py tests/test_filas.py -q && .venv/bin/pyflakes banca_multiple/main.py banca_multiple/filas.py tests/test_cli.py tests/test_filas.py`
  - Files: `banca_multiple/main.py`, `banca_multiple/filas.py`, `tests/test_cli.py`, `tests/test_filas.py`

- [x] **T005 — Columnas `CCB`/`CCF`/`Categoría` y nota en `Datos Fuente`**
  - Acceptance: `ENC_DATOS` tiene `CCB (%)`, `CCF (%)` y `Categoría` al final,
    en las columnas 36–38 (después de `Margen Financiero Ajustado 12M`, col
    35); `escribir_datos_fuente` escribe los valores del PDF en 202608 y `n.d.`
    en los demás meses (porcentajes con `FMT_PORC`, categoría como texto); la
    nota de CCL/LCR y CFEN/NSFR aparece en `Datos Fuente` y reemplaza la nota
    "n.d. en V1" de `Indicadores`; las 35 columnas previas, sus fórmulas y las
    comprobaciones de `validacion_libro.py` no cambian; el libro pasa
    `validar_libro`.
  - Verify:
    ```bash
    .venv/bin/python generar_banca_multiple.py --out /tmp/bancos.xlsx > /tmp/salida2.txt
    .venv/bin/python -c "from openpyxl import load_workbook; h=[c.value for c in load_workbook('/tmp/bancos.xlsx')['Datos Fuente 2026'][4]]; print(h[35:38])"
    .venv/bin/pytest -q && .venv/bin/pyflakes banca_multiple/ tests generar_banca_multiple.py
    ```
    Esperado: `['CCB\n(%)', 'CCF\n(%)', 'Categoría']` en las columnas 36–38 y
    `Validación general: OK`.
  - Files: `banca_multiple/estilos.py`, `banca_multiple/hojas/datos_fuente.py`, `banca_multiple/hojas/indicadores.py`

- [x] **Checkpoint 2:** libro generable con las columnas nuevas al final; 7
  hojas, 54 filas por mes y fórmulas existentes sin cambios; `validar_libro` OK;
  `pytest` y `pyflakes` limpios.

## Fase 3 · Validación y cierre

- [x] **T006 — Notas de liquidez en la documentación**
  - Acceptance: `README.md` (sección `Fuentes`) y `entradas/README.md`
    describen `ICAP_BM_YYYYMM.pdf` y explican CCL/LCR (activos líquidos de alta
    calidad / salidas netas a 30 días) y CFEN/NSFR (financiación estable
    disponible / requerida a 1 año), publicación trimestral con desfase de un
    trimestre y último dato `202606` → `n.d.` en septiembre de 2026.
  - Verify: `grep -n -E "CCL/LCR|CFEN/NSFR|ICAP_BM|202606" README.md entradas/README.md`
  - Files: `README.md`, `entradas/README.md`

- [x] **T007 — Validación ICAP/CCB/CCF: PDF vs tablero**
  - Acceptance: `validar_datos` acepta los datos del PDF de forma opcional; en
    la `fecha` del PDF compara por banco y para el Total los conceptos
    `icap_pub`, `ccb_pub` y `ccf_pub` del tablero contra el PDF con tolerancia
    de 0.02 pts; imprime la sección `ICAP / CCB / CCF del PDF vs tablero
    (202608)`; no compara otros meses; si excede la tolerancia, la corrida
    termina con `CON OBSERVACIONES`; los tests cubren caso OK y caso DIF.
  - Verify: `.venv/bin/pytest tests/test_validacion_datos.py -q && .venv/bin/python generar_banca_multiple.py > /tmp/salida_default.txt && grep -A60 "PDF vs tablero" /tmp/salida_default.txt && tail -1 /tmp/salida_default.txt`
    Esperado: peor diferencia ≤ 0.02 pts y `Validación general: OK`.
  - Files: `banca_multiple/validacion_datos.py`, `banca_multiple/main.py`, `tests/test_validacion_datos.py`

- [x] **T008 — Verificación global y diffs esperados**
  - Acceptance: `pytest` y `pyflakes` limpios; `--help` muestra `--pdf-icap`;
    corrida default con exit 0 y `Validación general: OK`; `comparar.py`
    entre la referencia de la spec 001 (generada antes de T005) y el libro
    nuevo muestra solo los diffs esperados: 3 columnas nuevas al final de
    `Datos Fuente` (cols 36–38), notas de liquidez y sección nueva en stdout;
    sin corrimiento de columnas ni cambios de fórmulas, ni hojas, filas o
    semáforos nuevos. Los diffs observados quedan registrados en `task.md`.
  - Verify:
    ```bash
    .venv/bin/pytest && .venv/bin/pyflakes banca_multiple/ tests generar_banca_multiple.py
    .venv/bin/python generar_banca_multiple.py --help | grep -- --pdf-icap
    .venv/bin/python generar_banca_multiple.py --out /tmp/bancos.xlsx > /tmp/salida2.txt
    .venv/bin/python scripts/comparar.py \
        --xlsx-a /tmp/referencia.xlsx --xlsx-b /tmp/bancos.xlsx \
        --stdout-a /tmp/salida1.txt --stdout-b /tmp/salida2.txt
    ```
    El comparador debe devolver exit 1 con solo esos diffs (no `IDÉNTICO`).
  - Files: ninguno (solo verificación; actualizar la lista de diffs en `task.md`).

**Diffs observados (registro T008; `plan.md` queda intacto):**

- `comparar.py` → exit 1, 4,379 entradas (3,766 xlsx + 613 stdout). Aglutinadas
  por causa son solo los cambios previstos; el comparador reporta celda por
  celda y línea por línea.
- XLSX: `Datos Fuente 2025/2026` ganan las columnas 36–38 (`CCB (%)`, `CCF (%)`,
  `Categoría`) con valor en agosto de 2026 y `n.d.` en los demás meses; tres
  filas de notas nuevas por hoja; cambios consecuentes de `max_row`,
  `max_column`, combinadas, anchos, altos y autofiltro. `Indicadores 2025/2026`:
  una nota reemplazada (`n.d. en V1`) y dos nuevas por hoja, con el mismo ajuste
  de `max_row`, combinadas y altos. Las 35 columnas antiguas, las fórmulas,
  `Catálogo`, `Diccionario` y `Semáforos` quedan sin cambios (verificado celda
  por celda en el área de datos).
- stdout: tres cambios lógicos — nueva línea `PDF de ICAP: ICAP_BM_202608.pdf ·
  corte 202608`, conteo del tablero de 57,342 a 61,084 registros (dos conceptos
  nuevos) y la sección `ICAP / CCB / CCF del PDF vs tablero (202608)` con 55
  bancos/Total + resumen. Peor diferencial 0.0050 pts (≤ 0.02); corrida con
  `Validación general: OK` y exit 0.
- Nota: el PDF trae valores a dos decimales (20.42, 16.93, ...); el ejemplo de
  cuatro decimales de la spec describe la precisión del tablero, no del PDF.

**Diffs observados (corrección del review; referencia = libro previo a la corrección):**

- `comparar.py` → exit 1, 108 diferencias, todas en `Datos Fuente 2026`, filas
  383–436 (agosto de 2026), columnas 36 (`CCB (%)`) y 37 (`CCF (%)`): los valores
  pasan de puntos a ratio al escribir (p. ej. `16.93` → `0.1693`) para que
  `FMT_PORC` muestre `16.93%` y no `1693.00%`. Es el único cambio en el libro;
  el `stdout` queda idéntico (0 diferencias). `filas.py` no cambia: la
  validación PDF vs tablero sigue comparando en puntos.
- `leer_icap` ahora falla con mensaje claro si el PDF no aporta 54 bancos más
  el Total; con `ICAP_BM_202608.pdf` extrae 54 + Total y el `stdout` no cambia.
- Verificación: `pytest` 70 pruebas, `pyflakes` limpio, `--help` con
  `--pdf-icap`, corrida default con `Validación general: OK` y exit 0.
- Cierre de revisión: el libro de `salidas/` se regeneró con el código corregido
  (`AJ402`/`AK402` = `0.1693`, formato `0.00%` → `16.93%`); `comparar.py` entre
  dos corridas del código final dio `IDÉNTICO` (exit 0).

- [x] **Checkpoint 3:** spec cumplida; cambio listo para revisión del humano.
  No se hace `git commit` ni `git push`.
