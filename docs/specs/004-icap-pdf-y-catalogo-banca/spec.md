# Spec: ICAP del PDF, vista Copilot y catálogo — V1

Extensión de las specs 001, 002 y 003. El libro principal
(`salidas/Bancos_Multiples_Indicadores_Datos.xlsx`) y la vista Copilot
(`salidas/Bancos_Multiples_Cortes_Trimestrales.xlsx`) funcionan, pero el tablero
de la CNBV viene desfasado: el CSV descargable `040_TO.csv` sigue siendo el de
26-oct (ICAP/capital neto/activos ponderados hasta `202608`, CCL/CFEN hasta
`202606`), mientras el Power BI en línea ya muestra ICAP de septiembre. El
usuario subió `entradas/ICAP_BM_202609.pdf` (Banxico, cifras al 30-sep-2026,
publicado 12-nov-2026); el lector actual `pdf_icap.py` lo parsea sin cambios
(54 bancos + Total, ICAP/CCB/CCF/Categoría, todos en `I`).

## Objective

1. **ICAP del PDF cuando falte en el tablero.** Configurar
   `PDF_ICAP = ICAP_BM_202609.pdf` y eliminar `entradas/ICAP_BM_202608.pdf` (ya
   no se necesita). En `filas.py`, para el mes del PDF sin dato en el tablero,
   escribir el ICAP del PDF como **valor numérico** en `Datos Fuente` (columna 9,
   `ICAP (%)`) en vez de `n.d.` o de la fórmula `H/G`. La celda lleva una nota
   visible de fuente: `ICAP: PDF de Banxico (tablero sin publicar ese mes)`. En
   los meses con dato del tablero se conserva la fórmula actual.

   - Referencias del PDF nuevo: Total ICAP 20.43, Ualá 28.83, BBVA 19.52,
     Santander 19.13 (puntos porcentuales; se escriben como ratio para `FMT_PORC`).
   - `_validar_icap_pdf` imprime `sin contraste en tablero · fuente PDF` cuando
     el mes del PDF no exista en el tablero, en lugar de un `OK` vacío. Cuando
     sí exista, compara ICAP/CCB/CCF con tolerancia de 0.02 pts como hoy.

2. **Vista Copilot (spec 003).** Quitar el `n.d.` forzado de ICAP en `2026 Q3`;
   usar el ICAP del PDF para ese corte (CCL/LCR sigue en `n.d.` por desfase).
   Actualizar la hoja `Leyenda` para documentar la fuente alternativa.

3. **Catálogo de 7 columnas.** Quitar **Federación**; cambiar **Nivel →
   Categoría** y llenarla con la categoría del PDF (`I` para los 54 bancos,
   `n.d.` si falta). Columnas finales: `No.`, `Clave CASFIM`, `Banco`,
   `Categoría`, `Estatus`, `Tipo`, `Fecha de Autorización`. Ajustar
   `ENC_CATALOGO`, `hojas/catalogo.py` (recibir `datos_icap`), la firma de
   `escribir_xlsx` y su llamada en `main.py`, `validacion_libro`, tests y README.

