# Tareas: Libro de indicadores de Banca Múltiple — V1

Spec: `spec.md` · Plan: `plan.md`.

## Fase 1 — Entorno y base

- [x] T001 Crear/validar el entorno virtual multiplataforma
  - Acceptance: README y AGENTS documentan la creación de `.venv` en Windows/macOS/Linux y la instalación editable con extras dev; el entorno importa `openpyxl`, `pytest` y `pyflakes`.
  - Verify: `.venv/bin/python -c "import openpyxl, pytest, pyflakes; print('ok')"` (usar ruta equivalente en Windows).
  - Files: README.md, AGENTS.md, pyproject.toml

- [x] T002 Configuración central en `config.py`
  - Acceptance: rutas reales a `BE BM 202609.xlsx` y `040_TO.csv`; `TIPO_SALDO = "Consolidado con SOFOMER"`; `CLAVE_SECTOR = "5"`; grupos `59`–`64`; `ANIOS` 2025 (12 meses) y 2026 (9 meses); `CONCEPTOS` con los códigos del spec; `CAMPOS_SECTOR`; `ND = "n.d."`; conversión a millones.
  - Verify: `.venv/bin/pytest tests/test_config.py`
  - Files: banca_multiple/config.py, tests/test_config.py

## Fase 2 — Lectura de datos

- [x] T003 Utilidades (`utilidades.py`)
  - Acceptance: `_a_numero`, `_norm`, `normalizar_clave`, `trimestre`, `fecha_mes`, `fecha_anterior`, `a_millones` (÷ 1,000,000) implementadas y probadas.
  - Verify: `.venv/bin/pytest tests/test_utilidades.py`
  - Files: banca_multiple/utilidades.py, tests/test_utilidades.py

- [x] T004 Lector XLSX del BE (`xlsx_lector.py`)
  - Acceptance: `_abrir_hoja` lee hojas por nombre desde el ZIP/XML y tolera las relaciones `customXml` del BE.
  - Verify: `.venv/bin/pyflakes banca_multiple/xlsx_lector.py`
  - Files: banca_multiple/xlsx_lector.py, tests/test_be.py
- [x] T005 `be.py`: universo y ROA/ROE publicados
  - Acceptance: `leer_universo` devuelve los 54 bancos (ranking, clave, nombre) desde `Evaluación Calidad Detallada`; lectura de ROA/ROE publicados del BE por banco y Sistema; claves normalizadas a 6 dígitos.
  - Verify: `.venv/bin/pytest tests/test_be.py`
  - Files: banca_multiple/be.py, tests/test_be.py

- [x] T006 `tablero.py`: filtro al vuelo del CSV
  - Acceptance: lectura en streaming; filtra por `tipo_saldo`, fecha y concepto; separa los 54 bancos, el total `5` y los grupos `59`–`64`; `Tablero.dato` disponible; tests con fixture.
  - Verify: `.venv/bin/pytest tests/test_tablero.py`
  - Files: banca_multiple/tablero.py, tests/test_tablero.py, tests/fixtures/tablero_mini.csv

Checkpoint — Lectura de datos: `.venv/bin/pytest tests/test_tablero.py tests/test_be.py` verde.

## Fase 3 — Filas

- [x] T007 `filas.py`: 54 filas por mes
  - Acceptance: genera 54 filas por mes y año; incluye `Trimestre`; convierte a millones; incluye campos para los 11 indicadores; crecimiento YoY usando datos del tablero (2024 si existe) o `n.d.`; `tiene_datos`.
  - Verify: `.venv/bin/pytest tests/test_filas.py`
  - Files: banca_multiple/filas.py, tests/test_filas.py

Checkpoint — Filas: conteo `54 × meses` por año.

## Fase 4 — Estilos e indicadores

- [x] T008 `estilos.py` y `fichas.py`
  - Acceptance: paleta AAA (`D1E7DD/FFF3CD/F8D7DA`); encabezados adaptados; `FICHAS` con los 11 indicadores y umbrales de la spec; `FICHAS_SEMAFORO` y `TOTAL_REGLAS`.
  - Verify: `.venv/bin/pytest tests/test_semaforos.py`
  - Files: banca_multiple/estilos.py, banca_multiple/fichas.py, tests/test_semaforos.py

## Fase 5 — Hojas del libro

- [x] T009 Hoja `Catálogo`
  - Acceptance: hoja `Catálogo` con los 54 bancos (clave CASFIM, nombre y campos disponibles; `n.d.` donde falte fuente); título con corte.
  - Verify: `.venv/bin/pyflakes banca_multiple/hojas/catalogo.py`
  - Files: banca_multiple/hojas/catalogo.py

- [x] T010 Hoja `Datos Fuente`
  - Acceptance: hojas `Datos Fuente 2025` y `Datos Fuente 2026`; filas banco × mes; columna `Trimestre`; fórmulas derivadas; notas de fuente y unidades.
  - Verify: `.venv/bin/pyflakes banca_multiple/hojas/datos_fuente.py`
  - Files: banca_multiple/hojas/datos_fuente.py

