# Tareas: Vista para Copilot — cortes trimestrales

Spec: `docs/specs/003-vista-copilot-cortes-trimestrales/spec.md` · Plan: `plan.md` de esta carpeta.
Orden por dependencia: T001 → T002 → T003 → T004 → T005. El humano revisa cada checkpoint antes de seguir.
En Windows usar `.venv\Scripts\python.exe` y `.venv\Scripts\pytest.exe`.

## Fase 0 · Configuración

- [x] **T001 — Ruta del libro compañero y cortes trimestrales en `config.py`**
  - Acceptance: `SALIDA_VISTA_COPILOT` apunta a
    `DIR_SALIDAS / "Bancos_Multiples_Cortes_Trimestrales.xlsx"`;
    `CORTES_TRIMESTRALES` deriva de `ANIOS` con cierre en 3/6/9/12 y entrega
    exactamente 7 entradas ordenadas (`2025 Q1`…`2025 Q4`, `2026 Q1`…`2026 Q3`),
    sin Q4 de 2026; las constantes existentes no cambian y el libro principal
    sigue idéntico.
  - Verify:
    ```bash
    .venv/bin/pytest tests/test_config.py -q
    .venv/bin/pyflakes banca_multiple/config.py tests/test_config.py
    .venv/bin/python -c "from banca_multiple.config import CORTES_TRIMESTRALES as c; print(len(c), [x[0] for x in c])"
    ```
    Esperado: `7 ['2025 Q1', '2025 Q2', '2025 Q3', '2025 Q4', '2026 Q1', '2026 Q2', '2026 Q3']`.
  - Files: `banca_multiple/config.py`, `tests/test_config.py`

- [x] **Checkpoint 0:** configuración lista; `pytest` y `pyflakes` limpios; el
  libro principal no cambia.

## Fase 1 · Cálculo compartido

- [x] **T002 — Funciones puras de los 11 indicadores y de la mediana de referencia**
  - Acceptance: en `banca_multiple/hojas/indicadores.py` se agregan
    `calcular_indicadores(fila)` y `calcular_mediana_min(filas_del_mes)` sin
    modificar `escribir_indicadores`; los 11 valores siguen la tabla del plan
    (`I=H/G` → `capital_neto/activos_riesgo`, …, `AG` → `ccl`), con división
    segura que devuelve `ND` si falta operando o el denominador es 0;
    eficiencia con ingresos ≤ 0 devuelve `n.a.`, distinto de `n.d.` (decisión
    resuelta); el MIN devuelto es el de cada banco (`AI/AC`), no una mediana
    repetida (decisión resuelta); `calcular_mediana_min` usa
    `statistics.median` sobre los 54 bancos del mes, negativos incluidos, solo
    como referencia para la `Leyenda`; los tests usan filas sintéticas, no
    `entradas/`.
  - Verify:
    ```bash
    .venv/bin/pytest tests/test_indicadores_valores.py -q
    .venv/bin/pyflakes banca_multiple/hojas/indicadores.py tests/test_indicadores_valores.py
    .venv/bin/python generar_banca_multiple.py --out /tmp/bancos.xlsx > /tmp/salida2.txt
    .venv/bin/python scripts/comparar.py --xlsx-a /tmp/referencia.xlsx --xlsx-b /tmp/bancos.xlsx --stdout-a /tmp/salida1.txt --stdout-b /tmp/salida2.txt
    ```
    Esperado: `IDÉNTICO` (exit 0) para el libro principal.
  - Files: `banca_multiple/hojas/indicadores.py`, `tests/test_indicadores_valores.py` (nuevo)

- [x] **Checkpoint 1:** paridad de valores verificada (MIN por banco, `n.a.` en
  eficiencia); extracción sin impacto en el libro principal.

## Fase 2 · Libro compañero y CLI

- [x] **T003 — Escritor de las 7 hojas de corte y la hoja `Leyenda`**
  - Acceptance: módulo nuevo que construye un `Workbook` con las 7 hojas en
    orden y `Leyenda` al final; cada hoja de corte tiene 15 columnas
    (`No.`, `Banco`, `Mes de corte`, `Trimestre` + 11 indicadores), 54 filas de
    datos y los indicadores escritos como número con `FMT_PORC` o texto exacto
    (`ND` / `n.a.`) con `FMT_TEXTO`, nunca como fórmula; Q3 2026 fuerza `n.d.` en
    ICAP y CCL/LCR; las filas llevan el MIN calculado de cada banco (no la
    mediana repetida); `Leyenda` incluye CCL/LCR, CFEN/NSFR, trimestralidad con
    desfase (`202606` → `n.d.` en sep-2026), `n.d.`, la nota de MIN y la mediana
    de los 54 como referencia del semáforo original.
  - Verify:
    ```bash
    .venv/bin/pytest tests/test_vista_copilot.py -q
    .venv/bin/pyflakes banca_multiple/vista_copilot.py tests/test_vista_copilot.py
    ```
    El test recorre el rango de datos y falla si `cell.data_type == "f"` o si
    alguna celda de indicador está vacía; comprueba `sheetnames`, 54 filas, 15
    columnas, los `n.d.` de `2026 Q3`, MIN distinto por banco, `n.a.` en
    eficiencia con ingresos ≤ 0 y la nota de mediana en `Leyenda`.
  - Files: `banca_multiple/vista_copilot.py` (nuevo), `tests/test_vista_copilot.py` (nuevo)

