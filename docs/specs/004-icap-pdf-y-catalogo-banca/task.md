# Tareas: ICAP del PDF, vista Copilot y catálogo — V1

Spec: `docs/specs/004-icap-pdf-y-catalogo-banca/spec.md` ·
Plan: `docs/specs/004-icap-pdf-y-catalogo-banca/plan.md`.
Ejecutar en orden. No hacer `git commit` ni `git push`.

## Fase 0 — Línea base

- [x] T001 — Capturar la referencia antes de tocar nada
  - Acceptance: con el código actual y el PDF de agosto, existen
    `/tmp/banca004/referencia.xlsx`, `bancos.xlsx`, `salida1.txt`,
    `vista_referencia.xlsx`, `vista.xlsx` y `vista_salida1.txt`. La referencia no
    se regenera después de borrar el PDF viejo.
  - Verify:
    ```bash
    mkdir -p /tmp/banca004
    .venv/bin/python generar_banca_multiple.py --out /tmp/banca004/bancos.xlsx > /tmp/banca004/salida1.txt
    cp /tmp/banca004/bancos.xlsx /tmp/banca004/referencia.xlsx
    .venv/bin/python generar_vista_copilot.py --out /tmp/banca004/vista.xlsx > /tmp/banca004/vista_salida1.txt
    cp /tmp/banca004/vista.xlsx /tmp/banca004/vista_referencia.xlsx
    ls -l /tmp/banca004/
    ```
  - Files: ninguno (solo salidas en `/tmp/banca004/`).

## Fase 1 — Entrada del PDF

- [x] T002 — Apuntar al PDF de septiembre y definir la nota de fuente
  - Acceptance: `config.PDF_ICAP == "ICAP_BM_202609.pdf"`;
    `config.NOTA_ICAP_PDF` contiene exactamente
    `ICAP: PDF de Banxico (tablero sin publicar ese mes)`; el test del nombre
    de agosto se renombra al de septiembre. `--help` sigue documentando
    `--pdf-icap`.
  - Verify:
    ```bash
    .venv/bin/pytest tests/test_config.py -q
    .venv/bin/pyflakes banca_multiple/config.py tests/test_config.py
    .venv/bin/python generar_banca_multiple.py --help | grep -- '--pdf-icap'
    ```
  - Files: `banca_multiple/config.py`, `tests/test_config.py`.

- [x] T003 — Borrar el PDF de agosto y actualizar `entradas/README.md`
  - Acceptance: `entradas/ICAP_BM_202608.pdf` ya no existe;
    `entradas/ICAP_BM_202609.pdf` sigue presente; el ejemplo del README de
    entradas dice `ICAP_BM_202609.pdf` → corte septiembre de 2026. No se borra
    ni se edita ningún otro archivo de `entradas/`.
  - Verify:
    ```bash
    test ! -e entradas/ICAP_BM_202608.pdf
    test -f entradas/ICAP_BM_202609.pdf
    grep -n 'ICAP_BM_202609.pdf' entradas/README.md
    ! grep -q '202608' entradas/README.md
    ```
  - Files: `entradas/ICAP_BM_202608.pdf` (borrar), `entradas/README.md`.

**Checkpoint Fase 1**

- [x] `pytest` y `pyflakes` limpios; el generador encuentra el PDF nuevo.

## Fase 2 — ICAP del PDF en el libro principal

- [x] T004 — Exponer el ICAP del PDF en las filas
  - Acceptance: `preparar_filas` agrega `icap_pdf` en puntos (p. ej. 28.83) solo
    para septiembre de 2026 y bancos presentes en el PDF; es `None`/no existe
    en los otros meses y cuando el tablero trae ICAP publicado. `ccb`, `ccf`,
    `categoria` y el resto de campos no cambian.
  - Verify:
    ```bash
    .venv/bin/pytest tests/test_filas.py -q
    ```
  - Files: `banca_multiple/filas.py`, `tests/test_filas.py`.

