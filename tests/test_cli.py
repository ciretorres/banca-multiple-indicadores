"""Pruebas del selector de años parse_anios de la CLI."""

import subprocess
import sys
from argparse import Namespace
from pathlib import Path

import pytest

from banca_multiple.config import ANIOS, PDF_ICAP
from banca_multiple.main import fecha_en_anios, parse_anios, ruta_pdf_icap

RAIZ = Path(__file__).resolve().parent.parent


def test_sin_texto_devuelve_todos_los_anios():
    assert parse_anios(None) == ANIOS


def test_anio_unico():
    assert parse_anios("2026") == {2026: ANIOS[2026]}


def test_rango_de_anios():
    assert parse_anios("2025-2026") == {anio: ANIOS[anio] for anio in (2025, 2026)}


def test_anio_fuera_de_la_config():
    with pytest.raises(SystemExit):
        parse_anios("2027")


def test_formato_invalido():
    with pytest.raises(SystemExit):
        parse_anios("dieciséis")


def test_help_documenta_pdf_icap():
    proc = subprocess.run(
        [sys.executable, str(RAIZ / "generar_banca_multiple.py"), "--help"],
        capture_output=True,
        text=True,
        cwd=RAIZ,
    )
    assert proc.returncode == 0
    assert "--pdf-icap" in proc.stdout


def test_ruta_pdf_icap_por_defecto():
    assert ruta_pdf_icap(Namespace(pdf_icap=None), Path("/entradas")) == (
        Path("/entradas") / PDF_ICAP
    )


def test_pdf_icap_sobrescribe_la_ruta_por_defecto(tmp_path):
    elegida = tmp_path / "ICAP_BM_202609.pdf"
    assert ruta_pdf_icap(Namespace(pdf_icap=elegida), Path("/entradas")) == elegida


def test_fecha_del_pdf_debe_estar_en_los_anios_generados():
    assert fecha_en_anios("202608", {2026: (8,)})
    assert not fecha_en_anios("202608", {2025: tuple(range(1, 13))})