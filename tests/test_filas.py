"""Pruebas de preparación de filas mensuales usando un tablero de prueba mínimo."""

from pathlib import Path

import pytest

from banca_multiple.config import ANIOS, ND
from banca_multiple.filas import preparar_filas
from banca_multiple.tablero import Tablero, leer_tablero
from banca_multiple.utilidades import fecha_mes

FIXTURE = Path(__file__).parent / "fixtures" / "tablero_mini.csv"
FECHAS = {fecha_mes(2026, mes) for mes in ANIOS[2026]} | {"202512"}

UNIVERSO = [
    {"clave": "040002", "consecutivo": 1, "nombre": "Banco Uno", "federacion": "n.d.", "nivel": "n.d.", "estatus": "En operación", "tipo": "n.d."},
    {"clave": "040009", "consecutivo": 2, "nombre": "Banco Dos", "federacion": "n.d.", "nivel": "n.d.", "estatus": "En operación", "tipo": "n.d."},
]
NOMBRES = {"040002": "Banco Uno Renombrado"}


@pytest.fixture(scope="module")
def filas():
    tablero = leer_tablero(FIXTURE, FECHAS)
    return preparar_filas(tablero, UNIVERSO, NOMBRES, 2026)


def _fila(filas, clave, mes):
    return next(f for f in filas if f["clave"] == clave and f["mes"] == mes)


def test_una_fila_por_sociedad_y_mes(filas):
    assert len(filas) == len(ANIOS[2026]) * len(UNIVERSO)


def test_importes_van_en_millones(filas):
    assert _fila(filas, "040002", "Enero")["activos"] == 1.0
    assert _fila(filas, "040002", "Enero")["gastos_adm"] == 0.02


def test_tiene_datos_falso_en_meses_sin_registros(filas):
    assert _fila(filas, "040009", "Enero")["tiene_datos"] is True
    assert _fila(filas, "040009", "Febrero")["tiene_datos"] is False


def test_nombres_reemplaza_al_del_universo(filas):
    assert _fila(filas, "040002", "Enero")["banco"] == "Banco Uno Renombrado"
    assert _fila(filas, "040009", "Enero")["banco"] == "Banco Dos"


def test_enero_toma_los_totales_de_diciembre(filas):
    enero = _fila(filas, "040002", "Enero")
    assert enero["captacion_prev"] == 0.5
    assert enero["cartera_total_prev"] == 1.0
    assert enero["mes"] == "Enero"
    assert enero["trimestre"] == "T1"


ICAP = {
    "fecha": "202601",
    "bancos": {
        "040002": {
            "ccb": 16.93,
            "ccf": 16.93,
            "icap": 20.42,
            "categoria": "I",
        }
    },
    "total": {"ccb": 18.75, "ccf": 17.22, "icap": 20.77, "categoria": "I"},
}


@pytest.fixture(scope="module")
def filas_con_icap():
    tablero = leer_tablero(FIXTURE, FECHAS)
    return preparar_filas(tablero, UNIVERSO, NOMBRES, 2026, icap=ICAP)


def test_datos_del_pdf_solo_en_el_mes_del_corte(filas_con_icap):
    enero = _fila(filas_con_icap, "040002", "Enero")
    assert enero["ccb"] == 16.93
    assert enero["ccf"] == 16.93
    assert enero["categoria"] == "I"


def test_datos_del_pdf_son_nd_en_otros_meses(filas_con_icap):
    febrero = _fila(filas_con_icap, "040002", "Febrero")
    assert febrero["ccb"] == ND
    assert febrero["ccf"] == ND
    assert febrero["categoria"] == ND


def test_sin_pdf_todos_los_meses_son_nd(filas):
    enero = _fila(filas, "040002", "Enero")
    assert enero["ccb"] == ND
    assert enero["ccf"] == ND
    assert enero["categoria"] == ND


def test_icap_pdf_es_numero_en_puntos_solo_en_el_mes_del_pdf(filas_con_icap):
    enero = _fila(filas_con_icap, "040002", "Enero")
    febrero = _fila(filas_con_icap, "040002", "Febrero")

    assert enero["icap_pdf"] == 20.42
    assert febrero["icap_pdf"] is None


def test_icap_pdf_es_none_si_el_banco_no_esta_en_el_pdf(filas_con_icap):
    assert _fila(filas_con_icap, "040009", "Enero")["icap_pdf"] is None


def test_icap_pdf_es_none_si_el_tablero_ya_publica_ese_mes():
    tablero = Tablero(
        valores={("040002", "202601"): {"icap_pub": 20.4}},
        sector={},
    )
    filas = preparar_filas(tablero, UNIVERSO, NOMBRES, 2026, icap=ICAP)

    assert _fila(filas, "040002", "Enero")["icap_pdf"] is None