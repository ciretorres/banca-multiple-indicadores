# Banca Múltiple · Generador de datos e indicadores

Programa que arma un solo libro de Excel con la Banca Múltiple supervisada por
la CNBV: 54 bancos autorizados en operación, catálogo, cifras mensuales por año,
indicadores, diccionario y semáforos. Un segundo libro companion reúne los
cortes trimestrales en valores para que Copilot los lea sin depender de fórmulas.

Las cifras financieras vienen del **tablero mensual de la CNBV** (`040_TO.csv`)
y del **boletín electrónico** (`BE BM YYYYMM.xlsx`, que aporta el universo y el
ROA/ROE publicados). El ICAP, CCB y CCF de septiembre de 2026 se toman del
**PDF de Banco de México**, porque el tablero aún no publica ese mes.

## Estructura

```
banca-multiple-indicadores/
├── entradas/                                 datos de CNBV y Banxico (no versionado)
│   ├── tablero/
│   │   └── sh_datos_csv_40_i/
│   │       ├── 040_TO.csv                    fuente mensual (en pesos)
│   │       ├── catalogo_conceptos_040.xlsx   catálogo de conceptos
│   │       └── catalogo_instituciones_040.csv
│   ├── BE BM 202609.xlsx                     universo y ROA/ROE publicados
│   ├── ICAP_BM_202609.pdf                    ICAP/CCB/CCF del corte 202609
│   └── README.md                             cómo reconstruir esta carpeta
├── salidas/                                  libros generados (no versionado)
│   ├── Bancos_Multiples_Indicadores_Datos.xlsx         7 hojas (Catálogo, 2 Datos Fuente, 2 Indicadores, Diccionario, Semáforos)
│   └── Bancos_Multiples_Cortes_Trimestrales.xlsx       7 cortes + Leyenda
├── generar_banca_multiple.py                 punto de entrada (wrapper)
├── generar_vista_copilot.py                  punto de entrada de la vista
├── pyproject.toml                            metadatos, dependencias, CLI y pytest
├── banca_multiple/                           todo el código del generador
│   ├── __main__.py                           permite `python -m banca_multiple`
│   ├── main.py                               CLI (argparse) y orquestación
│   ├── config.py                             rutas, ANIOS, CONCEPTOS, ND y notas
│   ├── utilidades.py                         fechas, números, normalización
│   ├── xlsx_lector.py                        lee .xlsx con zipfile + ElementTree
│   ├── be.py                                 boletín BE: universo y ROA/ROE
│   ├── tablero.py                            lee el CSV mensual (040_TO.csv)
│   ├── pdf_icap.py                           lee el PDF de ICAP de Banxico
│   ├── filas.py                              arma las filas de cada año
│   ├── validacion_datos.py                   validaciones contra BE, tablero y PDF
│   ├── estilos.py                            paleta, formatos, encabezados y helpers
│   ├── fichas.py                             FICHAS: diccionario y semáforos
│   ├── hojas/                                escritura de las hojas
│   │   ├── __init__.py                       escribir_xlsx (orden de hojas)
│   │   ├── catalogo.py                       Catálogo: 7 columnas
│   │   ├── datos_fuente.py                   Datos Fuente {año}
│   │   ├── indicadores.py                    Indicadores {año} + formato condicional
│   │   ├── diccionario.py                    Diccionario
│   │   └── semaforos.py                      Semáforos
│   ├── validacion_libro.py                   valida el .xlsx generado
│   └── vista_copilot.py                      libro de cortes trimestrales en valores
├── scripts/
│   └── comparar.py                           compara dos libros y dos stdout
├── tests/
│   ├── fixtures/
│   │   └── tablero_mini.csv                  CSV mini versionado (no usa entradas/)
│   ├── test_config.py, test_cli.py, test_filas.py, test_hojas.py
│   ├── test_be.py, test_tablero.py, test_pdf_icap.py, test_utilidades.py
│   ├── test_indicadores_valores.py, test_semaforos.py
│   └── test_validacion_datos.py, test_validacion_libro.py, test_vista_copilot.py
├── docs/specs/                               specs, planes y tareas del ciclo
└── README.md
```

Cada archivo tiene una sola responsabilidad y solo importa de capas
anteriores (no hay imports circulares):

