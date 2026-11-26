"""Funciones para crear y dar formato a la hoja «Semáforos»."""

from __future__ import annotations

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill

from ..estilos import (
    BORDE,
    FILA_DATOS,
    FILA_ENC,
    ENC_SEMAFOROS,
    _estilo_encabezado,
    _notas,
    _titulo,
)
from ..fichas import COLORES, FICHAS_SEMAFORO, TOTAL_REGLAS
from ..utilidades import enumerar


def escribir_semaforos(wb: Workbook, anios: list[int]) -> None:
    ws = wb.create_sheet("Semáforos")
    ncols = len(ENC_SEMAFOROS)

    _titulo(
        ws,
        ncols,
        "BANCA MÚLTIPLE · Semáforos",
        "Umbrales de referencia por indicador",
        "Verde = dentro del rango objetivo · Amarillo = vigilancia · "
        "Rojo = fuera de rango o n.a.",
    )

    for j, encabezado in enumerate(ENC_SEMAFOROS, start=1):
        ws.cell(row=FILA_ENC, column=j, value=encabezado)
    _estilo_encabezado(ws, FILA_ENC, ncols, alto=24)

    fila = FILA_DATOS
    for ficha in FICHAS_SEMAFORO:
        ws.merge_cells(start_row=fila, start_column=1, end_row=fila, end_column=ncols)
        titulo = ws.cell(
            row=fila,
            column=1,
            value=f"{ficha.indicador}  ·  {ficha.grupo}  ·  columna {ficha.columna} de Indicadores",
        )
        titulo.font = Font(bold=True, color="FFFFFF", size=10)
        titulo.fill = PatternFill("solid", fgColor="2F5597")
        titulo.alignment = Alignment(horizontal="left", vertical="center", indent=1)
        ws.row_dimensions[fila].height = 20
        fila += 1

        etiqueta = ws.cell(row=fila, column=1, value="Umbral")
        etiqueta.font = Font(bold=True, size=10)
        etiqueta.alignment = Alignment(horizontal="left", vertical="center", indent=1)
        etiqueta.border = Border(left=BORDE, right=BORDE, top=BORDE, bottom=BORDE)

        por_color: dict[str, list[str]] = {}
        for texto, _, color in ficha.tramos:
            por_color.setdefault(color, []).append(texto)

        for col, color in enumerate(("verde", "amarillo", "rojo"), start=2):
            celda = ws.cell(row=fila, column=col)
            if color in por_color:
                relleno, fuente = COLORES[color]
                celda.value = " · ".join(por_color[color])
                celda.fill = relleno
                celda.font = fuente
            else:
                celda.value = "—"
                celda.font = Font(color="A6A6A6")
            celda.alignment = Alignment(horizontal="center", vertical="center")
            celda.border = Border(left=BORDE, right=BORDE, top=BORDE, bottom=BORDE)

        ws.row_dimensions[fila].height = 20
        fila += 1

        celda = ficha.columna + str(FILA_DATOS)
        detalles = []
        for texto, condicion, _ in ficha.tramos:
            detalles.append(f"{texto} → {condicion.format(c=celda)}")

        ws.merge_cells(start_row=fila, start_column=1, end_row=fila, end_column=ncols)
        nota = ws.cell(row=fila, column=1, value="Excel (fracción): " + " · ".join(detalles))
        nota.font = Font(size=8, italic=True, color="595959")
        nota.alignment = Alignment(horizontal="left", vertical="center", indent=1)
        ws.row_dimensions[fila].height = 16
        fila += 2

    hojas_indicadores = enumerar([f"Indicadores {a}" for a in anios])
    notas = [
        f"Umbrales aplicados en {hojas_indicadores} ({len(FICHAS_SEMAFORO)} indicadores, {TOTAL_REGLAS} reglas).",
    ]
    _notas(ws, ncols, fila + 1, notas)

    for col, ancho in {"A": 40, "B": 24, "C": 24, "D": 24}.items():
        ws.column_dimensions[col].width = ancho

    ws.freeze_panes = f"A{FILA_DATOS}"
    ws.sheet_view.showGridLines = False