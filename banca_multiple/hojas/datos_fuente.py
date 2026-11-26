"""Funciones para crear y dar formato a las hojas de datos fuente."""

from __future__ import annotations

from openpyxl.utils import get_column_letter

from ..config import ANIOS, MESES, ND, NOTA_ICAP_PDF, NOTA_LIQUIDEZ
from ..estilos import (
    ENC_DATOS,
    FILA_DATOS,
    FILA_ENC,
    FMT_ANIO,
    FMT_MILES,
    FMT_PORC,
    _borde_y_banda,
    _celda_formula,
    _celda_numero,
    _estilo_encabezado,
    _notas,
    _texto,
    _titulo,
)


def _en_ratio(valor):
    """Pasa puntos porcentuales a ratio para celdas con FMT_PORC."""
    return valor / 100 if isinstance(valor, (int, float)) else valor


def escribir_datos_fuente(wb, filas, anio, n_entidades) -> None:
    nombre_hoja = f"Datos Fuente {anio}"
    ws = wb.create_sheet(nombre_hoja)
    ncols = len(ENC_DATOS)

    meses = ANIOS[anio]
    rango = f"{MESES[min(meses)]}–{MESES[max(meses)]} {anio}"
    _titulo(
        ws,
        ncols,
        f"BANCA MÚLTIPLE · Datos Fuente {anio}",
        f"{rango} · {n_entidades} bancos por mes · {len(filas)} filas",
        "Cifras en MILLONES DE PESOS. Fuente: tablero CNBV (040_TO.csv), "
        "tipo_saldo = Consolidado con SOFOMER.",
    )

    for j, enc in enumerate(ENC_DATOS, start=1):
        ws.cell(row=FILA_ENC, column=j, value=enc)
    _estilo_encabezado(ws, FILA_ENC, ncols, alto=62)

    for i, f in enumerate(filas):
        r = FILA_DATOS + i
        _celda_numero(ws, r, 1, f["no"], "0")
        _texto(ws, r, 2, f["banco"], negrita=True)
        _celda_numero(ws, r, 3, f["anio"], FMT_ANIO)
        _texto(ws, r, 4, f["mes"], alineacion="center")
        _texto(ws, r, 5, f["trimestre"], alineacion="center")

        _celda_numero(ws, r, 6, f["activos"], FMT_MILES)
        _celda_numero(ws, r, 7, f["activos_riesgo"], FMT_MILES)
        _celda_numero(ws, r, 8, f["capital_neto"], FMT_MILES)
        if f.get("icap_pdf") is not None:
            _celda_numero(ws, r, 9, _en_ratio(f["icap_pdf"]), FMT_PORC)
        else:
            _celda_formula(ws, r, 9, f'=IFERROR(H{r}/G{r},"{ND}")', FMT_PORC)
        _celda_numero(ws, r, 10, f["cartera_total"], FMT_MILES)
        _celda_numero(ws, r, 11, f["cartera_e3"], FMT_MILES)
        _celda_numero(ws, r, 12, f["cartera_neta"], FMT_MILES)
        _celda_numero(ws, r, 13, f["estimaciones"], FMT_MILES)
        _celda_numero(ws, r, 14, f["ingresos_int"], FMT_MILES)
        _celda_numero(ws, r, 15, f["gastos_int"], FMT_MILES)
        _celda_formula(ws, r, 16, f'=IFERROR(N{r}-O{r},"{ND}")', FMT_MILES)
        _celda_numero(ws, r, 17, f["margen_ajustado"], FMT_MILES)
        _celda_numero(ws, r, 18, f["gastos_adm"], FMT_MILES)
        _celda_numero(ws, r, 19, f["resultado_neto"], FMT_MILES)
        _celda_numero(ws, r, 20, f["captacion_tradicional"], FMT_MILES)
        _celda_numero(ws, r, 21, f["captacion_total"], FMT_MILES)
        _celda_numero(ws, r, 22, f["captacion_prev"], FMT_MILES)
        _celda_numero(ws, r, 23, f["cartera_total_prev"], FMT_MILES)
        _celda_numero(ws, r, 24, f["capital_contable"], FMT_MILES)
        _celda_numero(ws, r, 25, f["resultado_12m"], FMT_MILES)
        _celda_numero(ws, r, 26, f["activos_prom_12m"], FMT_MILES)
        _celda_numero(ws, r, 27, f["capital_prom_12m"], FMT_MILES)
        _celda_numero(ws, r, 28, f["margen_fin_12m"], FMT_MILES)
        _celda_numero(ws, r, 29, f["activo_prod_prom_12m"], FMT_MILES)
        _celda_numero(ws, r, 30, f["ingresos_operacion"], FMT_MILES)
        _celda_numero(ws, r, 31, f["captacion_prev_anio"], FMT_MILES)
        _celda_numero(ws, r, 32, f["cartera_total_prev_anio"], FMT_MILES)
        _celda_numero(ws, r, 33, f["ccl"], FMT_PORC)
        _celda_numero(ws, r, 34, f["cfen"], FMT_PORC)
        _celda_numero(ws, r, 35, f["margen_ajustado_12m"], FMT_MILES)
        _celda_numero(ws, r, 36, _en_ratio(f["ccb"]), FMT_PORC)
        _celda_numero(ws, r, 37, _en_ratio(f["ccf"]), FMT_PORC)
        _texto(ws, r, 38, f["categoria"], alineacion="center")

        _borde_y_banda(ws, r, ncols, i % 2 == 1)

    ultima = FILA_DATOS + len(filas) - 1
    notas = [
        "Unidades: millones de pesos (tablero en pesos ÷ 1,000,000).",
        "ICAP (col I) = Capital Neto / Activos sujetos a riesgo.",
        NOTA_ICAP_PDF,
        "Margen Financiero (col P) = Ingresos por intereses − Gastos por intereses.",
        *NOTA_LIQUIDEZ,
    ]
    _notas(ws, ncols, ultima + 2, notas)

    anchos = {"A": 6, "B": 24, "C": 8, "D": 11, "E": 10}
    for j in range(6, ncols + 1):
        anchos[get_column_letter(j)] = 15
    for col, ancho in anchos.items():
        ws.column_dimensions[col].width = ancho

    ws.freeze_panes = f"C{FILA_DATOS}"
    ws.auto_filter.ref = f"A{FILA_ENC}:{get_column_letter(ncols)}{ultima}"
    ws.sheet_view.showGridLines = False