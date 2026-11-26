# Spec: Libro de indicadores de Banca Múltiple — V1

## Objective

Generar el libro Excel de indicadores de la Banca Múltiple supervisada por la
CNBV, espejo del proyecto `sofipos-indicadores`: hojas Catálogo, Datos Fuente
(por año/mes con columna `Trimestre`), Indicadores (por año), Diccionario
(fórmulas y semáforo) y Semáforos (paleta accesible AAA de SOFIPOS).

- **Universo:** 54 bancos con código CASFIM `040xxx` que reportan en el BE
  202609. El total del sistema (código `5`) y los grupos (`59`–`64`) se usan
  solo para validación, no aparecen en las hojas.
- **Corte:** 2025 completo (12 meses) y 2026 enero–septiembre (9 meses), BE
  202609. Datos mensuales; la columna `Trimestre` se deriva del mes
  (Q1=ene-mar, Q2=abr-jun, Q3=jul-sep, Q4=oct-dic). El BE valida los meses de
  cierre de trimestre (mar/jun/sep/dic).
- **Unidad:** millones de pesos (CSV en pesos → ÷ 1,000,000). El BE usa
  "Millones de pesos".
- **Lector del tablero:** `tipo_saldo = "Consolidado con SOFOMER"` (cuadra con
  ROA/ROE publicados del BE).
- **Validación:** ROA/ROE calculados vs publicados en el BE; IMOR/ICOR
  calculados vs publicados del tablero; consistencia suma de los 54 bancos vs
  total `5` y grupos `59`–`64`.

## Tech Stack

- Python ≥ 3.11, `openpyxl` ≥ 3.1, `< 4`; `pytest` y `pyflakes` (dev).
- Entradas (no versionadas): `entradas/BE BM 202609.xlsx`,
  `entradas/tablero/sh_datos_csv_40_i/040_TO.csv` (512 MB, 8.17 M filas),
  `catalogo_conceptos_040.xlsx`, `catalogo_instituciones_040.csv`.
- Salida: `salidas/Bancos_Multiples_Indicadores_Datos.xlsx`.
- MCP de Excel (`excel-mcp-server`) para inspección de `.xlsx`; no requiere
  Excel instalado.

## Commands

- Generar: `.venv/bin/python generar_banca_multiple.py`
- Generar (ruta exacta): `.venv/bin/python generar_banca_multiple.py --out RUTA`
- Wrapper equivalente: `python -m banca_multiple`
- Ayuda: `.venv/bin/python generar_banca_multiple.py --help`
- Pruebas: `.venv/bin/pytest`
- Lint: `.venv/bin/pyflakes banca_multiple/`
- Comparación: `.venv/bin/python scripts/comparar.py --xlsx-a A --xlsx-b B`
- Verificación completa: ver AGENTS.md § "Verificar un cambio".

## Project Structure

```
banca-multiple-indicadores/
  generar_banca_multiple.py      # wrapper
  banca_multiple/                # paquete principal
    main.py, __main__.py, config.py
    tablero.py, be.py, filas.py, fichas.py, estilos.py
    validacion_datos.py, validacion_libro.py
    hojas/
      catalogo.py, datos_fuente.py, indicadores.py
      diccionario.py, semaforos.py
  entradas/                      # datos crudos CNBV (no versionados)
    BE BM YYYYMM.xlsx
    tablero/sh_datos_csv_40_i/
      040_TO.csv
      catalogo_conceptos_040.xlsx
      catalogo_instituciones_040.csv
  salidas/                       # .xlsx generado
  scripts/comparar.py
  tests/
  docs/specs/
```

## Code Style

- Español. Seguir el patrón de `sofipos-indicadores` antes de inventar uno nuevo.
- Docstrings solo cuando aporten.
- Configuración centralizada en `config.py`: rutas, periodos, conceptos CNBV,
  `TIPO_SALDO`, `ANIOS`, `TRIMESTRES`, `CAMPOS_SECTOR`, `ND = "n.d."`.
- Módulos pequeños por responsabilidad (`be`, `tablero`, `filas`, `fichas`,
  `estilos`, `validacion_datos`, `validacion_libro`, `hojas/*`).
- Unidades en millones de pesos (CSV pesos ÷ 1,000,000); el BE ya viene en
  "Millones de pesos".
- Paleta accesible AAA de SOFIPOS: `VERDE_FILL D1E7DD` / `AMARILLO_FILL FFF3CD`
  / `ROJO_FILL F8D7DA`; fuentes `0F5132` / `664D03` / `842029`.
- `pyflakes` limpio sobre `banca_multiple/`.

## Testing Strategy

- `pytest` sobre `tests/` y `pyflakes` sobre los archivos tocados.
- Tests análogos a `sofipos-indicadores`: config, tablero, filas, semáforos,
  validaciones, CLI.
- Validaciones numéricas: ROA/ROE calculados vs publicados (BE `Indicadores`,
  por banco y Sistema); IMOR/ICOR calculados vs publicados del tablero (por
  banco); consistencia suma de los 54 bancos vs total `5` y grupos `59`–`64`
  (tolerancia por redondeo).
