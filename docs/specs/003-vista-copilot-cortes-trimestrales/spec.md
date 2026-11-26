# Spec: Vista para Copilot — cortes trimestrales — V1

Extensión de las specs 001 y 002, que entregan el libro principal de 7 hojas,
54 bancos, corte 2025–2026 y cifras en millones de pesos. Esta spec agrega un
**libro compañero compacto** para que Microsoft Copilot Cloud pueda leer los
indicadores completos. No cambia el libro principal ni su lógica.

## Objective

El libro principal `salidas/Bancos_Multiples_Indicadores_Datos.xlsx` funciona,
pero la herramienta `office365_open` de Copilot Cloud devuelve una representación
textual parcial: solo ve el inicio (enero) y el final (septiembre) de
`Indicadores 2026`, no el bloque intermedio (filas 383–436 = agosto). Además, las
celdas de indicadores son fórmulas sin valor cacheado, así que el lector cloud
las ve vacías. El archivo no está truncado (tiene 486 filas de datos, 5–490): es
una limitación de la vista del lector, no del libro.

Se genera un **libro compacto compañero**, separado del principal, con los 11
indicadores ya calculados como valores (números o `n.d.`), organizados por corte
trimestral, para que Copilot lo lea completo sin depender de un rango parcial ni
de fórmulas sin cachear.

- **Salida nueva:** `salidas/Bancos_Multiples_Cortes_Trimestrales.xlsx`. El libro
  principal no se modifica.
- **7 hojas de corte:** `2025 Q1`, `2025 Q2`, `2025 Q3`, `2025 Q4`, `2026 Q1`,
  `2026 Q2`, `2026 Q3`. Cada hoja corresponde al mes de cierre del trimestre
  (mar/jun/sep/dic) y contiene 54 filas, una por banco. Q3 2026 cierra en
  septiembre: ICAP y CCL/CFEN en `n.d.` por desfase de publicación.
- **Columnas:** `No.`, `Banco`, `Mes de corte`, `Trimestre` más los 11
  indicadores del libro (ICAP, IMOR, ICOR, ROA, ROE, MIN, Crec. captación,
  Crec. cartera, Crédito neto/captación, Índice de eficiencia, CCL/LCR).
- **Valores, no fórmulas:** los 11 indicadores se calculan en Python reutilizando
  la misma lógica de `hojas/indicadores.py` (o extrayéndola a una función
  compartida), y se escriben números o `n.d.`. No hay celdas vacías por falta de
  cacheo. MIN conserva la mediana de los 54 bancos del mes, incluidos negativos,
  como en la spec 001.
- **Hoja `Leyenda`:** definición de CCL/LCR y CFEN/NSFR, por qué son trimestrales
  y van con desfase (último dato `202606` → `n.d.` en sep-2026), explicación de
  `n.d.` y nota de MIN (publicado CNBV no ajustado frente al libro ajustado).

## Tech Stack

- Python ≥ 3.11, `openpyxl` ≥ 3.1 y < 4; `pytest` y `pyflakes` (dev). Sin
  dependencias nuevas.
- Reutiliza el paquete `banca_multiple/`: `config.py` (rutas, `MESES`, `ANIOS`,
  `ND`), `be.py`, `tablero.py`, `filas.py`, `pdf_icap.py` y
  `hojas/indicadores.py` (definición de los 11 indicadores y la mediana de MIN).
- Entradas (las mismas del libro principal, no versionadas):
  `entradas/BE BM 202609.xlsx`,
  `entradas/tablero/sh_datos_csv_40_i/040_TO.csv`, catálogos y
  `entradas/ICAP_BM_202608.pdf`.
- Salida: `salidas/Bancos_Multiples_Cortes_Trimestrales.xlsx`.
- MCP de Excel (`excel-mcp-server`) para inspeccionar el `.xlsx` generado.

## Commands

- Generar el libro compañero: `.venv/bin/python generar_vista_copilot.py`
- Generar (ruta exacta): `.venv/bin/python generar_vista_copilot.py --out RUTA`
- Ayuda: `.venv/bin/python generar_vista_copilot.py --help`
- Pruebas: `.venv/bin/pytest`
- Lint: `.venv/bin/pyflakes banca_multiple/ tests generar_vista_copilot.py`
- Verificar que el libro principal no cambia (→ `IDÉNTICO`, exit 0): ver
  `AGENTS.md` § "Verificar un cambio". En Windows usar
  `.venv\Scripts\python.exe`.

## Project Structure

```
generar_banca_multiple.py        # sin cambios (entry point del libro principal)
generar_vista_copilot.py         # nuevo: entry point del libro compañero (--out, --help)
banca_multiple/
  config.py                      # editar: ruta de salida y cortes trimestrales si aplica
  vista_copilot.py               # nuevo (p. ej.): arma las 7 hojas de corte + Leyenda
  be.py, tablero.py, filas.py, pdf_icap.py   # reutilizar sin cambiar su CLI
  hojas/indicadores.py           # reutilizar la lógica de los 11 indicadores y MIN
tests/
  test_vista_copilot.py          # nuevo: hojas, filas, columnas, sin fórmulas, n.d., CLI
salidas/
  Bancos_Multiples_Indicadores_Datos.xlsx    # sin cambios
  Bancos_Multiples_Cortes_Trimestrales.xlsx  # nuevo
docs/specs/003-vista-copilot-cortes-trimestrales/
  spec.md                        # este ciclo (plan.md y task.md tras aprobación)
```

## Code Style