- [x] T011 Hoja `Indicadores`
  - Acceptance: hojas `Indicadores 2025` y `Indicadores 2026`; 11 indicadores con fórmulas; semáforos; MIN con mediana simple por mes (columna auxiliar oculta); ICAP y CCL/LCR `n.d.` en septiembre 2026.
  - Verify: `.venv/bin/pyflakes banca_multiple/hojas/indicadores.py`
  - Files: banca_multiple/hojas/indicadores.py

- [x] T012 `Diccionario` y `Semáforos`
  - Acceptance: hojas con fórmulas, umbrales y paleta AAA; notas.
  - Verify: `.venv/bin/pyflakes banca_multiple/hojas/diccionario.py banca_multiple/hojas/semaforos.py`
  - Files: banca_multiple/hojas/diccionario.py, banca_multiple/hojas/semaforos.py

- [x] T013 `escribir_xlsx` (`hojas/__init__.py`)
  - Acceptance: construye las hojas en orden (`Catálogo`, `Datos Fuente`, `Indicadores`, `Diccionario`, `Semáforos`), metadatos y `fullCalcOnLoad = True`.
  - Verify: `.venv/bin/python generar_banca_multiple.py --anios 2026 --out /tmp/bancos_2026.xlsx`
  - Files: banca_multiple/hojas/__init__.py

Checkpoint — Libro base: generación con `--anios 2026` sin error.

## Fase 6 — Orquestación

- [x] T014 `main.py` (CLI y flujo completo)
  - Acceptance: `argparse` con `--out`, `--entradas`, `--salidas`, `--tablero`, `--anios`; `parse_anios`; valida archivos; lee universo; prepara filas; valida datos; escribe; valida libro; retorna 0/2.
  - Verify: `.venv/bin/python generar_banca_multiple.py --help`
  - Files: banca_multiple/main.py, tests/test_cli.py

Checkpoint — Orquestación: corrida por defecto con exit 0 y "Validación general: OK".

## Fase 7 — Validaciones

- [x] T015 `validacion_datos.py`
  - Acceptance: ROA/ROE calculados vs publicados del BE (por banco y Sistema); IMOR/ICOR calculados vs publicados del tablero (por banco); consistencia suma de 54 vs total `5` y grupos `59`–`64`; ICAP con lag documentado.
  - Verify: `.venv/bin/pytest tests/test_validacion_datos.py`
  - Files: banca_multiple/validacion_datos.py, tests/test_validacion_datos.py

- [x] T016 `validacion_libro.py`
  - Acceptance: hojas esperadas; 54 filas en catálogo; filas por mes = 54; fórmulas clave; reglas de formato condicional = `TOTAL_REGLAS`.
  - Verify: `.venv/bin/pytest tests/test_validacion_libro.py`
  - Files: banca_multiple/validacion_libro.py, tests/test_validacion_libro.py

Checkpoint — Validaciones: numéricas dentro de tolerancia.

## Fase 8 — Pruebas

- [x] T017 Ajuste de tests y fixtures
  - Acceptance: tests de config, utilidades, tablero, filas, semáforos, CLI y validaciones verdes; fixtures adaptados a instituciones 040xxx.
  - Verify: `.venv/bin/pytest`
  - Files: tests/conftest.py, tests/test_filas.py, tests/test_tablero.py, tests/test_cli.py, tests/test_validacion_libro.py, tests/test_be.py
Checkpoint — Pruebas: `pytest` completo verde y `pyflakes banca_multiple/` limpio.

## Fase 9 — Documentación y verificación global

- [x] T018 Documentación (README, AGENTS, entradas)
  - Acceptance: README con uso, verificación, fuentes y `.venv`; AGENTS con conteos actualizados; entradas/README actualizado.
  - Verify: revisión manual de los archivos.
  - Files: README.md, AGENTS.md, entradas/README.md

- [x] T019 Verificación global (última tarea)
  - Acceptance: `pytest` pasa; `pyflakes` limpio; `--help` funciona; primer run genera el libro; regenerar y comparar con `scripts/comparar.py` → `IDÉNTICO` (exit 0).
  - Verify:
    ```bash
    .venv/bin/pytest
    .venv/bin/pyflakes banca_multiple/ tests generar_banca_multiple.py
    .venv/bin/python generar_banca_multiple.py --help
    .venv/bin/python generar_banca_multiple.py --out /tmp/bancos.xlsx > /tmp/salida1.txt
    cp /tmp/bancos.xlsx /tmp/referencia.xlsx
    .venv/bin/python generar_banca_multiple.py --out /tmp/bancos.xlsx > /tmp/salida2.txt
    .venv/bin/python scripts/comparar.py --xlsx-a /tmp/referencia.xlsx --xlsx-b /tmp/bancos.xlsx --stdout-a /tmp/salida1.txt --stdout-b /tmp/salida2.txt
    ```
  - Files: scripts/comparar.py

No hacer `git commit` ni `git push`; dejar el cambio listo y sugerir los comandos.