- `scripts/comparar.py` → `IDÉNTICO` para verificar que un cambio no altera el
  libro.
- Sin tests de integración pesados en V1.

## Boundaries

- **Always:** ejecutar `pytest` y `pyflakes` antes de cerrar; no alterar el
  libro sin documentar la diferencia esperada; usar
  `TIPO_SALDO = "Consolidado con SOFOMER"`; universo = 54 bancos del BE
  `Evaluación Calidad Detallada`; usar `ND = "n.d."` para datos no disponibles.
- **Ask first:** cambiar conceptos CNBV o universo; añadir dependencias;
  cambiar hojas/estructura del libro; cambiar validaciones o tolerancias.
- **Never:** tocar `sofipos-indicadores`; hacer `git commit` ni `git push`;
  editar `entradas/`; hardcodear rutas absolutas; incluir el total `5` o los
  grupos `59`–`64` en las hojas (solo validación).

## Fuentes y conceptos

- **Tablero:** `entradas/tablero/sh_datos_csv_40_i/040_TO.csv`, columnas
  `concepto, institucion, fecha, tipo_saldo, saldo_se`. Institución `040xxx`
  (5 dígitos en el CSV, con cero inicial en el BE) o `5`/`59`–`64`.
- **Catálogos:** `catalogo_conceptos_040.xlsx` (sector, tema, orden_tema, id,
  descripcion, indicador, orden) y `catalogo_instituciones_040.csv`
  (sector, institucion, descripcion, orden).
- **BE:** `BE BM 202609.xlsx` — hojas `Evaluación Calidad Detallada`
  (universo), `Indicadores` (ROA/ROE publicados), `EF Resumen` y
  `Cartera y calif` (validación por banco).

Conceptos CNBV verificados (202609), en pesos:

| Campo interno | Código CNBV | Uso |
|---|---|---|
| Capital neto | 4030211 | ICAP |
| Activos sujetos a riesgo | 4030249 | ICAP |
| ICAP publicado | 4021750 | validación (termina 202608 → n.d. en sep) |
| Activos | 40100001 | ROA |
| Activos (promedio 12m) | 40200004 | ROA |
| Capital contable | 40100002 | ROE |
| Capital contable (promedio 12m) | 40200005 | ROE |
| Cartera total | 40100185 | IMOR, crecimiento de cartera |
| Cartera etapa 3 (vencida) | 40100341 | IMOR |
| Cartera neta | 40100551 | crédito neto / captación |
| Estimación preventiva (balance) | 40100031 | ICOR |
| EPRC (resultado) | 40100131 | referencia |
| Resultado neto | 40100013 | ROA/ROE |
| Resultado neto (suma flujos 12m) | 40200015 | ROA/ROE anualizados |
| Margen financiero | 40100008 | referencia |
| Margen financiero ajustado | 40100009 | MIN |
| Margen financiero (suma flujos 12m) | 40200010 | referencia |
| Margen financiero ajustado (suma flujos 12m) | 40200011 | MIN anualizado |
| Ingresos por intereses | 40100006 | referencia |
| Gastos por intereses | 40100007 | referencia |
| Gastos de administración y promoción | 40100011 | índice de eficiencia |
| Ingresos totales de la operación | 40100170 | índice de eficiencia |
| Captación tradicional | 40100085 | crédito neto / captación |
| Captación total | 40100042 | crecimiento de captación |
| Activo productivo (promedio 12m) | 40200240 | MIN |
| IMOR publicado | 40200017 | validación |
| ICOR publicado | 40200096 | validación |
| ROA publicado | 40200001 | validación |
| ROE publicado | 40200002 | validación |
| MIN publicado | 4040001 | validación |
| CCL consolidado | 601 | no presente en 202609 → n.d. |
| CFEN consolidado | 610 | no presente en 202609 → n.d. |

## Indicadores y semáforos

1. **ICAP** = capital neto / activos sujetos a riesgo × 100 — verde ≥ 12%,
   amarillo 10–< 12%, rojo < 10% (n.d. en 202609 por lag de un mes).
2. **IMOR** = cartera vencida / cartera total × 100 — verde ≤ 3%,
   amarillo > 3–5%, rojo > 5%.
3. **ICOR** = estimaciones preventivas / cartera vencida × 100 (con `abs`) —
   verde ≥ 100%, amarillo 80–< 100%, rojo < 80%.
4. **ROA** = utilidad neta anualizada / activos totales promedio × 100 —
   verde ≥ 1%, amarillo > 0–< 1%, rojo ≤ 0%.
5. **ROE** = utilidad neta anualizada / capital contable promedio × 100 —
   verde ≥ 15%, amarillo > 0–< 15%, rojo ≤ 0%.
