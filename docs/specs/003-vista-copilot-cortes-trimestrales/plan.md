# Plan de implementación: Vista para Copilot — cortes trimestrales

Spec: `docs/specs/003-vista-copilot-cortes-trimestrales/spec.md` (aprobada, contrato).
Tareas: `task.md` de esta carpeta. La numeración y el índice viven en `docs/specs/README.md`.

## Enfoque técnico

Se agrega un **libro compañero** nuevo, generado por un entry point propio, sin
tocar el libro principal ni su CLI. La única parte delicada es calcular los 11
indicadores en Python con la **misma aritmética** de las fórmulas de
`hojas/indicadores.py`: se extraen funciones puras nuevas dentro de ese mismo
archivo y se deja `escribir_indicadores` intacto, de modo que el libro principal
siga byte-idéntico. El lector de Copilot recibe valores, no fórmulas.

Fases verticales: configuración → cálculo compartido → libro compañero → CLI →
verificación. Cada fase deja algo verificable y termina con un checkpoint; el
libro principal se compara contra referencia en los checkpoints 0, 1 y 3.

### Cómo calcular los 11 indicadores sin duplicar lógica

Las fórmulas de `escribir_indicadores` apuntan a celdas de `Datos Fuente`; esas
columnas ya están escritas desde las claves del dict de `filas` (`preparar_filas`).
La tabla única de correspondencia que deben usar las funciones nuevas es:

| Indicador | Fórmula en el libro | Operandos en `filas` |
|---|---|---|
| ICAP | `I = H/G` | `capital_neto / activos_riesgo` |
| IMOR | `K/J` | `cartera_e3 / cartera_total` |
| ICOR | `ABS(M)/K` | `abs(estimaciones) / cartera_e3` |
| ROA | `Y/Z` | `resultado_12m / activos_prom_12m` |
| ROE | `Y/AA` | `resultado_12m / capital_prom_12m` |
| MIN | `AI/AC` | `margen_ajustado_12m / activo_prod_prom_12m` (valor de cada banco) |
| Crec. captación | `U/AE-1` | `captacion_total / captacion_prev_anio - 1` |
| Crec. cartera | `J/AF-1` | `cartera_total / cartera_total_prev_anio - 1` |
| Crédito neto/captación | `L/T` | `cartera_neta / captacion_tradicional` |
| Índice de eficiencia | `IF(AD<=0,"n.a.",R/AD)` | `gastos_adm / ingresos_operacion`, o `n.a.` si ingresos ≤ 0 |
| CCL/LCR | `AG` | `ccl` (ya es ratio, se escribe tal cual) |

- **Decisión resuelta — MIN:** la columna MIN lleva el **MIN calculado de cada
  banco** (`AI/AC`), no la mediana repetida. `calcular_mediana_min(filas_del_mes)`
  usa `statistics.median` sobre `margen_ajustado_12m / activo_prod_prom_12m` de
  los 54 bancos (**negativos incluidos**) solo como referencia del semáforo
  original, que se documenta en `Leyenda`; no se escribe como columna.
- **Decisión resuelta — eficiencia:** se conserva `n.a.` cuando
  `ingresos_operacion <= 0`, igual que el libro principal; es distinto de `n.d.`
  (dato no disponible) y no se normaliza.
- División segura equivalente a `IFERROR`: si falta algún operando, no es número
  o el denominador es 0, devuelve `ND` (`n.d.`). Por eso septiembre de 2026 sale
  `n.d.` cuando el tablero no trae capital/activos de riesgo ni CCL.
- El escritor del compañero **no usa `_celda_numero`** para los indicadores:
  esa función convierte cualquier texto a `n.d.`. Escribe el número con
  `FMT_PORC` o el texto exacto (`n.d.` / `n.a.`) con `FMT_TEXTO`, sin fórmulas.

## Decisiones de diseño

- **Sin tocar el principal:** `generar_banca_multiple.py`, `banca_multiple/main.py`
  y las hojas existentes quedan iguales. El compañero reutiliza directamente
  `leer_universo`, `leer_tablero`, `leer_icap` y `preparar_filas` con los mismos
  archivos de `entradas/`; no importa `main.main()` para no arrastrar su CLI ni
  su stdout.