4. **README.md completo.** Reescribir con la **misma estructura del README de
   SOFIPOS** (repositorio hermano), adaptada a Banca Múltiple:

   - Título e intro; **Estructura** (árbol de carpetas + diagrama de
     dependencias, con `entradas/` y `salidas/` no versionados); **Requisitos**;
     **Instalación** (Windows/macOS/Linux, entorno virtual, dependencias); **MCP
     de Excel (opcional)**; **Pruebas**; **Uso** (ambos entry points:
     `generar_banca_multiple.py` y `python -m banca_multiple`); **Opciones**
     (`--entradas`, `--salidas`, `--out`, `--tablero`, `--anios`, `--pdf-icap`);
     **Hojas del libro** (7 fijas: Catálogo, Datos Fuente×2, Indicadores×2,
     Diccionario, Semáforos; más la vista Copilot separada); **Fuente: tablero
     de la CNBV** (tabla de conceptos abajo); **Unidades**; **Método**; tablas
     de columnas de `Datos Fuente` e `Indicadores`; **Semáforos**; **Validaciones
     que corre el script**; **Cobertura y excepciones conocidas**; **Cómo
     actualizar**; **Verificar que un cambio no altera el libro** (`comparar.py`,
     comandos Windows y macOS/Linux); **Notas de mantenimiento**; **Fuentes**
     (CNBV + Banxico).
   - Conceptos CNBV a documentar (códigos reales de `config.CONCEPTOS`):

     | Dato | Código | Dato | Código |
     |---|---|---|---|
     | Capital neto | `4030211` | Activos sujetos a riesgo | `4030249` |
     | ICAP | `4021750` | CCB / CCF | `4021754` / `4021755` |
     | IMOR | `40200017` | ICOR | `40200096` |
     | ROA / ROE | `40200001` / `40200002` | MIN | `4040001` |
     | Cartera total | `40100185` | Cartera etapa 3 | `40100341` |
     | Estimaciones | `40100031` | Resultado neto | `40100013` |
     | Resultado 12M | `40200015` | Activo promedio 12M | `40200004` |
     | Capital promedio 12M | `40200005` | Margen ajustado | `40100009` |
     | Margen ajustado 12M | `40200011` | Activo prod. promedio 12M | `40200240` |
     | Captación tradicional | `40100085` | Captación total | `40100042` |
     | Gastos de administración | `40100011` | Ingresos de operación | `40100170` |
     | CCL | `601` | CFEN | `610` |

   - **Unidades: millones de pesos** (el tablero publica en pesos; se divide
     entre 1,000,000). **Método:** periodicidad mensual con columna
     `Trimestre`; cortes trimestrales mar/jun/sep/dic; `tipo_saldo =
     Consolidado con SOFOMER`; 54 bancos, con el total `5` y los grupos `59`–`64`
     solo para validación; estados de resultados en YTD.
   - **Semáforos** (umbrales vigentes, sin cambios): ICAP ≥12 / 10–12 / <10;
     IMOR ≤3 / >3–5 / >5; ICOR ≥100 / 80–100 / <80; ROA ≥1 / >0–1 / ≤0; ROE
     ≥15 / >0–15 / ≤0; MIN vs mediana de los 54 (≥100% / 80–100% / <80%);
     crecimiento nominal (>0 / =0 / <0); crédito/captación 70–90%; eficiencia
     ≤55 / 55–70 / >70 (con `n.a.` en rojo); CCL ≥120 / 100–120 / <100.
   - **Validaciones:** consistencia del total `5` y de los grupos `59`–`64`,
     ROA/ROE contra el BE, IMOR/ICOR y CCB/CCF contra publicados, ICAP/CCB/CCF
     contra el PDF, y estructura del libro.
   - **Cobertura y excepciones:** ICAP vía PDF en septiembre (tablero sin
     publicar), CCL/CFEN trimestrales con desfase (`202606`), MIN publicado no
     ajustado frente al libro ajustado, `n.d.` y `n.a.`.

5. **Verificación.** `pytest` y `pyflakes` limpios; corrida principal y de la
   vista Copilot; `scripts/comparar.py` documentando los diffs esperados (ICAP
   de septiembre, catálogo de 7 columnas, README y Leyenda).

## Tech Stack

- Python ≥ 3.11, `openpyxl` ≥ 3.1 y < 4, `pypdf`, `pytest` y `pyflakes`. Sin
  dependencias nuevas.
- Reutiliza `banca_multiple/`: `config.py`, `pdf_icap.py` (sin cambios: ya lee
  el PDF nuevo), `filas.py`, `hojas/catalogo.py`, `hojas/datos_fuente.py`,
  `hojas/indicadores.py`, `validacion_datos.py`, `validacion_libro.py` y
  `vista_copilot.py`.
- Entradas: `entradas/ICAP_BM_202609.pdf` (nueva, presente), `entradas/BE BM
  202609.xlsx`, `entradas/tablero/sh_datos_csv_40_i/040_TO.csv` y catálogos.
- Salidas: `salidas/Bancos_Multiples_Indicadores_Datos.xlsx` y
  `salidas/Bancos_Multiples_Cortes_Trimestrales.xlsx`.

## Commands

- Generar el libro principal: `.venv/bin/python generar_banca_multiple.py`
- Generar con otra ruta: `.venv/bin/python generar_banca_multiple.py --out RUTA`
- Generar con otro PDF: `.venv/bin/python generar_banca_multiple.py --pdf-icap RUTA`
- Wrapper equivalente: `python -m banca_multiple`
- Ayuda: `.venv/bin/python generar_banca_multiple.py --help`
- Generar la vista Copilot: `.venv/bin/python generar_vista_copilot.py` (ídem
  `--out RUTA` y `--help`)