6. **MIN** = margen financiero ajustado por riesgos crediticios anualizado /
   activos productivos promedio × 100 — verde ≥ mediana de los 54 bancos con
   MIN; amarillo 80–< 100% de la mediana; rojo < 80% o negativo.
   *Nota:* el MIN publicado por la CNBV (4040001) usa Margen Financiero 12M
   (**no ajustado**), por lo que el indicador del libro (ajustado, según el
   capture) no es directamente comparable. La validación contrasta el MIN
   **publicado** (no ajustado) contra el tablero y deja constancia de la
   diferencia; la mediana incluye a los bancos con MIN negativo.
7. **Crecimiento de captación** = (captación periodo / captación mismo periodo
   año anterior − 1) × 100 — verde crecimiento nominal positivo; amarillo
   nominal positivo sin superar inflación; rojo nominal negativo. (Solo nominal
   en V1; ajuste por inflación pendiente.)
8. **Crecimiento de cartera** = (cartera total periodo / cartera mismo periodo
   año anterior − 1) × 100 — verde crecimiento real positivo y sin deterioro
   marcado de IMOR/ICOR; amarillo nominal positivo sin superar inflación; rojo
   caída real persistente o expansión muy superior a pares con deterioro.
9. **Crédito neto / captación** = cartera neta de estimaciones / captación
   tradicional × 100 — verde 70–90%, amarillo 60–< 70% o > 90–100%, rojo
   < 60% o > 100%.
10. **Índice de eficiencia** = gastos de administración y promoción / ingresos
    de operación × 100 — verde ≤ 55%, amarillo > 55–70%, rojo > 70%.
11. **CCL/LCR** = activos líquidos de alta calidad / salidas netas de efectivo a
    30 días × 100 — verde ≥ 120%, amarillo 100–< 120%, rojo < 100%. (n.d. en
    V1 por falta de datos.)

## Hojas del libro

- **Catálogo:** 54 bancos (clave CASFIM, nombre, autorización, nivel, estatus,
  tipo).
- **Datos Fuente 2025 / Datos Fuente 2026:** filas por banco × mes, con columna
  `Trimestre`.
- **Indicadores 2025 / Indicadores 2026:** los 11 indicadores con semáforo.
- **Diccionario:** fórmulas y umbrales del semáforo.
- **Semáforos:** paleta accesible AAA de SOFIPOS.

## Validaciones

- ROA/ROE calculados vs publicados en el BE `Indicadores` (por banco y
  Sistema).
- IMOR/ICOR calculados vs publicados del tablero (por banco).
- Consistencia: suma de los 54 bancos vs total `5` y vs grupos `59`–`64`
  (tolerancia por redondeo).
- ICAP con lag de un mes (termina 202608): validar recálculo vs publicado.
- NICAP no aplica (es SOFIPOS).

## Success Criteria

- `generar_banca_multiple.py --help` funciona y `pyflakes banca_multiple/` sale
  limpio.
- `pytest` pasa.
- El libro generado contiene las hojas Catálogo, Datos Fuente 2025, Datos Fuente
  2026, Indicadores 2025, Indicadores 2026, Diccionario y Semáforos.
- Catálogo con los 54 bancos del BE.
- Datos Fuente con filas por banco × mes (2025: 12 meses; 2026: 9 meses) y
  columna `Trimestre`.
- Indicadores calculados para los 11 indicadores con semáforo.
- ROA/ROE calculados cuadran con el BE `Indicadores` (Sistema y bancos) dentro
  de tolerancia.
- IMOR/ICOR calculados cuadran con el tablero (por banco) dentro de tolerancia.
- Suma de los 54 bancos cuadra con total `5` y grupos `59`–`64` dentro de
  tolerancia.
- CCL y crecimiento real marcados `n.d.`/nota según Out of Scope.
- Regenerar el libro y comparar con `scripts/comparar.py` → `IDÉNTICO`.

## Out of Scope (Deferred)

- Ajuste por inflación en crecimiento (solo nominal + nota).
- CCL/CFEN (sin datos en 202609) → n.d.
- Mediana por agrupación o tamaño (solo mediana simple de los 54).
- NICAP (es SOFIPOS).
- Documentación completa (README mínimo).
- Tests de integración pesados.

## Open Questions

- ICAP recalc vs publicado: validar si capital neto / activos sujetos a riesgo
  cuadra con el publicado.
- Mediana de MIN: resuelto — se incluyen los bancos con MIN negativo.
- Si un banco no reporta un mes: ¿`n.d.` o excluir la fila? (en SOFIPOS se
  deja `n.d.`).
- Confirmar si el BE trae más indicadores publicados por banco (ICAP, IMOR,
  ICOR) además de ROA/ROE.
- Fuente de autorización/nivel/estatus/tipo para el Catálogo: el BE BM no
  incluye hoja `Universo`; confirmar si se toman de otro documento o quedan
  `n.d.`.
- Definir el umbral de "deterioro marcado" de IMOR/ICOR para el semáforo del
  crecimiento de cartera.
- Fuente y serie de inflación para el ajuste real (V2).