- **Cortes derivados de `ANIOS`:** pares (año, trimestre, mes de cierre) con
  cierre en 3/6/9/12. Como `ANIOS[2026]` llega solo hasta 9, salen exactamente
  7 hojas: `2025 Q1`…`2025 Q4` y `2026 Q1`…`2026 Q3`. Se guardan en `config.py`
  junto con `SALIDA_VISTA_COPILOT`.
- **Columnas de cada corte:** `No.`, `Banco`, `Mes de corte` (texto, p. ej.
  `Septiembre`), `Trimestre` (el valor del libro, p. ej. `T3`) y los 11
  indicadores = 15 columnas; 54 filas por hoja, sin totales ni grupos.
- **Q3 2026:** se fuerza `n.d.` en ICAP y CCL/LCR por desfase de publicación
  (último dato CCL `202606`), además de la división segura. No se inventan datos
  de septiembre.
- **Leyenda al final**, con `NOTA_LIQUIDEZ` de `config.py`, explicación de
  `n.d.`, el desfase trimestral, la nota de MIN (publicado CNBV no ajustado
  frente al libro ajustado) y la mediana de los 54 como referencia del semáforo.
- **MIN por banco (resuelto):** se escribe el MIN calculado de cada banco; la
  mediana de los 54 solo se menciona en `Leyenda`, nunca como valor repetido.
- **Eficiencia `n.a.` (resuelto):** con ingresos de operación ≤ 0 se escribe
  `n.a.`, igual que el libro principal; no se convierte en `n.d.`.
- **Sin duplicar datos de entrada:** no se editan rutas absolutas ni `entradas/`.

## Grafo de dependencias y orden

```
T001 config ──→ T002 funciones de cálculo ──→ T003 escritor del libro ──→ T004 CLI ──→ T005 verificación
     │                 │                             │
     └── checkpoint 0  └── checkpoint 1              └── checkpoint 2 ────────┘
```

T002 va antes que T003 porque el escritor consume las funciones puras. T004 va
después del escritor porque solo lo invoca. T005 cierra todo. No hay trabajo
paralelo seguro: todos comparten la definición de los 11 indicadores.

## Fases verticales y checkpoints

### Fase 0 · Configuración (T001)

Ruta del archivo nuevo y lista de los 7 cortes, sin cambiar constantes
existentes. El libro principal no se toca.

**Checkpoint 0:** `pytest tests/test_config.py` y `pyflakes` limpios; la lista
de cortes imprime 7 nombres exactos; corrida del libro principal → `IDÉNTICO`.

### Fase 1 · Cálculo compartido (T002)

Funciones puras nuevas en `hojas/indicadores.py` + tests con filas sintéticas.
`escribir_indicadores` queda sin cambios.

**Checkpoint 1:** los 11 valores coinciden con la aritmética de las fórmulas;
MIN por banco (la mediana de los 54, negativos incluidos, solo para `Leyenda`);
eficiencia con ingresos ≤ 0 → `n.a.`, distinto de `n.d.`; división segura →
`n.d.`; `comparar.py` del libro principal → `IDÉNTICO`.

### Fase 2 · Libro compañero y CLI (T003–T004)

Escritor de las 7 hojas + `Leyenda`, y entry point con `--out`/`--help`. Primera
corrida real con las entradas del proyecto.

**Checkpoint 2:** el `.xlsx` nuevo existe con 7 hojas de corte + `Leyenda`, 54
filas y 15 columnas por corte, cero fórmulas, `n.d.` en Q3 2026; `--help` y
`--out RUTA` funcionan; `pytest` y `pyflakes` limpios.

### Fase 3 · Cierre (T005)

Verificación global y registro de resultados en `task.md`.

**Checkpoint 3:** gate humano; sin `git commit` ni `git push`.

## Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Cambiar el libro principal al extraer la lógica | Alto | Solo agregar funciones nuevas en `indicadores.py`; no editar `escribir_indicadores`, `main.py` ni `generar_banca_multiple.py`. Comparar contra referencia en T001, T002 y T005 → `IDÉNTICO` (exit 0). |
| Fórmulas convertidas a valores con escala distinta | Alto | Usar la tabla de correspondencia de arriba y escribir con `FMT_PORC`, sin multiplicar por 100. Test de paridad con filas sintéticas y revisión de un banco real. |
| Celdas vacías por falta de valor cacheado | Alto | Escribir siempre número o texto (`ND` / `n.a.`); test que recorre todo el rango y falla si `cell.data_type == "f"` o si la celda está vacía. |
| MIN escrito como mediana repetida | Medio | Escribir `AI/AC` por banco; la mediana de los 54 (negativos incluidos) solo se documenta en `Leyenda`; test que comprueba valores distintos entre bancos. |
| Q3 2026 con datos donde debe decir `n.d.` | Medio | División segura + regla explícita de desfase para ICAP y CCL/LCR en `2026 Q3`; test con fila sintética y comprobación en la corrida real. |
| Fechas de cierre incorrectas (hojas que sobran o faltan) | Medio | Derivar los cortes de `ANIOS` y meses 3/6/9/12; 2026 no genera Q4; test de nombres exactos y orden. |
| `n.a.` de eficiencia convertido en `n.d.` (decisión resuelta) | Medio | No usar `_celda_numero` para los indicadores; escritor propio que conserva el texto exacto `n.a.`; test específico que lo distingue de `n.d.`. |
| `Leyenda` incompleta o en posición incorrecta | Bajo | Alimentarla de `NOTA_LIQUIDEZ` + notas de `n.d.` y MIN; crearla al final del `Workbook`; test de orden de `sheetnames`. |
| `--out` no respeta la ruta / ayuda incompleta | Bajo | `--help` con `argparse`; test de subprocess que pase `--out tmp_path` y verifique el archivo, sin tocar la CLI del libro principal. |

## Cómo verificar

Antes de T001 se guarda la referencia del libro principal con el código actual
(ver `AGENTS.md` § "Verificar un cambio"). Al cierre:

```bash
.venv/bin/pytest
.venv/bin/pyflakes banca_multiple/ tests generar_vista_copilot.py
.venv/bin/python generar_vista_copilot.py --help | grep -- --out
.venv/bin/python generar_vista_copilot.py --out /tmp/vista_copilot.xlsx
.venv/bin/python -c "from openpyxl import load_workbook; wb=load_workbook('/tmp/vista_copilot.xlsx'); print(wb.sheetnames); print([(ws.title, ws.max_row-5+1, ws.max_column, sum(c.data_type=='f' for row in ws.iter_rows() for c in row)) for ws in wb.worksheets if ws.title!='Leyenda'])"
.venv/bin/python generar_banca_multiple.py --out /tmp/bancos.xlsx > /tmp/salida2.txt
.venv/bin/python scripts/comparar.py \
    --xlsx-a /tmp/referencia.xlsx --xlsx-b /tmp/bancos.xlsx \
    --stdout-a /tmp/salida1.txt --stdout-b /tmp/salida2.txt
```

Criterios de la verificación:

- `pytest` (70 pruebas existentes + las nuevas) y `pyflakes` sin errores.
- `--help` documenta `--out`; `--out RUTA` escribe exactamente en esa ruta.
- Libro compañero: 7 hojas de corte en orden + `Leyenda` al final; 54 filas y
  15 columnas por corte; cero fórmulas y cero celdas vacías en los indicadores;
  Q3 2026 con ICAP y CCL/LCR en `n.d.`; MIN distinto por banco y mediana solo
  en `Leyenda`; eficiencia con ingresos ≤ 0 en `n.a.`, no en `n.d.`.
- Libro principal: `generar_banca_multiple.py` y su CLI intactos y
  `comparar.py` → **`IDÉNTICO` (exit 0)**.
- En Windows usar `.venv\Scripts\python.exe` y `.venv\Scripts\pytest.exe`.

## Decisiones resueltas (gate)

- **MIN:** se escribe el MIN calculado de cada banco (`AI/AC`), no la mediana
  repetida. La mediana de los 54 (negativos incluidos) se menciona solo en
  `Leyenda` como referencia del semáforo original.
- **Índice de Eficiencia:** se conserva `n.a.` cuando los ingresos de operación
  son ≤ 0, igual que el libro principal; es distinto de `n.d.`.

## Open Questions

- Etiqueta exacta de «Mes de corte»: se asume texto del mes (`Septiembre`), según
  la suposición ya registrada en la spec.
