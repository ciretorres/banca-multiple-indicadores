"""Pruebas de las hojas esperadas y del catálogo validado."""

from pathlib import Path

import pytest
from openpyxl import load_workbook

from banca_multiple.config import ANIOS
from banca_multiple.estilos import ENC_CATALOGO, FILA_ENC
from banca_multiple.filas import preparar_filas
from banca_multiple.hojas import escribir_xlsx
from banca_multiple.tablero import leer_tablero
from banca_multiple.utilidades import fecha_mes
from banca_multiple.validacion_libro import hojas_esperadas, validar_libro

FIXTURE = Path(__file__).parent / "fixtures" / "tablero_mini.csv"
UNIVERSO = [
    {"clave": "040002", "consecutivo": 1, "nombre": "Banco Uno"},
    {"clave": "040009", "consecutivo": 2, "nombre": "Banco Dos"},
]


def test_hojas_esperadas_con_anios_no_contiguos_en_orden_descendente():
    assert hojas_esperadas({2025: [], 2026: []}) == [
        "Catálogo",
        "Datos Fuente 2026",
        "Datos Fuente 2025",
        "Indicadores 2026",
        "Indicadores 2025",
        "Diccionario",
        "Semáforos",
    ]


def test_hojas_esperadas_con_anio_unico():
    assert hojas_esperadas({2026: []}) == [
        "Catálogo",
        "Datos Fuente 2026",
        "Indicadores 2026",
        "Diccionario",
        "Semáforos",
    ]


@pytest.fixture
def libro_valido(tmp_path):
    fechas = {fecha_mes(2026, mes) for mes in ANIOS[2026]} | {"202512"}
    tablero = leer_tablero(FIXTURE, fechas)
    filas = {2026: preparar_filas(tablero, UNIVERSO, {}, 2026)}
    ruta = tmp_path / "libro.xlsx"
    escribir_xlsx(UNIVERSO, [], {}, filas, ruta)
    return ruta, filas


def test_encabezados_del_catalogo_son_los_siete_esperados(libro_valido):
    ruta, filas = libro_valido
    wb = load_workbook(ruta)

    assert [wb["Catálogo"].cell(row=FILA_ENC, column=j).value for j in range(1, 8)] == ENC_CATALOGO
    assert validar_libro(ruta, UNIVERSO, filas) is True


def test_encabezado_distinto_del_catalogo_marca_error(libro_valido, capsys):
    ruta, filas = libro_valido
    wb = load_workbook(ruta)
    wb["Catálogo"].cell(row=FILA_ENC, column=4).value = "Federación"
    wb.save(ruta)

    assert validar_libro(ruta, UNIVERSO, filas) is False
    assert "ERROR" in capsys.readouterr().out