```
config ← utilidades ← xlsx_lector ← be / tablero / pdf_icap ← filas ← validacion_datos
   ↑                                                               ↑
estilos ← fichas ← hojas/* ← validacion_libro ← main ← generar_banca_multiple.py
                        └─ vista_copilot ← generar_vista_copilot.py
```

`entradas/` y `salidas/` están en `.gitignore` porque pesan decenas de MB y los
datos los publica la CNBV (el PDF de ICAP, Banxico). Para reconstruir la carpeta
de entrada, sigue las instrucciones de [`entradas/README.md`](entradas/README.md).

## Requisitos

- Python 3.11 o superior. En Windows usa `python`; en macOS y Linux, `python3`.
- [`openpyxl`](https://openpyxl.readthedocs.io/) 3.1+ y
  [`pypdf`](https://pypi.org/project/pypdf/) 5+ (dependencias en `pyproject.toml`).
- `pytest` y `pyflakes` para pruebas y lint (extra `dev`).

## Instalación

```bash
git clone https://github.com/ciretorres/banca-multiple-indicadores.git
cd banca-multiple-indicadores
```

### Crear el entorno virtual

**Windows** (PowerShell o CMD):

```powershell
python -m venv .venv
```

**macOS / Linux**:

```bash
python3 -m venv .venv
```

### Instalar dependencias

**Windows**:

```powershell
.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

**macOS / Linux**:

```bash
.venv/bin/pip install -e ".[dev]"
```

### MCP de Excel (opcional)

Para que OpenCode o Claude Code lean los `.xlsx` con el MCP de Excel se instala
`uv` (comando en `AGENTS.md` § MCP de Excel); el generador no lo necesita. La
configuración del servidor está en `opencode.jsonc`. Los libros de la CNBV traen
relaciones `../customXml/…` fuera del paquete: con ellos `describe_workbook`
falla (usa `read_range` o `openpyxl` directo); los libros de `salidas/` se leen
completos.

## Pruebas

**Windows**:

```powershell
.venv\Scripts\python.exe -m pytest
.venv\Scripts\python.exe -m pyflakes banca_multiple tests generar_banca_multiple.py generar_vista_copilot.py
```

**macOS / Linux**:

```bash
.venv/bin/python -m pytest
.venv/bin/pyflakes banca_multiple/ tests generar_banca_multiple.py generar_vista_copilot.py
```

Los tests (en `tests/`) usan un CSV mini versionado y no requieren las carpetas
`entradas/` ni `salidas/`, excepto la prueba del PDF real, que se omite si el
archivo no está.

## Uso

Descarga primero los datos de entrada (ver
[`entradas/README.md`](entradas/README.md)) y ejecuta desde la raíz del
repositorio. Sale con código 0 cuando todas las validaciones pasan.

Hay dos formas de invocar el generador principal (hacen exactamente lo mismo):

**Windows**:

```powershell
.venv\Scripts\python.exe generar_banca_multiple.py
.venv\Scripts\python.exe -m banca_multiple
```

**macOS / Linux**:

```bash
.venv/bin/python generar_banca_multiple.py
.venv/bin/python -m banca_multiple
```

### Vista Copilot (libro compañero)

`generar_vista_copilot.py` crea
`salidas/Bancos_Multiples_Cortes_Trimestrales.xlsx`: siete cortes trimestrales
(`2025 Q1` a `2026 Q3`) con 54 bancos cada uno y los 11 indicadores escritos como
valores (números o `n.d.`/`n.a.`), sin fórmulas ni celdas vacías por falta de
valor cacheado; termina con una hoja `Leyenda`. El libro principal no se modifica.

**Windows**:

```powershell
.venv\Scripts\python.exe generar_vista_copilot.py
.venv\Scripts\python.exe generar_vista_copilot.py --out ruta\exacta.xlsx
```

**macOS / Linux**:

```bash
.venv/bin/python generar_vista_copilot.py
.venv/bin/python generar_vista_copilot.py --out ruta/exacta.xlsx
```

En `2026 Q3` el ICAP sale del PDF de septiembre y `CCL/LCR` sigue en `n.d.` por
el desfase del tablero. La `Leyenda` explica esa fuente alternativa.

## Opciones

Las opciones del generador principal son iguales en las dos formas de invocarlo:

**Windows**:

```powershell
.venv\Scripts\python.exe generar_banca_multiple.py --entradas otra_carpeta
.venv\Scripts\python.exe generar_banca_multiple.py --salidas otra_carpeta
.venv\Scripts\python.exe generar_banca_multiple.py --out ruta\exacta.xlsx
.venv\Scripts\python.exe generar_banca_multiple.py --tablero ruta\040_TO.csv
.venv\Scripts\python.exe generar_banca_multiple.py --anios 2026
.venv\Scripts\python.exe generar_banca_multiple.py --pdf-icap ruta\ICAP_BM_202609.pdf
```

**macOS / Linux**:

```bash
.venv/bin/python generar_banca_multiple.py --entradas otra_carpeta
.venv/bin/python generar_banca_multiple.py --salidas otra_carpeta
.venv/bin/python generar_banca_multiple.py --out ruta/exacta.xlsx
.venv/bin/python generar_banca_multiple.py --tablero ruta/040_TO.csv
.venv/bin/python generar_banca_multiple.py --anios 2026
.venv/bin/python generar_banca_multiple.py --pdf-icap ruta/ICAP_BM_202609.pdf
```

| Opción | Qué hace |
|---|---|
| `--entradas` | Carpeta con el BE, el PDF y la carpeta `tablero/`. |
| `--salidas` | Carpeta donde se escribe el libro (nombre fijo). |
| `--out` | Ruta exacta del `.xlsx`; tiene prioridad sobre `--salidas`. |
| `--tablero` | Ruta exacta de `040_TO.csv`. |
| `--anios` | Año (`2026`) o rango (`2025-2026`); por defecto los de `ANIOS`. |
| `--pdf-icap` | Ruta exacta del PDF; por defecto `ICAP_BM_202609.pdf` en `entradas/`. |

`--anios` solo admite años presentes en `ANIOS`; un año fuera de la configuración
termina con un mensaje de error. Un mes del PDF fuera de los años generados
también se rechaza. La vista Copilot acepta `--out` y `--help`.

## Hojas del libro

La estructura es fija: **7 hojas** (1 catálogo, 2 de datos, 2 de indicadores,
diccionario y semáforos), más la vista separada descrita arriba.

| Hoja | Contenido |
|---|---|
| `Catálogo` | 54 bancos: No., Clave CASFIM, Banco, Categoría, Estatus, Tipo y Fecha de Autorización; al final, notas de origen. |
| `Datos Fuente 2026` | 38 columnas: cifras mensuales enero–septiembre de 2026, 54 bancos por mes. |
| `Indicadores 2026` | 16 columnas visibles + mediana oculta (Q): indicadores por fórmula contra `Datos Fuente` del mismo año. |
| `Datos Fuente 2025` | Ídem para enero–diciembre de 2025. |
| `Indicadores 2025` | Ídem para 2025. |
| `Diccionario` | 11 indicadores: fórmula, grupo de razón financiera y descripción. |
| `Semáforos` | 11 bloques y 34 reglas de formato condicional. |

El orden de datos e indicadores es 2026 y después 2025. La vista Copilot es un
libro aparte con siete cortes y `Leyenda`.

## Fuente: tablero de la CNBV

`entradas/tablero/sh_datos_csv_40_i/040_TO.csv` es una serie larga
(`concepto, institucion, fecha, saldo_se, tipo_saldo`):

- Periodicidad **mensual**; 2025 completo y 2026 de enero a septiembre.
- Importes en **pesos** (se dividen entre 1,000,000 al escribirlos).
- Solo se usan saldos **`tipo_saldo = Consolidado con SOFOMER`**.
- Los 54 bancos tienen clave `040xxx`; la fila `institucion = 5` es el total del
  sector y las filas `59`–`64` son grupos: sirven solo para validar, no entran
  en las hojas.
- CCL y CFEN se publican solo en cierres trimestrales (mar/jun/sep/dic).

Conceptos utilizados (códigos de `config.CONCEPTOS`):

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

Del BE se leen el universo (clave CASFIM, nombre, estatus y tipo) y el
ROA/ROE publicados para validar. El cruce es siempre por **Clave CASFIM**.

## Unidades

**Todo el libro está en millones de pesos.** El tablero publica en pesos; el
generador divide cada importe entre 1,000,000 antes de escribirlo. Las columnas
monetarias usan el formato `#,##0.00` y los indicadores `0.00%`. Las notas al pie
de cada hoja lo indican.

## Método

- **Periodicidad mensual** con columna `Trimestre`; los cortes trimestrales son
  mar/jun/sep/dic y alimentan la vista Copilot.
- **54 bancos en cada mes** (más el total `5` y los grupos `59`–`64` solo para
  validación). Si un banco no reporta, sus celdas dicen `n.d.`; no se imputan
  ceros.
- **Estado de resultados en YTD.** Ingresos, gastos, gastos de administración y
  resultado neto son acumulados del año, igual que los publica el tablero.
- **ICAP = Capital Neto / Activos sujetos a riesgo** (`H / G`). En septiembre de
  2026, sin dato en el tablero, se escribe el ICAP del PDF como **número** en
  vez de la fórmula; los demás meses conservan `H / G`.
- **CCB y CCF** del PDF de Banxico se escriben como número en el mes del corte.
- **ROA y ROE se calculan**, no se copian: `Resultado Neto 12M / Activos
  promedio 12M` y `Resultado Neto 12M / Capital promedio 12M`.
- **MIN** usa Margen Financiero Ajustado 12M y se compara contra la mediana de
  los 54 bancos del mes (columna Q oculta).
- Las estimaciones preventivas conservan el signo reportado por la CNBV; por
  eso ICOR usa `ABS(...)`.

### Columnas de `Datos Fuente AAAA`

| Col | Campo | Tipo |
|---|---|---|
| A–E | No., Banco, Año, Mes, Trimestre | dato |
| F | Activos Totales | dato |
| G | Activos sujetos a riesgo | dato |
| H | Capital Neto | dato |
| I | ICAP = H / G | fórmula (número del PDF en septiembre de 2026) |
| J | Cartera Total | dato |
| K | Cartera etapa 3 | dato |
| L | Cartera Neta | dato |
| M | Estimaciones preventivas | dato |
| N–O | Ingresos / Gastos por intereses (YTD) | dato |
| P | Margen Financiero = N − O | fórmula |
| Q | Margen Financiero Ajustado | dato |
| R | Gastos de administración y promoción (YTD) | dato |
| S | Resultado Neto (YTD) | dato |
| T–U | Captación Tradicional / Total | dato |
| V–W | Captación y Cartera Total del mes anterior | dato |
| X | Capital contable | dato |
| Y–AA | Resultado 12M, Activos y Capital promedio 12M | dato |
| AB–AC | Margen Financiero 12M, Activo productivo promedio 12M | dato |
| AD | Ingresos totales de la operación | dato |
| AE–AF | Captación y Cartera Total mismo mes año anterior | dato |
| AG–AH | CCL y CFEN | dato |
| AI | Margen Financiero Ajustado 12M | dato |
| AJ–AK | CCB y CCF del PDF | dato |
| AL | Categoría del PDF | dato |

### Columnas de `Indicadores AAAA`

| Col | Indicador | Fórmula |
|---|---|---|
| F | ICAP | `Datos Fuente!I` (número del PDF en septiembre de 2026) |
| G | IMOR | `K / J` |
| H | ICOR | `ABS(M) / K` |
| I | ROA | `Y / Z` |
| J | ROE | `Y / AA` |
| K | MIN | `AI / AC` |
| L | Crecimiento de Captación | `U / AE − 1` |
| M | Crecimiento de Cartera | `J / AF − 1` |
| N | Crédito Neto / Captación | `L / T` |
| O | Índice de Eficiencia | `R / AD`, con `n.a.` si los ingresos son ≤ 0 |
| P | CCL/LCR | `AG` |
| Q | Mediana de MIN del mes | dato oculto para el semáforo |

Todas son fórmulas que apuntan a la hoja de datos del mismo año, en la misma
fila. La vista Copilot calcula los mismos indicadores en Python y los escribe
como valores.

## Semáforos

| Indicador | Verde 🟢 | Amarillo 🟡 | Rojo 🔴 |
|---|---|---|---|
| ICAP | ≥ 12% | 10% – < 12% | < 10% |
| IMOR | ≤ 3% | > 3% – 5% | > 5% |
| ICOR | ≥ 100% | 80% – < 100% | < 80% |
| ROA | ≥ 1% | > 0% – < 1% | ≤ 0% |
| ROE | ≥ 15% | > 0% – < 15% | ≤ 0% |
| MIN | ≥ 100% de la mediana | 80% – < 100% de la mediana | < 80% de la mediana |
| Crec. de Captación y de Cartera | > 0% | = 0% | < 0% |
| Crédito Neto / Captación | 70% – 90% | 60% – < 70% o > 90% – 100% | < 60% o > 100% |
| Índice de Eficiencia | ≤ 55% | > 55% – 70% | > 70% o `n.a.` |
| CCL/LCR | ≥ 120% | 100% – < 120% | < 100% |

- **`n.a.` en rojo** cuando los ingresos totales de la operación son ≤ 0.
- Paleta con contraste **AAA de WCAG 2.2** (≥ 7:1 entre texto y fondo): verde
  `D1E7DD` / `0F5132`, amarillo `FFF3CD` / `664D03` y rojo `F8D7DA` / `842029`.
- Las condiciones se evalúan sobre fracciones (12% = 0.12) y solo si la celda es
  numérica, para que los `n.d.` no se pinten. La regla de `n.a.` es la excepción.
- Hay 11 indicadores × 3 tramos + la regla de `n.a.` = **34 reglas por hoja de
  indicadores**.

## Validaciones que corre el script

1. **Cobertura:** 54 filas por mes en cada año solicitado.
2. **Consistencia del tablero:** suma de los 54 bancos contra el total `5` y los
   grupos `59`–`64` para los conceptos de `CAMPOS_SECTOR`. Diferencia máxima
   aceptada: 1,000,000 de pesos (1 millón).
3. **ROA y ROE calculados** contra el boletín electrónico. Tolerancia: 0.02
   puntos porcentuales.
4. **IMOR, ICOR y MIN publicado** contra el tablero; tolerancia de 0.02 puntos
   (0.05 para IMOR).
5. **ICAP / CCB / CCF del PDF** contra el tablero cuando ese mes viene publicado;
   tolerancia de 0.02 puntos. Si el tablero no trae ese mes, se imprime
   `sin contraste en tablero · fuente PDF` y no se marca diferencia.
6. **Estructura del libro:** nombres y orden de hojas, filas por año, 7
   encabezados exactos del catálogo, fórmulas visibles, 11 indicadores en el
   diccionario, 11 bloques de semáforo y 34 reglas de formato condicional.

## Cobertura y excepciones conocidas

- **Septiembre de 2026:** el CSV del tablero todavía no publica capital neto,
  activos ponderados ni ICAP de ese mes. El ICAP se toma del PDF de Banxico y se
  escribe como número en `Datos Fuente` (columna I) y en la vista Copilot.
- **CCL y CFEN:** se publican solo en cortes trimestrales con desfase de un
  trimestre; el último dato es `202606`, por eso aparecen `n.d.` en septiembre
  de 2026. No se llenan con datos del PDF.
- **MIN publicado:** la CNBV publica el concepto `4040001` con Margen Financiero
  12M no ajustado; el libro muestra el ajustado (`40200011`). Se documenta en
  la validación.
- **`n.d.`** = dato no disponible en el corte (se escribe como texto, no como
  celda vacía). **`n.a.`** = índice de eficiencia no aplicable cuando los
  ingresos de operación son ≤ 0.
- El total `5` y los grupos `59`–`64` no se incluyen como bancos en las hojas.

## Cómo actualizar

### Un mes nuevo de 2026

1. Descarga el tablero actualizado y reemplaza
   `entradas/tablero/sh_datos_csv_40_i/040_TO.csv`.
2. Agrega el mes a `ANIOS[2026]` en `banca_multiple/config.py`.
3. Si hay un PDF nuevo de Banxico, renómbralo `ICAP_BM_YYYYMM.pdf`, actualiza
   `PDF_ICAP` en `config.py` (o pasa `--pdf-icap RUTA`) y elimina el PDF anterior.
4. Corre el programa. Cuando el tablero ya publique ICAP para el mes del PDF, la
   validación vuelve a comparar ambos y la columna I recupera la fórmula `H/G`
   automáticamente: no hay que editar hojas ni fórmulas.

Para probar un año sin generar el libro completo usa `--anios 2026`
(o `--anios 2025-2026`); el Diccionario y los Semáforos solo citan los años
incluidos.

### Un año nuevo

Agrega el año a `ANIOS` en `banca_multiple/config.py` y listo: las hojas, la
validación del libro y los textos se derivan de `ANIOS`.

### Un banco nuevo

Debe aparecer con clave `040xxx` en la hoja `Evaluación Calidad Detallada` del
BE vigente. El catálogo, el universo y las hojas se derivan de ahí; la
categoría del PDF se cruza por clave y es `n.d.` si el banco no está en el PDF.

## Verificar que un cambio no altera el libro

`scripts/comparar.py` compara dos libros (y opcionalmente dos salidas de
`stdout`) celda por celda: valores, fórmulas, formatos, notas, anchos y formato
condicional. Sale con código 0 si son idénticos.

**Windows** (compara solo el `.xlsx`):

```powershell
.venv\Scripts\python.exe generar_banca_multiple.py --out $env:TEMP\bancos.xlsx
Copy-Item $env:TEMP\bancos.xlsx $env:TEMP\referencia.xlsx

# ... hacer el cambio ...

.venv\Scripts\python.exe generar_banca_multiple.py --out $env:TEMP\bancos.xlsx
.venv\Scripts\python.exe scripts\comparar.py --xlsx-a $env:TEMP\referencia.xlsx --xlsx-b $env:TEMP\bancos.xlsx
```

**macOS / Linux** (compara el `.xlsx` y el `stdout`):

```bash
# 1. generar una referencia con el código actual
.venv/bin/python generar_banca_multiple.py --out /tmp/bancos.xlsx > /tmp/salida1.txt
cp /tmp/bancos.xlsx /tmp/referencia.xlsx

# 2. hacer el cambio y volver a generar (misma ruta)
.venv/bin/python generar_banca_multiple.py --out /tmp/bancos.xlsx > /tmp/salida2.txt

# 3. comparar
.venv/bin/python scripts/comparar.py \
    --xlsx-a /tmp/referencia.xlsx --xlsx-b /tmp/bancos.xlsx \
    --stdout-a /tmp/salida1.txt --stdout-b /tmp/salida2.txt
```

Si también comparas el `stdout`, ambas corridas deben escribir en la **misma
ruta**: la última línea (`Archivo generado: …`) imprime la ruta exacta. Un
`IDÉNTICO` significa que el libro no cambió en nada; en la spec 004 los diffs
esperados (ICAP de septiembre, notas de fuente, catálogo de 7 columnas y
Leyenda) están documentados en su `task.md`.

## Notas de mantenimiento

- Los umbrales del semáforo viven en `FICHAS` (`banca_multiple/fichas.py`); si
  cambia un umbral, hay que cambiarlo ahí para que el libro se vuelva a producir
  igual. La hoja `Semáforos` se genera de esa misma lista.
- Las notas de liquidez y la nota de fuente del ICAP están en
  `banca_multiple/config.py` (`NOTA_LIQUIDEZ` y `NOTA_ICAP_PDF`) y se comparten
  entre hojas, vista y documentación.
- Los encabezados del catálogo viven en `ENC_CATALOGO`
  (`banca_multiple/estilos.py`); anchos, notas y filtro se derivan de esa lista.
- El mes del PDF se deriva siempre del nombre del archivo, no de la fecha actual.
- Las estimaciones preventivas conservan el signo de la CNBV; por eso ICOR usa
  `ABS(...)`.

## Fuentes

- [Portafolio Informativo de la CNBV](https://portafolioinfo.cnbv.gob.mx/Paginas/Inicio.aspx)
- [Tablero de información financiera de la CNBV ( Power BI )](https://app.powerbi.com/)
- [Boletines de Banca Múltiple](https://portafolioinfo.cnbv.gob.mx/Paginas/Contenidos.aspx)
- [Banco de México — Nivel de capitalización y alertas tempranas](https://www.banxico.org.mx/)