- [x] T005 — Escribir el número en `Datos Fuente` col 9 y la nota de fuente
  - Acceptance: si la fila trae `icap_pdf`, la col 9 es número en ratio
    (`20.43 → 0.2043`) con `FMT_PORC`; si no, conserva
    `=IFERROR(H{r}/G{r},"n.d.")`. La nota `NOTA_ICAP_PDF` aparece visible en
    las notas de `Datos Fuente` e `Indicadores`. El resto de columnas y las
    fórmulas de `Indicadores` siguen iguales.
  - Verify:
    ```bash
    .venv/bin/pytest tests/test_hojas.py -q
    .venv/bin/pyflakes banca_multiple/hojas/datos_fuente.py banca_multiple/hojas/indicadores.py
    ```
  - Files: `banca_multiple/hojas/datos_fuente.py`,
    `banca_multiple/hojas/indicadores.py`, `tests/test_hojas.py`.

- [x] T006 — Validar sin contraste cuando el tablero no trae ese mes
  - Acceptance: `_validar_icap_pdf` imprime
    `sin contraste en tablero · fuente PDF` y no marca `DIF` si el tablero no
    trae ICAP para la fecha del PDF; con tablero presente mantiene la
    comparación de 0.02 pts. La corrida completa termina con
    `Validación general: OK`.
  - Verify:
    ```bash
    .venv/bin/pytest tests/test_validacion_datos.py -q
    .venv/bin/python generar_banca_multiple.py --out /tmp/banca004/bancos.xlsx > /tmp/banca004/salida_ok.txt
    grep 'sin contraste en tablero' /tmp/banca004/salida_ok.txt
    grep 'Validación general: OK' /tmp/banca004/salida_ok.txt
    ```
  - Files: `banca_multiple/validacion_datos.py`,
    `tests/test_validacion_datos.py`.

**Checkpoint Fase 2**

- [x] Corrida principal OK; col I de septiembre numérica y resto de meses con
      fórmula; `pytest` y `pyflakes` limpios.

## Fase 3 — Catálogo de 7 columnas

- [x] T007 — Reducir el catálogo a 7 columnas y pasar `datos_icap`
  - Acceptance: `ENC_CATALOGO` es exactamente
    `No.`, `Clave CASFIM`, `Banco`, `Categoría`, `Estatus`, `Tipo`,
    `Fecha de Autorización`; no hay `Federación` ni `Nivel`; la categoría sale
    de `datos_icap["bancos"][clave]["categoria"]` (`n.d.` si falta); anchos,
    notas y `auto_filter` cubren solo A:G. `escribir_xlsx(..., datos_icap=None)`
    recibe el dato desde `main.py` por keyword.
  - Verify:
    ```bash
    .venv/bin/python generar_banca_multiple.py --out /tmp/banca004/bancos.xlsx > /tmp/banca004/salida_cat.txt
    grep 'Validación general: OK' /tmp/banca004/salida_cat.txt
    .venv/bin/pyflakes banca_multiple/estilos.py banca_multiple/hojas/catalogo.py banca_multiple/hojas/__init__.py banca_multiple/main.py
    ```
  - Files: `banca_multiple/estilos.py`, `banca_multiple/hojas/catalogo.py`,
    `banca_multiple/hojas/__init__.py`, `banca_multiple/main.py`.

- [x] T008 — Verificar encabezados del catálogo y cubrirlos con tests
  - Acceptance: `validacion_libro` compara los 7 encabezados de la fila 4 con
    `ENC_CATALOGO` y marca error si falta alguno; los tests cubren
    `Categoría = I` / `n.d.`, ausencia de `Federación` y 7 encabezados exactos.
  - Verify:
    ```bash
    .venv/bin/pytest tests/test_hojas.py tests/test_validacion_libro.py -q
    ```
  - Files: `banca_multiple/validacion_libro.py`, `tests/test_hojas.py`,
    `tests/test_validacion_libro.py`.

