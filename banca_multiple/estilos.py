"""Estilos, formatos y funciones auxiliares para las hojas del libro."""

from __future__ import annotations

from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from .config import ND

AZUL = "1F3864"
GRIS = "F2F2F2"
AMBAR = "FFF2CC"
BORDE = Side(style="thin", color="BFBFBF")

FMT_MILES = '#,##0.00;[Red]-#,##0.00'
FMT_PORC = "0.00%"
FMT_ANIO = "0"
FMT_TEXTO = "@"
FMT_FECHA = "dd-mmm-yyyy"

VERDE_FILL = PatternFill("solid", fgColor="D1E7DD")
AMARILLO_FILL = PatternFill("solid", fgColor="FFF3CD")
ROJO_FILL = PatternFill("solid", fgColor="F8D7DA")
VERDE_FONT = Font(color="0F5132", bold=True)
AMARILLO_FONT = Font(color="664D03", bold=True)
ROJO_FONT = Font(color="842029", bold=True)

FILA_ENC = 4
FILA_DATOS = 5

ENC_CATALOGO = [
    "No.", "Clave CASFIM", "Banco", "Categoría", "Estatus", "Tipo",
    "Fecha de Autorización",
]

ENC_DATOS = [
    "No.", "Banco", "Año", "Mes", "Trimestre",
    "Activos Totales\n(millones de pesos)",
    "Activos sujetos a riesgo\n(millones de pesos)",
    "Capital Neto\n(millones de pesos)",
    "ICAP\n(%)",
    "Cartera Total\n(millones de pesos)",
    "Cartera etapa 3\n(millones de pesos)",
    "Cartera Neta\n(millones de pesos)",
    "Estimaciones preventivas\n(millones de pesos)",
    "Ingresos por intereses\n(millones de pesos)",
    "Gastos por intereses\n(millones de pesos)",
    "Margen Financiero\n(millones de pesos)",
    "Margen Financiero Ajustado\n(millones de pesos)",
    "Gastos de administración y promoción\n(millones de pesos)",
    "Resultado Neto\n(millones de pesos)",
    "Captación Tradicional\n(millones de pesos)",
    "Captación Total\n(millones de pesos)",
    "Captación Total mes anterior\n(millones de pesos)",
    "Cartera Total mes anterior\n(millones de pesos)",
    "Capital contable\n(millones de pesos)",
    "Resultado Neto 12M\n(millones de pesos)",
    "Activos promedio 12M\n(millones de pesos)",
    "Capital contable promedio 12M\n(millones de pesos)",
    "Margen Financiero 12M\n(millones de pesos)",
    "Activo productivo promedio 12M\n(millones de pesos)",
    "Ingresos totales de la operación\n(millones de pesos)",
    "Captación Total mismo mes año anterior\n(millones de pesos)",
    "Cartera Total mismo mes año anterior\n(millones de pesos)",
    "CCL\n(%)",
    "CFEN\n(%)",
    "Margen Financiero Ajustado 12M\n(millones de pesos)",
    "CCB\n(%)",
    "CCF\n(%)",
    "Categoría",
]

ENC_INDICADORES = [
    "No.", "Banco", "Año", "Mes", "Trimestre",
    "ICAP\n(%)", "IMOR\n(%)", "ICOR\n(%)", "ROA\n(%)", "ROE\n(%)",
    "MIN\n(%)", "Crecimiento de Captación\n(%)",
    "Crecimiento de Cartera\n(%)",
    "Crédito Neto / Captación\n(%)",
    "Índice de Eficiencia\n(%)",
    "CCL/LCR\n(%)",
]

ENC_DICCIONARIO = ["Indicador", "Fórmula", "Grupo de razón financiera", "Descripción"]
ENC_SEMAFOROS = ["Rango", "Verde", "Amarillo", "Rojo"]