- Pruebas: `.venv/bin/pytest`
- Lint: `.venv/bin/pyflakes banca_multiple/ tests generar_banca_multiple.py generar_vista_copilot.py`
- Comparar: `.venv/bin/python scripts/comparar.py --xlsx-a A --xlsx-b B`
  (opcionalmente `--stdout-a`/`--stdout-b`, con ambas corridas en la misma ruta).
- En Windows usar `.venv\Scripts\python.exe`; detalle en `AGENTS.md` §
  "Verificar un cambio" y en el README § "Verificar que un cambio no altera el
  libro".

## Project Structure

```
generar_banca_multiple.py        # sin cambios
generar_vista_copilot.py         # sin cambios
banca_multiple/
  config.py                      # editar: PDF_ICAP → ICAP_BM_202609.pdf; nota de fuente ICAP
  pdf_icap.py                    # sin cambios (parsea el PDF nuevo tal cual)
  filas.py                       # editar: ICAP del PDF como dato en el mes sin tablero
  estilos.py                     # editar: ENC_CATALOGO (7 columnas)
  hojas/__init__.py              # editar: pasar datos_icap a escribir_catalogo
  hojas/catalogo.py              # editar: recibir datos_icap; Categoría del PDF; sin Federación
  hojas/datos_fuente.py          # editar: valor ICAP del PDF en col 9 + nota de fuente
  hojas/indicadores.py           # editar: nota de fuente ICAP (asumir ambas hojas)
  validacion_datos.py            # editar: mensaje "sin contraste en tablero · fuente PDF"
  validacion_libro.py            # editar: verificar encabezados del catálogo de 7 columnas
  main.py                        # editar: pasar datos_icap a escribir_xlsx
  vista_copilot.py               # editar: Q3 sin n.d. forzado de ICAP; Leyenda
entradas/
  ICAP_BM_202608.pdf             # eliminar
  ICAP_BM_202609.pdf             # ya presente (sin cambios)
  README.md                      # editar: quitar referencia al PDF viejo (asumir)
tests/
  test_config.py, test_filas.py, test_hojas.py          # editar
  test_validacion_datos.py, test_validacion_libro.py    # editar
  test_vista_copilot.py                                 # editar
README.md                        # reescribir completo (estructura SOFIPOS adaptada)
docs/specs/004-icap-pdf-y-catalogo-banca/
  spec.md                        # este ciclo (plan.md y task.md tras aprobación)
```

## Code Style

- Español; configuración central en `config.py`, módulos pequeños por
  responsabilidad, docstrings solo cuando aporten y `ND = "n.d."`.
- La nota de fuente se define en `config.py` (como `NOTA_LIQUIDEZ`) y se agrega
  con `_notas` en las hojas; los porcentajes del PDF se convierten con
  `_en_ratio` (20.43 → 0.2043) y se escriben con `FMT_PORC`.
- En `Datos Fuente`, la columna 9 sigue siendo fórmula salvo en el mes del PDF
  sin tablero, donde se escribe el número:

  ```python
  if fila.get("icap_pdf") is not None:
      _celda_numero(ws, r, 9, _en_ratio(fila["icap_pdf"]), FMT_PORC)
  else:
      _celda_formula(ws, r, 9, f'=IFERROR(H{r}/G{r},"{ND}")', FMT_PORC)
  ```

- Catálogo: `ENC_CATALOGO` con 7 entradas y la categoría del PDF por clave
  `040xxx` (`datos_icap["bancos"][clave]["categoria"]`, `ND` si falta). La
  categoría va como texto centrado, igual que `Estatus`/`Tipo`.
- `pyflakes` limpio sobre `banca_multiple/`, `tests/` y los dos scripts.

## Testing Strategy

- `pytest` sobre `tests/` y `pyflakes` sobre los archivos tocados.
- `test_config.py`: `PDF_ICAP == "ICAP_BM_202609.pdf"` y nota de fuente presente.
- `test_filas.py`: mes del PDF sin tablero → campo de ICAP del PDF como número;
  demás meses → sin valor PDF; categoría por banco para el catálogo.
