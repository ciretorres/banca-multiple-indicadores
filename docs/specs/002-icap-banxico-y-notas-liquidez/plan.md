# Plan de implementación: ICAP de Banco de México y notas de liquidez

Spec: `docs/specs/002-icap-banxico-y-notas-liquidez/spec.md` (aprobada).
Tareas: `task.md` de esta carpeta.

## Enfoque técnico

Se agrega una fuente nueva (PDF de Banxico) al flujo ya existente sin tocar la
lógica mensual/trimestral: `config` → `pdf_icap` → `filas`/`main` → hojas y
validación. Cada fase deja el libro generable y verificable.

El riesgo mayor (leer un PDF cuyo texto trae espacios entre caracteres) se
ataca primero y de forma aislada con un fixture de texto: `leer_icap` no depende
de `entradas/`, recibe el mapa `clave → nombre` que `main.py` ya construye con
`leer_universo`, y devuelve un dict con `fecha`, 54 bancos y `total`.

En `Datos Fuente` se agregan tres columnas **al final**, después de
`Margen Financiero Ajustado 12M` (col 35): 36 = `CCB (%)`, 37 = `CCF (%)`,
38 = `Categoría`. No se inserta nada en medio: las 35 columnas actuales, sus
fórmulas y las referencias desde `Indicadores` quedan intactas. Solo cambian
`estilos.py` (encabezados), `datos_fuente.py` (celdas nuevas y nota) y la nota
de `Indicadores`.

La validación nueva compara, solo en el mes del PDF, ICAP/CCB/CCF del tablero
(`4021750`, `4021754`, `4021755`) contra el PDF, por banco y para el Total, con
tolerancia de 0.02 pts. El Total del PDF nunca se escribe como fila.

## Decisiones de diseño

- `pypdf` se usa únicamente dentro de `pdf_icap.py`; `utilidades._norm` sigue
  siendo la base para normalizar acentos y mayúsculas.
- El mes del corte sale de `ICAP_BM_YYYYMM.pdf` con una expresión regular; la
  ruta por defecto es `DIR_ENTRADAS / PDF_ICAP` y `--pdf-icap` la sobreescribe.
  Subir otro mes solo cambia esa configuración o esa bandera.
- CCB/CCF del PDF son la fuente principal de las columnas nuevas; los del
  tablero sirven de respaldo y de comparación. Categoría se escribe como texto.
- Sin PDF para un mes, `ccb`, `ccf` y `categoria` valen `ND` (`n.d.`).
- Las columnas nuevas se añaden al final de `Datos Fuente` (36–38, letras
  AJ–AL); las 35 columnas y sus fórmulas no se reindexan.
- `Indicadores` no gana columnas ni cambia sus fórmulas: solo cambia el texto
  de la nota de liquidez.

## Grafo de dependencias y orden

```
T001 pypdf ──→ T002 config ──→ T003 pdf_icap
                                  │
                 ┌────────────────┼─────────────────┐
                 ▼                ▼                 ▼
          T004 main/filas   T005 columnas      T007 validación
                 └────────→ libro ←─────────────┘
                                  │
                 T006 docs ──→ T008 verificación global
```

T003 va antes que T004/T005/T007 porque todos consumen su salida. T006 es
independiente, pero se cierra con T008 para documentar el comportamiento final.

## Fases verticales y checkpoints

### Fase 0 · Base (T001–T002)

Dependencia instalada y rutas/códigos configurados. Aún no cambia el libro.

**Checkpoint 0:** `import pypdf` funciona con `.venv/bin/python` (y con
`.venv\Scripts\python.exe` en Windows); `pytest` y `pyflakes` limpios.

### Fase 1 · Lector del PDF (T003)

Primer corte vertical: `leer_icap` entrega fecha, 54 bancos y Total con los
cuatro campos. Se prueba contra texto sintético, sin depender del PDF real.

**Checkpoint 1:** `tests/test_pdf_icap.py` pasa; falla claro si faltan
encabezados, filas o el renglón Total; `pyflakes` limpio.

### Fase 2 · El PDF entra al libro (T004–T005)

CLI, filas con datos solo en el mes del PDF y tres columnas nuevas al final de
`Datos Fuente`. Sin reindexación: las fórmulas existentes y las comprobaciones
de `validacion_libro.py` no se tocan.

**Checkpoint 2:** corrida default genera el libro con `CCB (%)`, `CCF (%)` y
`Categoría` en las columnas 36–38, con valores en 202608 y `n.d.` en otros
meses; las fórmulas previas siguen iguales; `validar_libro` da OK; `pytest` y
`pyflakes` limpios.