- [x] **T004 — Entry point `generar_vista_copilot.py` con `--out` y `--help`**
  - Acceptance: script nuevo multiplataforma que usa `argparse`, con `--out`
    (ruta exacta) y valor por defecto `SALIDA_VISTA_COPILOT`; carga universo,
    nombres, tablero, PDF de ICAP y `preparar_filas` con los mismos archivos de
    `entradas/` que el libro principal, sin importar `main.main()` ni tocar su
    CLI; imprime un resumen breve y escribe el libro del T003; `--out RUTA`
    respeta la ruta dada.
  - Verify:
    ```bash
    .venv/bin/python generar_vista_copilot.py --help | grep -- --out
    .venv/bin/python generar_vista_copilot.py --out /tmp/vista_copilot.xlsx
    .venv/bin/pytest tests/test_vista_copilot.py -q
    .venv/bin/pyflakes generar_vista_copilot.py banca_multiple/vista_copilot.py tests/test_vista_copilot.py
    ```
    Esperado: exit 0, `/tmp/vista_copilot.xlsx` creado y 7 hojas + `Leyenda`.
  - Files: `generar_vista_copilot.py` (nuevo), `banca_multiple/vista_copilot.py`, `tests/test_vista_copilot.py`

- [x] **Checkpoint 2:** libro compañero generable y verificado; CLI propia sin
  efectos en la CLI del libro principal.

## Fase 3 · Cierre

- [x] **T005 — Verificación global y registro de resultados**
  - Acceptance: `pytest` y `pyflakes` limpios; `--help` documenta `--out`;
    corrida nueva con exit 0; libro compañero con 7 hojas + `Leyenda`, 54 filas
    y 15 columnas por corte, cero fórmulas y cero celdas vacías en indicadores,
    `n.d.` en ICAP/CCL de `2026 Q3`, MIN por banco y `n.a.` en eficiencia con
    ingresos ≤ 0; libro principal intacto con
    `generar_banca_multiple.py` y su CLI sin cambios y `comparar.py` →
    **`IDÉNTICO` (exit 0)**. Los resultados se registran aquí; el plan queda
    intacto. No se hace `git commit` ni `git push`.
  - Verify:
    ```bash
    .venv/bin/pytest
    .venv/bin/pyflakes banca_multiple/ tests generar_vista_copilot.py
    .venv/bin/python generar_vista_copilot.py --help | grep -- --out
    .venv/bin/python generar_vista_copilot.py --out /tmp/vista_copilot.xlsx
    .venv/bin/python -c "from openpyxl import load_workbook; wb=load_workbook('/tmp/vista_copilot.xlsx'); print(wb.sheetnames); print([(ws.title, ws.max_row - 5 + 1, ws.max_column, sum(c.data_type=='f' for row in ws.iter_rows() for c in row)) for ws in wb.worksheets if ws.title!='Leyenda'])"
    .venv/bin/python generar_banca_multiple.py --out /tmp/bancos.xlsx > /tmp/salida2.txt
    .venv/bin/python scripts/comparar.py --xlsx-a /tmp/referencia.xlsx --xlsx-b /tmp/bancos.xlsx --stdout-a /tmp/salida1.txt --stdout-b /tmp/salida2.txt
    ```
    Esperado: `pytest` OK (70 pruebas + nuevas), `pyflakes` limpio, siete tuplas
    `(hoja, 54, 15, 0)` y `IDÉNTICO` con exit 0 del comparador.
  - Files: ninguno (solo verificación; registro de resultados en este `task.md`)

Resultados (2026-11-25): `pytest` 113 pruebas OK; `pyflakes` limpio; `--help`
documenta `--out`; corrida real con `--out` y con la ruta por defecto → exit 0;
libro compañero con `2025 Q1`…`2026 Q3` + `Leyenda`, 54 filas de datos y 15
columnas por corte, 0 fórmulas y 0 celdas vacías en indicadores; `2026 Q3` con
ICAP y CCL/LCR en `n.d.` y 3 eficiencias `n.a.`; MIN distinto por banco y
mediana de los 54 en `Leyenda`; libro principal `IDÉNTICO` (exit 0).
Nota: el conteo correcto de filas de datos es `ws.max_row - 5 + 1` (= 54): los
datos van de la fila 5 a la 58 y el encabezado está en la fila 4. La forma
`ws.max_row - 5` daba 53 por off-by-one; el one-liner de arriba ya está corregido.

- [x] **Checkpoint 3:** spec cumplida; cambio listo para revisión del humano.
