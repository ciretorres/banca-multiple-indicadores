# Plan de implementación: ICAP del PDF, vista Copilot y catálogo — V1

Spec: `docs/specs/004-icap-pdf-y-catalogo-banca/spec.md` (aprobada).

## Resumen

Tres cortes verticales: (1) usar el ICAP del PDF de septiembre cuando el tablero
no publique ese mes, (2) reducir el catálogo a 7 columnas con la categoría del
PDF y (3) reflejar todo eso en la vista Copilot. Después se reescribe el README
y se verifica con `pytest`, `pyflakes`, `comparar.py` y diffs esperados
documentados. No se hace `git commit` ni `git push`.

## Decisiones técnicas

1. **Dato del PDF en `filas.py`.** `preparar_filas` ya recibe `icap` y calcula
   `es_mes_pdf`; agregar el campo `icap_pdf` con el valor en **puntos** (20.43,
   no 0.2043) solo cuando el mes del PDF coincida y el tablero no traiga ICAP
   publicado para esa fecha. En los demás meses el campo queda `None` y no se
   toca ninguna columna. Los campos `ccb`, `ccf` y `categoria` siguen igual.

2. **Decisión en `datos_fuente.py`, no en `filas.py`.** La columna 9 sigue siendo
   `=IFERROR(H{r}/G{r},"n.d.")` salvo si `fila["icap_pdf"]` existe: entonces se
   escribe `_en_ratio(icap_pdf)` con `FMT_PORC`. Así se conserva la fórmula de
   los demás meses. `Indicadores` **no cambia su lógica**: su
   columna F ya apunta a `I` de `Datos Fuente` y recoge el número solo.

3. **Nota de fuente centralizada.** `config.NOTA_ICAP_PDF` con el texto exacto
   `ICAP: PDF de Banxico (tablero sin publicar ese mes)`, agregada vía `_notas`
   a `Datos Fuente` e `Indicadores`, igual que `NOTA_LIQUIDEZ`. El diff de notas
   queda documentado como esperado en ambos años.

4. **Validación sin contraste.** `_validar_icap_pdf` detecta primero si el tablero
   trae ICAP para la fecha del PDF. Si no lo trae, imprime
   `sin contraste en tablero · fuente PDF` y devuelve `True` (sin `DIF`); si lo
   trae, mantiene la comparación actual con tolerancia de 0.02 pts.

5. **Catálogo derivado de una sola lista.** `ENC_CATALOGO` pasa a 7 entradas;
   `catalogo.py` recibe `datos_icap` y toma la categoría por clave `040xxx`
   (`ND` si falta). `ncols`, `auto_filter`, notas y anchos se derivan de
   `len(ENC_CATALOGO)`. `escribir_xlsx` acepta `datos_icap=None` al final de la
   firma y `main.py` lo pasa por palabra clave: las llamadas existentes siguen
   funcionando.

6. **Vista Copilot.** En `_escribir_corte`, si la fila trae `icap_pdf`, se
   sobreescribe `valores["ICAP"] = icap_pdf / 100` (ratio para `FMT_PORC`); se
   elimina el `n.d.` forzado de ICAP en `2026 Q3` y se conserva el de
   `CCL/LCR`. La `Leyenda` incluye `NOTA_ICAP_PDF`. Los argumentos `--out` y el
   nombre de la vista no cambian.

7. **Línea base primero.** Generar referencia con el código actual (PDF de
   agosto) antes de borrar `entradas/ICAP_BM_202608.pdf`; no regenerarla después.
   `pdf_icap.py`, `generar_banca_multiple.py`, `generar_vista_copilot.py` y
   `scripts/comparar.py` no se tocan.

## Archivos a tocar

| Archivo | Cambio |
|---|---|
| `banca_multiple/config.py` | `PDF_ICAP` → `ICAP_BM_202609.pdf`; `NOTA_ICAP_PDF` |
| `banca_multiple/filas.py` | campo `icap_pdf` solo en el mes del PDF sin tablero |
| `banca_multiple/hojas/datos_fuente.py` | col 9: número vs fórmula; nota |
| `banca_multiple/hojas/indicadores.py` | nota de fuente (fórmulas intactas) |
| `banca_multiple/validacion_datos.py` | mensaje "sin contraste en tablero · fuente PDF" |
| `banca_multiple/estilos.py` | `ENC_CATALOGO` de 7 columnas |
| `banca_multiple/hojas/catalogo.py` | `datos_icap`; Categoría; sin Federación/Nivel |
| `banca_multiple/hojas/__init__.py`, `banca_multiple/main.py` | pasar `datos_icap` |
| `banca_multiple/validacion_libro.py` | verificar encabezados del catálogo |
| `banca_multiple/vista_copilot.py` | ICAP del PDF en Q3; Leyenda |
| `entradas/README.md` | ejemplo `202609`; borrar `entradas/ICAP_BM_202608.pdf` |
| `README.md` | reescritura completa con estructura SOFIPOS adaptada |
| `tests/test_{config,filas,hojas,validacion_datos,validacion_libro,vista_copilot}.py` | casos nuevos |

Sin cambios: `pdf_icap.py`, los dos scripts de entrada, `scripts/comparar.py`,
specs 001–003.

## Orden y dependencias