**Checkpoint Fase 3**

- [x] Catálogo con 7 columnas, `validacion_libro` y tests pasan.

## Fase 4 — Vista Copilot

- [x] T009 — ICAP del PDF en `2026 Q3` y Leyenda actualizada
  - Acceptance: se elimina el `n.d.` forzado de ICAP en `2026 Q3`; ese corte
    muestra el ICAP del PDF como número en ratio para los 54 bancos;
    `CCL/LCR` sigue en `n.d.`; la Leyenda incluye `NOTA_ICAP_PDF`; los otros
    seis cortes no cambian.
  - Verify:
    ```bash
    .venv/bin/pytest tests/test_vista_copilot.py -q
    .venv/bin/python generar_vista_copilot.py --out /tmp/banca004/vista.xlsx
    ```
  - Files: `banca_multiple/vista_copilot.py`,
    `tests/test_vista_copilot.py`.

**Checkpoint Fase 4**

- [x] Vista generada; Q3 con ICAP numérico y CCL/LCR en `n.d.`.

## Fase 5 — Documentación

- [x] T010 — Reescribir `README.md` completo
  - Acceptance: misma estructura del README de SOFIPOS adaptada: Estructura
    (árbol + diagrama de dependencias, `entradas/` y `salidas/` no versionados),
    Requisitos, Instalación (Windows/macOS/Linux, venv, dependencias), MCP de
    Excel (opcional), Pruebas, Uso (ambos entry points), Opciones (`--entradas`,
    `--salidas`, `--out`, `--tablero`, `--anios`, `--pdf-icap`), Hojas del libro
    (7 fijas + vista), Fuente: tablero de la CNBV (tabla de conceptos con los
    códigos reales de `config.CONCEPTOS`), Unidades (millones), Método, columnas
    de `Datos Fuente` e `Indicadores`, Semáforos (umbrales vigentes),
    Validaciones, Cobertura y excepciones (ICAP vía PDF en septiembre), Cómo
    actualizar, Verificar que un cambio no altera el libro (Windows y
    macOS/Linux con `comparar.py`), Notas de mantenimiento y Fuentes (CNBV +
    Banxico). Sin restos de terminología SOFIPOS ni del PDF de agosto.
  - Verify:
    ```bash
    grep -n '^## ' README.md
    ! grep -qi 'sofipo' README.md
    ! grep -q '202608' README.md
    ```
  - Files: `README.md`.

## Fase 6 — Verificación global

- [x] T011 — Verificar todo y documentar los diffs esperados
  - Acceptance: `pytest` pasa y `pyflakes` sale limpio; corridas principal y de
    la vista sin errores; `comparar.py` (exit 1 esperado) muestra **solo** los
    diffs listados en el plan § "Diffs esperados": catálogo A:G, columna I de
    septiembre en `Datos Fuente 2026`, notas de fuente en las hojas,
    `2026 Q3` col E de la vista y Leyenda; `stdout` con el PDF nuevo y el
    mensaje de fuente PDF. Ningún diff en 2025 (salvo notas), en fórmulas de
    otros meses, en semáforos ni en nombres de hojas. Sin commit.
  - Verify:
    ```bash
    .venv/bin/pytest
    .venv/bin/pyflakes banca_multiple/ tests generar_banca_multiple.py generar_vista_copilot.py
    .venv/bin/python generar_banca_multiple.py --out /tmp/banca004/bancos.xlsx > /tmp/banca004/salida2.txt
    .venv/bin/python generar_vista_copilot.py --out /tmp/banca004/vista.xlsx > /tmp/banca004/vista_salida2.txt
    .venv/bin/python scripts/comparar.py \
      --xlsx-a /tmp/banca004/referencia.xlsx --xlsx-b /tmp/banca004/bancos.xlsx \
      --stdout-a /tmp/banca004/salida1.txt --stdout-b /tmp/banca004/salida2.txt
    .venv/bin/python scripts/comparar.py \
      --xlsx-a /tmp/banca004/vista_referencia.xlsx --xlsx-b /tmp/banca004/vista.xlsx \
      --stdout-a /tmp/banca004/vista_salida1.txt --stdout-b /tmp/banca004/vista_salida2.txt
    ```
  - Files: ninguno (solo lectura de salidas; revisar cada diff).

