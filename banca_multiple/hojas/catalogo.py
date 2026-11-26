"""Hoja Catálogo de bancos."""

from __future__ import annotations

import calendar
import re

from openpyxl.styles import Alignment
from openpyxl.utils import get_column_letter

from ..config import BE_UNIVERSO, MESES
from ..estilos import (
    ENC_CATALOGO,
    FILA_DATOS,
    FILA_ENC,
    FMT_FECHA,
    _borde_y_banda,
    _celda_numero,
    _estilo_encabezado,
    _notas,
    _texto,
    _titulo,
)


def _corte_be() -> tuple[int, int, str]:
    m = re.search(r"(\d{4})(\d{2})", BE_UNIVERSO)
    anio, mes = (int(x) for x in m.groups())
    ultimo = calendar.monthrange(anio, mes)[1]
    return anio, mes, f"{ultimo} de {MESES[mes].lower()} de {anio}"


def escribir_catalogo(wb, universo, nombres, bajas) -> None:
    ws = wb.create_sheet("Catálogo")
    ncols = len(ENC_CATALOGO)
    anio, mes, corte = _corte_be()

    _titulo(
        ws,
        ncols,
        "BANCA MÚLTIPLE · Catálogo",
        f"{len(universo)} bancos autorizados en operación · Información al {corte}",
        "Fuente: BE BM 202609, hoja Evaluación Calidad Detallada.",
    )

    for j, enc in enumerate(ENC_CATALOGO, start=1):
        ws.cell(row=FILA_ENC, column=j, value=enc)
    _estilo_encabezado(ws, FILA_ENC, ncols, alto=40)

    for i, reg in enumerate(universo):
        r = FILA_DATOS + i
        _celda_numero(ws, r, 1, reg["consecutivo"], "0")
        _texto(ws, r, 2, reg["clave"], alineacion="center")
        _texto(ws, r, 3, nombres.get(reg["clave"], reg["nombre"]), negrita=True)
        _texto(ws, r, 4, reg.get("federacion", "n.d."))
        _texto(ws, r, 5, reg.get("nivel", "n.d."), alineacion="center")
        _texto(ws, r, 6, reg.get("estatus", "n.d."), alineacion="center")
        _texto(ws, r, 7, reg.get("tipo", "n.d."), alineacion="center")
        fecha = reg.get("fecha_autorizacion")
        if fecha is None:
            _texto(ws, r, 8, "n.d.", alineacion="center")
        else:
            celda = ws.cell(row=r, column=8, value=fecha)
            celda.number_format = FMT_FECHA
            celda.alignment = Alignment(horizontal="center", vertical="center")
        _borde_y_banda(ws, r, ncols, i % 2 == 1)
    ultima = FILA_DATOS + len(universo) - 1
    notas = [
        f"Fuente del catálogo: {BE_UNIVERSO}, hoja Evaluación Calidad Detallada.",
        "Los 54 bancos con código CASFIM 040xxx que reportan en el BE 202609.",
    ]
    _notas(ws, ncols, ultima + 2, notas)

    anchos = {"A": 6, "B": 13, "C": 28, "D": 16, "E": 8, "F": 14, "G": 10, "H": 14}
    for col, ancho in anchos.items():
        ws.column_dimensions[col].width = ancho
    ws.freeze_panes = f"C{FILA_DATOS}"
    ws.auto_filter.ref = f"A{FILA_ENC}:{get_column_letter(ncols)}{ultima}"
    ws.sheet_view.showGridLines = False