```
T001 línea base
 ├─ T002 config + nota ── T003 borrar PDF viejo
 ├─ T004 filas (icap_pdf) ── T005 hojas ── T006 validación
 │                       └─ T009 vista Copilot (requiere T002)
 └─ T007 catálogo ── T008 tests + validacion_libro
T010 README (independiente, después de T003)
T011 verificación global (requiere todo lo anterior)
```

Tareas detalladas en `task.md`. Máximo 4 archivos por tarea.

## Fases y checkpoints

### Fase 0 — Línea base (T001)

Capturar libro principal, vista y sus `stdout` con el código sin cambios y con
el PDF de agosto. Sin esta línea base no se pueden documentar los diffs.

### Fase 1 — Entrada del PDF (T002–T003)

**Checkpoint:** `pytest` y `pyflakes` limpios; el generador encuentra
`ICAP_BM_202609.pdf`; `entradas/README.md` ya no menciona el archivo viejo.

### Fase 2 — ICAP del PDF en el libro principal (T004–T006)

**Checkpoint:** corrida principal termina con `Validación general: OK`, imprime
`sin contraste en tablero · fuente PDF`, y la hoja `Datos Fuente 2026` tiene
número en la columna I de septiembre y fórmula en los otros meses.

### Fase 3 — Catálogo de 7 columnas (T007–T008)

**Checkpoint:** `validacion_libro` y los tests pasan; el libro se abre y el
catálogo muestra `I` en la categoría de los bancos del PDF.

### Fase 4 — Vista Copilot (T009)

**Checkpoint:** `2026 Q3` muestra ICAP numérico y CCL/LCR en `n.d.`; la Leyenda
explica la fuente alternativa; los otros seis cortes quedan iguales.

### Fase 5 — Documentación (T010)

**Checkpoint:** README con todas las secciones pedidas y conceptos copiados de
`config.CONCEPTOS` (no de SOFIPOS).

### Fase 6 — Verificación global (T011)

**Checkpoint:** `pytest`, `pyflakes`, ambas corridas y `comparar.py` con solo
los diffs esperados listados abajo.

## Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Escribir el número en la col 9 de todos los meses rompe la fórmula `H/G` | Alto | Condición `icap_pdf is not None` + campo solo en el mes del PDF sin ICAP publicado; test por mes |
| El PDF da puntos (20.43) y `FMT_PORC` espera ratio | Alto | `_en_ratio` en `Datos Fuente`, `/100` en la vista; test `0.2043` |
| Cambiar la col F de `Indicadores` a valor rompe la validación de fórmulas | Medio | No tocar esa fórmula: ya referencia la col I del libro principal |
| El tablero no trae septiembre y la validación imprimía un `OK` vacío | Medio | Rama "sin contraste" explícita, sin `DIF`; test con `capsys` |
| Catálogo 8 → 7 columnas desalinea encabezados, anchos, notas y filtro | Alto | Todo derivado de `ENC_CATALOGO`; test de encabezados exactos y `validacion_libro` |
| Bancos del PDF sin clave en el universo → categoría errónea | Medio | `datos_icap["bancos"].get(clave, {}).get("categoria", ND)`; total `5` no va al catálogo |
| Firma nueva de `escribir_xlsx` rompe llamadas existentes | Medio | Parámetro opcional al final, pasado por keyword desde `main.py` |
| README extenso con conceptos de SOFIPOS copiados por error | Medio | Usar los códigos reales de `config.CONCEPTOS` y revisar secciones con `grep '^## '` |
| Borrar el PDF viejo antes de tener referencia | Medio | T001 captura la línea base; T003 verifica que el PDF nuevo existe |
| `comparar.py` muestra diffs de notas, merges y anchos además de los datos | Medio | Documentarlos como esperados; exigir que 2025 y las fórmulas de otros meses no cambien |

## Verificación

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

En esta spec el exit 1 de `comparar.py` es esperado: se revisa cada diff, no se
exige `IDÉNTICO` ciego. En Windows usar `.venv\Scripts\python.exe`.

### Diffs esperados

- **Libro principal**
  - `Catálogo`: encabezados D–G, celdas D–G (categoría del PDF, estatus, tipo,
    fecha), celdas combinadas A1/A2/A3 y notas de A:H a A:G, anchos D–G,
    `max_column` 8 → 7 y `auto_filter` `A4:H58` → `A4:G58`; `max_row` si se
    agrega la nota de origen de la categoría.
  - `Datos Fuente 2026`: columna I de las 54 filas de septiembre (fórmula →
    número con `FMT_PORC`) y nota de fuente agregada al bloque final
    (`max_row` +1).
  - `Indicadores 2026`: nota de fuente agregada al bloque final (`max_row` +1);
    las fórmulas de la columna F no cambian.
  - `Datos Fuente 2025` e `Indicadores 2025`: solo la nota de fuente agregada
    (`max_row` +1).
  - `stdout`: nombre del PDF y corte `202609`, sección de ICAP con
    `sin contraste en tablero · fuente PDF` en vez de la comparación.
- **Vista Copilot**
  - `2026 Q3`: columna E (ICAP) de 54 filas, de `n.d.` a número del PDF.
  - `Leyenda`: nota de fuente agregada y, por eso, el bloque de medianas una
    fila más abajo (`max_row` y celdas A–C desde la nota en adelante).
  - Los otros seis cortes, idénticos.

Cualquier diff fuera de esta lista (por ejemplo, otra columna de `Datos Fuente`,
otro mes, semáforos o nombres de hojas) es un error a corregir antes de cerrar.
