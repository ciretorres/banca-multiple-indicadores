"""Funciones para crear las hojas de indicadores y aplicar sus semáforos."""

from __future__ import annotations

import statistics

from openpyxl import Workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.utils import get_column_letter

from ..config import ANIOS, MESES, ND, NOTA_LIQUIDEZ
from ..estilos import (
    ENC_INDICADORES,
    FILA_DATOS,
    FILA_ENC,
    FMT_ANIO,
    FMT_PORC,
    _borde_y_banda,
    _celda_formula,
    _celda_numero,
    _estilo_encabezado,
    _notas,
    _texto,
    _titulo,
)
from ..fichas import COLORES, COND_NA, FICHAS_SEMAFORO


# Nombres de los 11 indicadores, en el orden de las columnas de la vista.
NOMBRES_INDICADORES = (
    "ICAP", "IMOR", "ICOR", "ROA", "ROE", "MIN",
    "Crec. captación", "Crec. cartera", "Crédito neto/captación",
    "Índice de eficiencia", "CCL/LCR",
)


def _numero(valor):
    return valor if isinstance(valor, (int, float)) else None


def _dividir(numerador, denominador):
    """Equivale a IFERROR: número si es posible, ND si no."""
    num = _numero(numerador)
    den = _numero(denominador)
    if num is None or den is None or den == 0:
        return ND
    return num / den


def _crecimiento(actual, anterior):
    valor = _dividir(actual, anterior)
    return valor - 1 if isinstance(valor, (int, float)) else ND


def calcular_indicadores(fila: dict) -> dict:
    """Calcula los 11 indicadores de un banco con la aritmética del libro."""
    estimaciones = _numero(fila.get("estimaciones"))
    ingresos = _numero(fila.get("ingresos_operacion"))
    ccl = fila.get("ccl")

    if ingresos is None:
        eficiencia = ND
    elif ingresos <= 0:
        eficiencia = "n.a."
    else:
        eficiencia = _dividir(fila.get("gastos_adm"), ingresos)

    return {
        "ICAP": _dividir(fila.get("capital_neto"), fila.get("activos_riesgo")),
        "IMOR": _dividir(fila.get("cartera_e3"), fila.get("cartera_total")),
        "ICOR": (
            ND if estimaciones is None
            else _dividir(abs(estimaciones), fila.get("cartera_e3"))
        ),
        "ROA": _dividir(fila.get("resultado_12m"), fila.get("activos_prom_12m")),
        "ROE": _dividir(fila.get("resultado_12m"), fila.get("capital_prom_12m")),
        "MIN": _dividir(
            fila.get("margen_ajustado_12m"), fila.get("activo_prod_prom_12m")
        ),
        "Crec. captación": _crecimiento(
            fila.get("captacion_total"), fila.get("captacion_prev_anio")
        ),
        "Crec. cartera": _crecimiento(
            fila.get("cartera_total"), fila.get("cartera_total_prev_anio")
        ),
        "Crédito neto/captación": _dividir(
            fila.get("cartera_neta"), fila.get("captacion_tradicional")
        ),
        "Índice de eficiencia": eficiencia,
        "CCL/LCR": ccl if _numero(ccl) is not None else ND,
    }


def calcular_mediana_min(filas_del_mes: list[dict]) -> float:
    """Mediana de MIN de los 54 bancos del mes, negativos incluidos."""
    valores = []
    for fila in filas_del_mes:
        ma = fila.get("margen_ajustado_12m")
        ap = fila.get("activo_prod_prom_12m")
        if isinstance(ma, (int, float)) and isinstance(ap, (int, float)) and ap:
            valores.append(ma / ap)
    return statistics.median(valores) if valores else 0.0


def aplicar_formato_condicional(ws, nfilas: int) -> None:
    primera = FILA_DATOS
    ultima = FILA_DATOS + nfilas - 1

    for ficha in FICHAS_SEMAFORO:
        rango = f"{ficha.columna}{primera}:{ficha.columna}{ultima}"
        celda = f"{ficha.columna}{primera}"

        for _, condicion, color in ficha.tramos:
            relleno, fuente = COLORES[color]

            if condicion == COND_NA:
                regla = condicion.format(c=celda)
            else:
                cond_formateada = condicion.format(c=celda).replace(
                    "$Q5", f"$Q{primera}"
                )
                regla = "AND(ISNUMBER({c}),{cond})".format(
                    c=celda,
                    cond=cond_formateada,
                )

            ws.conditional_formatting.add(
                rango,
                FormulaRule(
                    formula=[regla],
                    fill=relleno,
                    font=fuente,
                    stopIfTrue=False,
                ),
            )


