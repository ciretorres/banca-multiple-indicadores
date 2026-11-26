# Plan: Libro de indicadores de Banca Múltiple — V1

Spec de origen: `docs/specs/001-libro-indicadores-banca-multiple/spec.md`.

## Enfoque técnico

Espejo del proyecto `sofipos-indicadores`, adaptado a Banca Múltiple:

- **Entradas:** `entradas/BE BM 202609.xlsx` y `entradas/tablero/sh_datos_csv_40_i/040_TO.csv`.
- **Lector BE:** se reutiliza el patrón de `xlsx_lector.py` (lectura directa del ZIP/XML) porque los `.xlsx` de la CNBV traen relaciones `customXml` que rompen `openpyxl`/`describe_workbook`. `be.py` lee el universo desde `Evaluación Calidad Detallada` (54 bancos) y los ROA/ROE publicados desde `Indicadores`.
- **Tablero:** lectura en streaming del CSV, filtrando por `tipo_saldo = "Consolidado con SOFOMER"`, fechas y conceptos; separa los 54 bancos, el total `5` y los grupos `59`–`64`.
- **Unidad:** millones de pesos (CSV en pesos ÷ 1,000,000). El BE ya viene en "Millones de pesos".
- **Periodos:** 2025 (12 meses) y 2026 (ene–sep, 9 meses). La columna `Trimestre` se deriva del mes.
- **Indicadores:** 11, con umbrales de la spec. MIN usa mediana simple de los 54 bancos con MIN, calculada por mes en Python y referenciada por el formato condicional. ICAP y CCL/LCR quedan `n.d.` en septiembre 2026 por lag/falta de datos. Crecimiento se reporta solo nominal + nota.

Módulos auxiliares a crear (no estaban en el árbol inicial pero siguen el patrón de `sofipos-indicadores`): `utilidades.py` y `xlsx_lector.py`.

## Orden de cambios por fases

### Fase 1 — Entorno y base
- T001 Crear/validar `.venv` multiplataforma.
- T002 Configuración central (`config.py`).

Checkpoint 1: `pytest tests/test_config.py` verde y `pyflakes banca_multiple/config.py` limpio.

### Fase 2 — Lectura de datos
- T003 Utilidades.
- T004 Lector XLSX del BE.
- T005 `be.py` (universo + ROA/ROE publicados).
- T006 `tablero.py` (filtro al vuelo).

Checkpoint 2: lectura de entradas reales sin error; tests de tablero verdes.

### Fase 3 — Filas
- T007 `filas.py` (54 filas/mes, `Trimestre`, millones, crecimiento YoY).

Checkpoint 3: `tests/test_filas.py` verde; conteo 54 × meses.

### Fase 4 — Estilos e indicadores
- T008 `estilos.py` + `fichas.py` (paleta AAA, umbrales).

Checkpoint 4: `tests/test_semaforos.py` verde.

### Fase 5 — Hojas del libro
- T009 `hojas/catalogo.py`.
- T010 `hojas/datos_fuente.py`.
- T011 `hojas/indicadores.py` (MIN con mediana, ICAP/CCL `n.d.`).
- T012 `hojas/diccionario.py` + `hojas/semaforos.py`.
- T013 `hojas/__init__.py` (`escribir_xlsx`).

Checkpoint 5: libro se genera sin error con `--anios 2026`.

### Fase 6 — Orquestación
- T014 `main.py` (CLI + flujo completo).

Checkpoint 6: corrida por defecto sale con exit 0 y "Validación general: OK".

### Fase 7 — Validaciones
- T015 `validacion_datos.py`.
- T016 `validacion_libro.py`.

Checkpoint 7: validaciones numéricas dentro de tolerancia.

### Fase 8 — Pruebas
- T017 Ajuste de tests y fixtures.

Checkpoint 8: `pytest` completo verde.

### Fase 9 — Documentación y verificación global
- T018 README / AGENTS / entradas.
- T019 Verificación global (última tarea).

## Dependencias clave

- `config.py` → `tablero.py`, `be.py`, `filas.py`, hojas.
- `utilidades.py` → `tablero.py`, `filas.py`, hojas.
- `xlsx_lector.py` → `be.py`.
- `tablero.py` + `be.py` → `filas.py` → hojas → `main.py`.
- `estilos.py` + `fichas.py` → hojas de indicadores/diccionario/semáforos.
- `validacion_datos.py` depende de `be.py`, `tablero.py`, `filas.py`.
- `validacion_libro.py` depende de hojas y `config.py`.

## Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| CSV de 512 MB / 8.17 M filas | Alto | Filtrar al vuelo por `tipo_saldo`, fecha y concepto; leer solo fechas necesarias (mes actual y anterior/año anterior). |
| BE con `customXml` | Alto | Usar `xlsx_lector.py` (ZIP/XML) en lugar de `openpyxl` para el BE. |
| Nombres del BE vs tablero por código | Medio | Normalizar claves a 6 dígitos; validar cobertura de los 54 en `validacion_datos`. |
| Mediana de MIN dinámica por mes | Medio | Calcular en Python por mes; escribir en columna auxiliar oculta de Indicadores y referenciarla en el formato condicional. |
| ICAP con lag de un mes (termina 202608) | Medio | No forzar cálculo en septiembre; marcar `n.d.` y validar recálculo vs publicado cuando haya datos. |
| Crecimiento YoY requiere 2024 | Medio | Usar datos 2024 del tablero si existen; si no, `n.d.`; documentar en notas. |
| Unidades (pesos vs millones) | Alto | Conversión única en `filas.py` (`a_millones`, ÷ 1,000,000); BE ya en millones. |
| Catálogo sin fuente para autorización/nivel/estatus/tipo | Medio | Mantener Open Question; poblar con lo disponible del BE y marcar `n.d.` lo faltante. |
| Consistencia total `5` vs grupos `59`–`64` | Medio | Guardar agregados por institución en `Tablero`; comparar suma de 54 con tolerancia. |
| Cambios no intencionales en el libro | Alto | Verificar con `scripts/comparar.py` → `IDÉNTICO` tras cada cambio relevante. |

## Verificación

```bash
.venv/bin/pytest
.venv/bin/pyflakes banca_multiple/ tests generar_banca_multiple.py
.venv/bin/python generar_banca_multiple.py --help
.venv/bin/python generar_banca_multiple.py --out /tmp/bancos.xlsx
.venv/bin/python scripts/comparar.py --xlsx-a /tmp/referencia.xlsx --xlsx-b /tmp/bancos.xlsx
```

La última corrida debe imprimir `IDÉNTICO` con exit 0. No hacer `git commit` ni `git push`; dejar listo y sugerir comandos.