- `test_hojas.py` / `test_validacion_libro.py`: `Datos Fuente` col 9 numérica solo
  en septiembre y fórmula en el resto; nota visible de fuente; catálogo con 7
  encabezados exactos y `Categoría = I` / `n.d.`.
- `test_validacion_datos.py`: con tablero sin el mes del PDF, imprime
  `sin contraste en tablero · fuente PDF` y no marca `DIF`; con tablero
  presente, mantiene la comparación de 0.02 pts.
- `test_vista_copilot.py`: `2026 Q3` con ICAP del PDF (no `n.d.`), CCL/LCR en
  `n.d.`, y `Leyenda` con la nota de fuente alternativa.
- `scripts/comparar.py`: en esta spec los diffs esperados son el ICAP de
  septiembre (valor en vez de `n.d.`/fórmula), las notas de fuente, el catálogo
  de 7 columnas y la Leyenda; documentarlos en vez de exigir `IDÉNTICO` ciego.
  El resto (hojas, filas, semáforos, fórmulas de otros meses) no cambia.

## Boundaries

- **Always:** derivar el mes del corte del nombre del PDF; usar `ND = "n.d."`
  y notas visibles para documentar la fuente alternativa; ejecutar `pytest` y
  `pyflakes` antes de cerrar; documentar cualquier diferencia del libro y de la
  vista frente a la referencia con `comparar.py`.
- **Ask first:** cambiar umbrales de semáforo, tolerancias o reglas de
  validación distintas de las indicadas; cambiar el universo de 54 bancos, el
  total `5`, los grupos `59`–`64`, los nombres de hojas o de archivos de salida;
  borrar otros archivos de `entradas/`.
- **Never:** editar el CSV del tablero; llenar CCL/CFEN de septiembre; inventar
  datos; hardcodear rutas absolutas; tocar las specs 001–003; hacer `git commit`
  ni `git push`.

## Success Criteria

- `PDF_ICAP = ICAP_BM_202609.pdf`; `entradas/ICAP_BM_202608.pdf` ya no existe y
  `entradas/README.md` no lo menciona. `pytest` pasa y `pyflakes` sale limpio.
- El mes del PDF sin dato en el tablero muestra el ICAP del PDF como número en
  `Datos Fuente` col 9 (Total 20.43, Ualá 28.83, BBVA 19.52, Santander 19.13,
  como ratios), con la nota `ICAP: PDF de Banxico (tablero sin publicar ese
  mes)`; los demás meses conservan la fórmula `H/G`.
- `_validar_icap_pdf` imprime `sin contraste en tablero · fuente PDF` para ese
  mes, sin marcar `DIF`; cuando el tablero tenga el dato, la comparación sigue
  con tolerancia 0.02 pts. La corrida termina con `Validación general: OK`.
- La vista Copilot tiene ICAP del PDF en `2026 Q3` (no `n.d.`), CCL/LCR en
  `n.d.`, y la `Leyenda` documenta la fuente alternativa.
- El catálogo tiene exactamente 7 columnas, sin `Federación`, con `Nivel`
  renombrado a `Categoría` y valores `I`/`n.d.` del PDF; `validacion_libro` y los
  tests reflejan esa estructura.
- `README.md` sigue la estructura del README de SOFIPOS adaptada a Banca
  Múltiple e incluye todos los contenidos del Objective § 4.
- `scripts/comparar.py` muestra solo los diffs esperados (ICAP de septiembre,
  notas, catálogo de 7 columnas, Leyenda); el resto del libro queda idéntico.

## Out of Scope (Deferred)

- Cambiar el CSV del tablero: el usuario lo actualizará cuando la CNBV publique
  los datos de septiembre.
- Llenar CCL/CFEN de septiembre: el tablero solo trae hasta `202606`.
- Cambiar umbrales del semáforo ni reglas de validación distintas de las
  indicadas.

## Open Questions

- ¿La nota de fuente ICAP va en `Datos Fuente` y en `Indicadores`, o solo en
  `Datos Fuente`? (asumir ambas, como el resto de notas).
- ¿El catálogo conserva `Tipo` y `Fecha de Autorización` aunque queden en
  `n.d.`? (asumir sí; solo se quita `Federación` y se renombra `Nivel`).
- ¿Borrar el PDF viejo también del índice de `entradas/README.md`? (asumir sí).