- Español; seguir los patrones de las specs 001/002: configuración central en
  `config.py`, módulos pequeños por responsabilidad, docstrings solo cuando
  aporten y `ND = "n.d."` para datos no disponibles.
- Reutilizar `preparar_filas` y las mismas definiciones de los 11 indicadores de
  `hojas/indicadores.py`. Extraer a una función compartida solo si hace falta,
  sin duplicar la lógica ni alterar el libro principal.
- Encabezados de cada hoja de corte, en este orden (15 columnas):

  ```python
  ["No.", "Banco", "Mes de corte", "Trimestre",
   "ICAP", "IMOR", "ICOR", "ROA", "ROE", "MIN",
   "Crec. captación", "Crec. cartera", "Crédito neto/captación",
   "Índice de eficiencia", "CCL/LCR"]
  ```

- Los porcentajes se escriben como el mismo valor numérico y escala del libro
  principal con `FMT_PORC` (el ratio, no puntos porcentuales); los no disponibles
  van como texto `n.d.`. Sin celdas vacías en las columnas de indicadores.
- Cero fórmulas en el libro compañero: toda celda de datos debe cumplir
  `cell.data_type != "f"`.
- `pyflakes` limpio sobre `banca_multiple/`, `tests/` y el nuevo script.

## Testing Strategy

- `pytest` sobre `tests/` y `pyflakes` sobre los archivos tocados.
- `tests/test_vista_copilot.py`:
  - las 7 hojas de corte con nombres exactos y `Leyenda` al final;
  - cada hoja de corte con 54 filas de datos (una por banco) y las 15 columnas
    indicadas;
  - cero fórmulas: `cell.data_type != "f"` en todo el rango de datos;
  - Q3 2026 con ICAP y CCL/LCR en `n.d.` por desfase de publicación;
  - MIN acorde con el cálculo del libro principal (mediana de los 54 bancos del
    mes, negativos incluidos);
  - `--help` documenta `--out` y `--out RUTA` respeta la ruta dada, sin tocar la
    CLI de `generar_banca_multiple.py`.
- `scripts/comparar.py` sobre el libro principal → `IDÉNTICO` (esta spec no
  cambia el libro principal).
- Revisión manual: abrir el libro nuevo y confirmar que se leen completas las 7
  hojas de corte y que no hay celdas vacías por falta de valor cacheado.

## Boundaries

- **Always:** no modificar el libro principal ni su CLI; escribir valores
  (números o `n.d.`), nunca fórmulas, en el libro compañero; usar `ND = "n.d."`;
  ejecutar `pytest` y `pyflakes` antes de cerrar; verificar `comparar.py` →
  `IDÉNTICO` en el libro principal.
- **Ask first:** cambiar el universo de 54 bancos, los cortes trimestrales, la
  lista de 11 indicadores, el nombre de las hojas o del archivo de salida;
  extraer la lógica de indicadores a un módulo compartido que afecte al libro
  principal.
- **Never:** tocar `generar_banca_multiple.py` ni su CLI; editar `entradas/`;
  hardcodear rutas absolutas; hacer `git commit` ni `git push`; incluir
  CCB/CCF/Categoría ni el total `5`/grupos `59`–`64` en el libro compañero;
  inventar datos para septiembre de 2026.

## Success Criteria

- `.venv/bin/python generar_vista_copilot.py --help` funciona y documenta
  `--out`; `pyflakes` sale limpio y `pytest` pasa.
- Existe `salidas/Bancos_Multiples_Cortes_Trimestrales.xlsx` con las hojas
  `2025 Q1` a `2026 Q3` y `Leyenda`.
- Cada hoja de corte tiene exactamente 54 filas de datos y 15 columnas (`No.`,
  `Banco`, `Mes de corte`, `Trimestre` + 11 indicadores).
- Todas las celdas de indicadores son valores numéricos o `n.d.`: cero fórmulas
  (`data_type != "f"`) y cero celdas vacías por falta de cacheo.
- Q3 2026 (septiembre) tiene ICAP y CCL/LCR en `n.d.` por desfase de publicación.
- MIN se calcula con la misma lógica que el libro principal (mediana de los 54
  bancos del mes, negativos incluidos).
- La hoja `Leyenda` incluye: definición de CCL/LCR y CFEN/NSFR, por qué son
  trimestrales y van con desfase (último dato `202606` → `n.d.` en sep-2026),
  explicación de `n.d.` y la nota de MIN (publicado CNBV no ajustado frente al
  libro ajustado).
- El libro principal no cambia: `generar_banca_multiple.py` y su CLI siguen
  intactos y `scripts/comparar.py` devuelve `IDÉNTICO` frente a la referencia.

## Out of Scope (Deferred)

- Modificar el libro principal ni las specs 001/002.
- Incluir CCB/CCF/Categoría: la fuente PDF es de agosto y no encaja con los
  cortes mar/jun/sep/dic.
- Llenar el ICAP de septiembre de 2026 (desfase de publicación).
- Explicar o defender el comportamiento de Copilot: solo se genera el archivo
  compatible.
- Cambiar la CLI de `generar_banca_multiple.py`.
- Semáforos o colores propios en el libro compañero: la vista solo muestra
  valores.

## Open Questions

- ¿Las hojas llevan el sufijo en el mes de corte ("Septiembre 2026") o solo el
  número de trimestre? (asumir columna "Mes de corte" con texto).
- ¿La Leyenda va como primera o última hoja? (asumir última, para que las 7 de
  corte queden juntas al inicio).
