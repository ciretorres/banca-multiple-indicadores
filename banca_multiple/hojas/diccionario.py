"""Funciones para crear y dar formato a la hoja «Diccionario»."""

from __future__ import annotations

from openpyxl import Workbook

from ..estilos import (
    ENC_DICCIONARIO,
    FILA_DATOS,
    FILA_ENC,
    _borde_y_banda,
    _estilo_encabezado,
    _notas,
    _texto,
    _texto_envuelto,
    _titulo,
)
from ..fichas import FICHAS
from ..utilidades import enumerar


def escribir_diccionario(wb: Workbook, anios: list[int]) -> None:
    ws = wb.create_sheet("Diccionario")
    ncols = len(ENC_DICCIONARIO)

    _titulo(
        ws,
        ncols,
        "BANCA MÚLTIPLE · Diccionario de indicadores",
        "Qué mide cada indicador y cómo se calcula",
        "Cada renglón corresponde a una columna de las hojas "
        f"{enumerar([f'Indicadores {a}' for a in anios])}.",
    )

    for j, encabezado in enumerate(ENC_DICCIONARIO, start=1):
        ws.cell(row=FILA_ENC, column=j, value=encabezado)
    _estilo_encabezado(ws, FILA_ENC, ncols, alto=32)

    for i, ficha in enumerate(FICHAS):
        r = FILA_DATOS + i
        _texto(ws, r, 1, ficha.indicador, negrita=True)
        _texto_envuelto(ws, r, 2, ficha.formula, alto=34)
        _texto(ws, r, 3, ficha.grupo, alineacion="center")
        _texto_envuelto(ws, r, 4, ficha.descripcion, alto=40)
        _borde_y_banda(ws, r, ncols, i % 2 == 1)

    ultima = FILA_DATOS + len(FICHAS) - 1

    notas = [
        "ICAP con lag de un mes: no disponible en septiembre 2026.",
        "CCL/LCR: n.d. en V1 por falta de datos.",
        "Crecimiento se reporta solo nominal en V1.",
    ]
    _notas(ws, ncols, ultima + 2, notas)

    for col, ancho in {"A": 30, "B": 62, "C": 28, "D": 88}.items():
        ws.column_dimensions[col].width = ancho

    ws.freeze_panes = f"A{FILA_DATOS}"
    ws.sheet_view.showGridLines = False