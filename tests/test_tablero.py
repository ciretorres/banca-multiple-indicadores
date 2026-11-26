"""Pruebas de la lectura del CSV del tablero con el fixture mini."""

import csv
from pathlib import Path

import pytest

from banca_multiple.config import ANIOS
from banca_multiple.tablero import leer_tablero
from banca_multiple.utilidades import fecha_mes

FIXTURE = Path(__file__).parent / "fixtures" / "tablero_mini.csv"
FECHAS = {fecha_mes(2026, mes) for mes in ANIOS[2026]} | {"202512"}


@pytest.fixture
def tablero():
    return leer_tablero(FIXTURE, FECHAS)


def test_contenido_del_tablero(tablero):
    esperadas = {
        ("040002", "202512"), ("040002", "202601"), ("040002", "202602"),
        ("040002", "202603"), ("040002", "202604"), ("040002", "202605"),
        ("040002", "202606"), ("040002", "202607"), ("040002", "202608"),
        ("040009", "202601"),
    }
    assert set(tablero.valores) == esperadas
    assert len(tablero.sector) == 2


def test_descarta_filas_invalidas(tablero):
    with open(FIXTURE, newline="", encoding="utf-8-sig") as f:
        filas_csv = sum(1 for _ in csv.DictReader(f))
    tablero2 = leer_tablero(FIXTURE, FECHAS)
    entradas = sum(len(campos) for campos in tablero2.valores.values()) + len(tablero2.sector)
    assert filas_csv - entradas == 4


def test_fila_del_sector_no_entra_en_valores(tablero):
    assert tablero.sector[("202601", "activos")] == 9000000.0
    assert ("5", "202601") not in tablero.valores
    assert ("000005", "202601") not in tablero.valores


def test_claves_normalizadas(tablero):
    assert all(clave.isdigit() and len(clave) == 6 for clave, _ in tablero.valores)


def test_dato(tablero):
    assert tablero.dato("040002", "202601", "activos") == 1001000.0
    assert tablero.dato("040009", "202602", "activos") is None