### Resultado de la verificación (T011)

- `pytest`: 127 passed. `pyflakes`: limpio. Corrida principal con
  `Validación general: OK` y `sin contraste en tablero · fuente PDF`; corrida de
  la vista sin errores. Sin commit ni push.
- `comparar.py` termina con exit 1 (esperado). Libro principal: **989 diffs**,
  todos en estas categorías:
  - `Catálogo` (231): `max_column` 8 → 7, celdas combinadas/anchos/filtro
    `A:H` → `A:G`, encabezados `D4:G4`, celdas `D5:G58` (categoría `I` del PDF
    y estatus/tipo/fecha recorridos una columna) y desaparición de la columna H.
  - `Datos Fuente 2026` (423): columna I (9) de las 54 filas de septiembre
    (fórmula → número del PDF) y columnas AJ/AK/AL (36–38) de agosto y
    septiembre (108 filas): al cambiar el PDF de agosto por el de septiembre,
    agosto pierde CCB/CCF/categoría y septiembre los gana. Es consecuencia
    directa del nuevo PDF, no un cambio de lógica. El resto son los
    desplazamientos de las notas (+1 fila).
  - `Datos Fuente 2025` (45), `Indicadores 2025` (32) e `Indicadores 2026`
    (32): únicamente el desplazamiento de las notas por `NOTA_ICAP_PDF` (+1
    fila); ninguna celda de datos ni fórmula cambia.
  - `stdout` (226): nombre del PDF y corte `202609`, y la sección de comparación
    ICAP/CCB/CCF sustituida por `sin contraste en tablero · fuente PDF`. El
    resto de las líneas coincide.
- Vista Copilot: **89 diffs**; `2026 Q3` columna E (54 filas, de `n.d.` a número
  del PDF) y `Leyenda` (35: nota nueva y desplazamiento de la tabla de
  medianas). `stdout` idéntico y los otros seis cortes, sin cambios.
- Fuera de esa lista no hay diffs: semáforos, fórmulas de otros meses, nombres
  de hojas ni datos de 2025.

## Cierre de hallazgos del reviewer

- [x] R1 — `docs/specs/README.md:10`: spec 004 marcada como `terminada`.
- [x] R2 — `README.md:27`: `7 hojas (Catálogo, 2 Datos Fuente, 2 Indicadores,
      Diccionario, Semáforos)` en vez de `7 hojas fijas + 2 por año`.
- [x] R3 — Artefactos por defecto regenerados con el código final (corridas sin
      `--out`). Verificado en `salidas/`: `Catálogo!D4 = Categoría` con 7 columnas
      A:G; el ICAP de septiembre es número en `Datos Fuente 2026!I437:I490` (la
      referencia `I433` del hallazgo es Santander de agosto y debe conservar la
      fórmula `H/G`); `2026 Q3!E5 = 2.5609` y `Leyenda!A8` contiene
      `NOTA_ICAP_PDF`.
- [x] R4 — `_tolera_dif` se conserva en `validacion_datos.py`: lo usan tres
      aserciones de `tests/test_validacion_datos.py`.

Verificación del cierre: `pytest` 127 passed; `pyflakes` limpio; cuatro corridas
(con y sin `--out`) con exit 0; `comparar.py` da `IDÉNTICO` entre dos corridas
del código final del libro principal y de la vista (misma ruta de salida). Sin
commit ni push.