def escribir_indicadores(wb: Workbook, filas: list[dict], anio: int) -> None:
    nombre_hoja = f"Indicadores {anio}"
    ws = wb.create_sheet(nombre_hoja)
    ncols = len(ENC_INDICADORES)
    ref = f"'Datos Fuente {anio}'"

    meses = ANIOS[anio]
    rango = f"{MESES[min(meses)]}–{MESES[max(meses)]} {anio}"
    _titulo(
        ws,
        ncols,
        f"BANCA MÚLTIPLE · Indicadores {anio}",
        f"{rango} · {len(filas)} filas",
        "Indicadores con semáforo. MIN se compara contra la mediana de los 54 bancos del mes.",
    )

    for j, encabezado in enumerate(ENC_INDICADORES, start=1):
        ws.cell(row=FILA_ENC, column=j, value=encabezado)
    _estilo_encabezado(ws, FILA_ENC, ncols, alto=50)

    # Mediana de MIN por mes.
    medianas: dict[str, float] = {}
    for mes in meses:
        vals = []
        for f in filas:
            if f["mes"] != MESES[mes]:
                continue
            ma = f.get("margen_ajustado_12m")
            ap = f.get("activo_prod_prom_12m")
            if isinstance(ma, (int, float)) and isinstance(ap, (int, float)) and ap:
                vals.append(ma / ap)
        medianas[MESES[mes]] = statistics.median(vals) if vals else 0.0

    for i, f in enumerate(filas):
        r = FILA_DATOS + i

        _celda_numero(ws, r, 1, f["no"], "0")
        _texto(ws, r, 2, f["banco"], negrita=True)
        _celda_numero(ws, r, 3, f["anio"], FMT_ANIO)
        _texto(ws, r, 4, f["mes"], alineacion="center")
        _texto(ws, r, 5, f["trimestre"], alineacion="center")

        formulas_pct = {
            6: f'=IFERROR({ref}!I{r},"{ND}")',  # ICAP
            7: f'=IFERROR({ref}!K{r}/{ref}!J{r},"{ND}")',  # IMOR
            8: f'=IFERROR(ABS({ref}!M{r})/{ref}!K{r},"{ND}")',  # ICOR
            9: f'=IFERROR({ref}!Y{r}/{ref}!Z{r},"{ND}")',  # ROA
            10: f'=IFERROR({ref}!Y{r}/{ref}!AA{r},"{ND}")',  # ROE
            11: f'=IFERROR({ref}!AI{r}/{ref}!AC{r},"{ND}")',  # MIN
            12: f'=IFERROR({ref}!U{r}/{ref}!AE{r}-1,"{ND}")',  # Crec. captación
            13: f'=IFERROR({ref}!J{r}/{ref}!AF{r}-1,"{ND}")',  # Crec. cartera
            14: f'=IFERROR({ref}!L{r}/{ref}!T{r},"{ND}")',  # Crédito Neto
            15: (
                f'=IFERROR(IF({ref}!AD{r}<=0,"n.a.",'
                f'{ref}!R{r}/{ref}!AD{r}),"{ND}")'
            ),  # Índice de Eficiencia
            16: f'=IFERROR({ref}!AG{r},"{ND}")',  # CCL
        }
        for col, formula in formulas_pct.items():
            _celda_formula(ws, r, col, formula, FMT_PORC)

        # Columna Q (oculta): mediana de MIN del mes.
        med = medianas.get(f["mes"], 0.0)
        _celda_numero(ws, r, 17, med, FMT_PORC)

        _borde_y_banda(ws, r, ncols, i % 2 == 1)

    ultima = FILA_DATOS + len(filas) - 1

    aplicar_formato_condicional(ws, len(filas))

    # Ocultar columna Q.
    ws.column_dimensions[get_column_letter(17)].hidden = True

    notas = [
        "ICAP = Capital Neto / Activos sujetos a riesgo.",
        "IMOR = Cartera etapa 3 / Cartera Total.",
        "ICOR = ABS(Estimaciones) / Cartera etapa 3.",
        "ROA = Resultado Neto 12M / Activos promedio 12M.",
        "ROE = Resultado Neto 12M / Capital contable promedio 12M.",
        "MIN = Margen Financiero Ajustado 12M / Activo productivo promedio 12M; "
        "semáforo frente a la mediana de los 54 bancos del mes.",
        "Crecimiento de Captación = (Captación Total / Captación Total mismo mes año anterior) − 1.",
        "Crecimiento de Cartera = (Cartera Total / Cartera Total mismo mes año anterior) − 1.",
        "Crédito Neto / Captación = Cartera Neta / Captación Tradicional.",
        "Índice de Eficiencia = Gastos de administración y promoción / Ingresos totales de la operación.",
        *NOTA_LIQUIDEZ,
    ]
    _notas(ws, ncols, ultima + 2, notas)

    anchos = {"A": 6, "B": 24, "C": 8, "D": 11, "E": 10}
    for j in range(6, ncols + 1):
        anchos[get_column_letter(j)] = 18
    for col, ancho in anchos.items():
        ws.column_dimensions[col].width = ancho

    ws.freeze_panes = f"C{FILA_DATOS}"
    ws.auto_filter.ref = f"A{FILA_ENC}:{get_column_letter(ncols)}{ultima}"
    ws.sheet_view.showGridLines = False
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 1
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_title_rows = f"{FILA_ENC}:{FILA_ENC}"