### Fase 3 · Validación y cierre (T006–T008)

Sección de validación PDF vs tablero, notas de liquidez en documentación y
verificación global con diffs esperados.

**Checkpoint 3:** corrida default termina con `Validación general: OK` y exit 0;
`comparar.py` muestra únicamente los diffs esperados y están documentados.

## Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Texto del PDF con espacios entre caracteres (`B a n c o   B i n e o`) | Alto | Normalizar con `_norm` y quitar todos los espacios antes de comparar; localizar columnas por texto de encabezado, no por posición fija; fixture sintético + prueba rápida con el PDF real. |
| Nombres del PDF no coinciden con el catálogo `040xxx` | Alto | Usar el mapa `clave → nombre` de `leer_universo`; comparar sin acentos, mayúsculas ni espacios; si un nombre no se mapea, `SystemExit` con la lista de nombres no reconocidos. Nunca hardcodear claves. |
| Categoría como texto (`"I"`) y `n.d.` en otros meses | Medio | Escribir la columna con `_texto` y `FMT_TEXTO`; `ND` en meses sin PDF; comprobar en el test que los 54 bancos y el Total traen categoría. |
| Mes derivado del nombre del archivo | Medio | Regex `ICAP_BM_(\d{6})\.pdf` validada en `leer_icap`; `main.py` verifica que esa fecha esté en el rango generado y falla con mensaje claro si no. |
| Cambio de formato del PDF en entregas futuras | Medio | Buscar encabezados (`ICAP`, `CCB`, `CCF`, `Categoría`) y renglón Total por texto; si falta algo, `SystemExit` con archivo, columna o fila. |
| Columnas nuevas al final de `Datos Fuente` omitidas en anchos, autofiltro o notas | Medio | En T005 ampliar `ENC_DATOS` a 38 encabezados y escribir las columnas 36–38; las fórmulas y comprobaciones de las 35 columnas actuales no cambian. Verificar con `--out` y `Validación general: OK`. |
| `comparar.py` no da `IDÉNTICO` (exit 1) | Medio | Esperado en esta spec: documentar los diffs (3 columnas nuevas al final, notas, sección nueva en stdout) y comprobar que las 35 columnas previas y sus fórmulas quedan idénticas. No exigir exit 0 del comparador. |
| `pypdf` ausente en otro equipo | Medio | T001 agrega la dependencia a `pyproject.toml`, instala con `.venv/bin/pip install -e ".[dev]"` y verifica el import en ambos ejecutables (Unix/Windows). |

## Cómo verificar

Con el código previo a T005 (spec 001) se guarda la referencia; después se
comparan libro y stdout con los comandos de `AGENTS.md`:

```bash
.venv/bin/pytest
.venv/bin/pyflakes banca_multiple/ tests generar_banca_multiple.py
.venv/bin/python generar_banca_multiple.py --help | grep -- --pdf-icap
.venv/bin/python generar_banca_multiple.py --out /tmp/bancos.xlsx > /tmp/salida2.txt
.venv/bin/python scripts/comparar.py \
    --xlsx-a /tmp/referencia.xlsx --xlsx-b /tmp/bancos.xlsx \
    --stdout-a /tmp/salida1.txt --stdout-b /tmp/salida2.txt
```

Criterios de aceptación de la verificación:

- `pytest` y `pyflakes` sin errores; `--help` documenta `--pdf-icap`.
- Corrida default: `Validación general: OK`, exit 0, con la sección
  `ICAP / CCB / CCF del PDF vs tablero (202608)` y peor diferencia ≤ 0.02 pts.
- `Datos Fuente`: los 35 encabezados actuales intactos y `CCB (%)`, `CCF (%)`,
  `Categoría` al final (cols 36–38, AJ–AL); valores del PDF en 202608 y `n.d.`
  en los demás meses; mismas filas (54 por mes) y mismas 7 hojas. Las fórmulas
  de `Datos Fuente` e `Indicadores` no cambian.
- Diffs esperados de `comparar.py`: solo las columnas 36–38 en las dos hojas
  `Datos Fuente`, las notas de liquidez y la sección nueva en stdout. Sin
  corrimiento de columnas ni cambios de fórmulas; todo lo demás idéntico.

## Open Questions

- Etiquetas exactas de los encabezados y del renglón Total en
  `entradas/ICAP_BM_202608.pdf`: se confirman al implementar T003; el lector
  debe fallar con mensaje claro si no aparecen.
