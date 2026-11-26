"""Arma el libro compañero con cortes trimestrales en valores, sin fórmulas."""

from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter

from .config import CORTES_TRIMESTRALES, MESES, ND, NOTA_LIQUIDEZ
from .estilos import (
    FILA_DATOS,
    FILA_ENC,
    FMT_PORC,
    FMT_TEXTO,
    _borde_y_banda,
    _estilo_encabezado,
    _notas,
    _texto,
    _titulo,
)
from .hojas.indicadores import NOMBRES_INDICADORES, calcular_indicadores, calcular_mediana_min

ENC_VISTA_COPILOT = [
    "No.", "Banco", "Mes de corte", "Trimestre", *NOMBRES_INDICADORES,
]


def _celda_valor(ws, fila: int, col: int, valor) -> None:
    """Escribe un número con FMT_PORC o el texto exacto (n.d. / n.a.)."""
    celda = ws.cell(row=fila, column=col)
    if isinstance(valor, (int, float)):
        celda.value = float(valor)
        celda.number_format = FMT_PORC
        celda.alignment = Alignment(horizontal="right", vertical="center")
    else:
        celda.value = valor
        celda.number_format = FMT_TEXTO
        celda.font = Font(italic=True, color="808080")
        celda.alignment = Alignment(horizontal="center", vertical="center")


def _escribir_corte(wb, nombre, anio, mes, filas_del_anio) -> None:
    ws = wb.create_sheet(nombre)
    ncols = len(ENC_VISTA_COPILOT)

    _titulo(
        ws,
        ncols,
        f"BANCA MÚLTIPLE · {nombre}",
        f"{MESES[mes]} {anio} · 54 bancos",
        "Indicadores calculados en Python: valores, sin fórmulas.",
    )
    for j, encabezado in enumerate(ENC_VISTA_COPILOT, start=1):
        ws.cell(row=FILA_ENC, column=j, value=encabezado)
    _estilo_encabezado(ws, FILA_ENC, ncols, alto=48)

    del_mes = [f for f in filas_del_anio if f["mes"] == MESES[mes]]
    for i, fila in enumerate(del_mes):
        r = FILA_DATOS + i
        ws.cell(row=r, column=1, value=fila["no"]).number_format = "0"
        _texto(ws, r, 2, fila["banco"], negrita=True)
        _texto(ws, r, 3, MESES[mes], alineacion="center")
        _texto(ws, r, 4, fila["trimestre"], alineacion="center")

        valores = calcular_indicadores(fila)
        if nombre == "2026 Q3":  # desfase de publicación: último dato CCL 202606
            valores["ICAP"] = ND
            valores["CCL/LCR"] = ND
        for j, clave in enumerate(NOMBRES_INDICADORES, start=5):
            _celda_valor(ws, r, j, valores[clave])

        _borde_y_banda(ws, r, ncols, i % 2 == 1)

    ultima = FILA_DATOS + len(del_mes) - 1
    anchos = {"A": 6, "B": 24, "C": 15, "D": 12}
    for j in range(5, ncols + 1):
        anchos[get_column_letter(j)] = 20
    for col, ancho in anchos.items():
        ws.column_dimensions[col].width = ancho
    ws.freeze_panes = f"E{FILA_DATOS}"
    ws.auto_filter.ref = f"A{FILA_ENC}:{get_column_letter(ncols)}{ultima}"
    ws.sheet_view.showGridLines = False


def _escribir_leyenda(wb, filas: dict[int, list[dict]]) -> None:
    ws = wb.create_sheet("Leyenda")

    _titulo(
        ws,
        3,
        "BANCA MÚLTIPLE · Leyenda",
        "Vista para Copilot · cortes trimestrales 2025–2026",
        "Los indicadores son valores calculados, no fórmulas.",
    )
    notas = [
        *NOTA_LIQUIDEZ,
        "n.d. = dato no disponible en el corte; se escribe como texto y no como celda vacía.",
        "n.a. = índice de eficiencia no aplicable cuando los ingresos totales de la operación son ≤ 0.",
        "MIN = Margen Financiero Ajustado 12M / Activo productivo promedio 12M de cada banco. "
        "El MIN publicado por la CNBV no está ajustado; en esta vista se usa la serie ajustada del libro.",
        "La mediana de los 54 bancos del mes (negativos incluidos) es la referencia del semáforo "
        "original; se muestra por corte abajo y no se repite como valor de cada banco.",
    ]
    _notas(ws, 3, FILA_DATOS, notas)

    fila = FILA_DATOS + len(notas) + 1
    for j, encabezado in enumerate(
        ("Corte", "Mes de corte", "Mediana MIN (54 bancos)"), start=1
    ):
        ws.cell(row=fila, column=j, value=encabezado)
    _estilo_encabezado(ws, fila, 3, alto=24)

    for nombre, anio, _, mes in CORTES_TRIMESTRALES:
        fila += 1
        del_mes = [f for f in filas[anio] if f["mes"] == MESES[mes]]
        ws.cell(row=fila, column=1, value=nombre)
        ws.cell(row=fila, column=2, value=MESES[mes])
        celda = ws.cell(row=fila, column=3, value=calcular_mediana_min(del_mes))
        celda.number_format = FMT_PORC

    for col, ancho in (("A", 14), ("B", 18), ("C", 24)):
        ws.column_dimensions[col].width = ancho
    ws.sheet_view.showGridLines = False


def escribir_vista_copilot(filas: dict[int, list[dict]], ruta: Path) -> None:
    """Escribe el libro compañero con los siete cortes y la Leyenda al final."""
    wb = Workbook()
    wb.remove(wb.active)

    for nombre, anio, _, mes in CORTES_TRIMESTRALES:
        _escribir_corte(wb, nombre, anio, mes, filas[anio])
    _escribir_leyenda(wb, filas)

    wb.properties.title = "Bancos Multiples - Cortes Trimestrales"
    wb.properties.creator = "Generador automatico (tablero CNBV + BE)"

    ruta.parent.mkdir(parents=True, exist_ok=True)
    wb.save(ruta)