def _estilo_encabezado(ws, fila: int, columnas: int, alto: int = 46) -> None:
    for j in range(1, columnas + 1):
        celda = ws.cell(row=fila, column=j)
        celda.font = Font(bold=True, color="FFFFFF", size=10)
        celda.fill = PatternFill("solid", fgColor=AZUL)
        celda.alignment = Alignment(
            horizontal="center",
            vertical="center",
            wrap_text=True,
        )
        celda.border = Border(
            left=BORDE,
            right=BORDE,
            top=BORDE,
            bottom=Side(style="medium", color=AZUL),
        )
    ws.row_dimensions[fila].height = alto


def _titulo(ws, columnas: int, titulo: str, subtitulo: str, nota: str) -> None:
    ultima = get_column_letter(columnas)
    ws.merge_cells(f"A1:{ultima}1")
    ws["A1"] = titulo
    ws["A1"].font = Font(bold=True, size=14, color=AZUL)
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 22
    ws.merge_cells(f"A2:{ultima}2")
    ws["A2"] = subtitulo
    ws["A2"].font = Font(bold=True, size=11)
    ws["A2"].alignment = Alignment(horizontal="center")
    ws.merge_cells(f"A3:{ultima}3")
    ws["A3"] = nota
    ws["A3"].font = Font(size=9, italic=True, color="595959")
    ws["A3"].alignment = Alignment(horizontal="center", wrap_text=True)
    ws.row_dimensions[3].height = 28


def _notas(ws, columna_final: int, fila: int, textos: list[str]) -> None:
    for texto in textos:
        ws.merge_cells(
            start_row=fila,
            start_column=1,
            end_row=fila,
            end_column=columna_final,
        )
        celda = ws.cell(row=fila, column=1, value=texto)
        celda.font = Font(size=8, color="595959")
        celda.alignment = Alignment(
            horizontal="left",
            vertical="center",
            wrap_text=True,
        )
        ws.row_dimensions[fila].height = 26
        fila += 1


def _texto(ws, fila, col, valor, negrita=False, alineacion="left", color=None):
    celda = ws.cell(row=fila, column=col, value=valor)
    celda.number_format = FMT_TEXTO
    if color:
        celda.font = Font(bold=negrita, italic=color is not None and color != "000000", color=color)
    else:
        celda.font = Font(bold=negrita)
    celda.alignment = Alignment(horizontal=alineacion, vertical="center", wrap_text=False, indent=1 if alineacion == "left" else 0)


def _celda_numero(ws, fila, col, valor, formato):
    celda = ws.cell(row=fila, column=col)
    if isinstance(valor, (int, float)):
        celda.value = float(valor)
        celda.number_format = formato
        celda.font = Font()
        celda.alignment = Alignment(horizontal="right", vertical="center")
    else:
        celda.value = ND
        celda.number_format = FMT_TEXTO
        celda.font = Font(italic=True, color="808080")
        celda.alignment = Alignment(horizontal="center", vertical="center")


def _celda_formula(ws, fila, col, formula, formato):
    celda = ws.cell(row=fila, column=col, value=formula)
    celda.number_format = formato
    celda.font = Font(bold=True, color=AZUL)
    celda.alignment = Alignment(horizontal="right", vertical="center")
    celda.fill = PatternFill("solid", fgColor=AMBAR)


def _borde_y_banda(ws, fila, columnas, banda):
    for j in range(1, columnas + 1):
        celda = ws.cell(row=fila, column=j)
        celda.border = Border(left=BORDE, right=BORDE, top=BORDE, bottom=BORDE)
        if banda and celda.fill.fgColor.rgb in (None, "00000000"):
            celda.fill = PatternFill("solid", fgColor=GRIS)


def _texto_envuelto(ws, fila, col, valor, alto=30):
    celda = ws.cell(row=fila, column=col, value=valor)
    celda.number_format = FMT_TEXTO
    celda.font = Font(size=10)
    celda.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True, indent=1)
    ws.row_dimensions[fila].height = alto