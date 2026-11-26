"""Pruebas del lector del PDF de ICAP con texto sintético."""

from pathlib import Path

import pytest

from banca_multiple.be import leer_universo
from banca_multiple.config import BE_UNIVERSO, DIR_ENTRADAS, PDF_ICAP
from banca_multiple.pdf_icap import _fecha_del_nombre, _parse, leer_icap

NOMBRES = {
    "040165": "Banco Bineo",
    "040012": "BBVA México",
}

ENCABEZADO = """Institución CCB 2/
%
CCF 3/
%
ICAP 4/
%
Categoría 5/
"""

FILAS = """B a n c o   B i n e o 268.07 268.07 268.07 I
BBVA México 16.93 16.93 20.42 I
Total Banca Múltiple 18.75 17.22 20.77 I
"""


def test_fecha_derivada_del_nombre_del_archivo():
    assert _fecha_del_nombre(Path("entradas/ICAP_BM_202608.pdf")) == "202608"


def test_nombre_sin_formato_de_fecha_falla():
    with pytest.raises(SystemExit, match="ICAP_BM_YYYYMM.pdf"):
        _fecha_del_nombre(Path("entradas/icap.pdf"))


def test_extrae_campos_de_bancos_y_total():
    resultado = _parse(
        ENCABEZADO + FILAS, "202608", NOMBRES, "ICAP_BM_202608.pdf", n_bancos=2
    )

    assert resultado["fecha"] == "202608"
    assert set(resultado["bancos"]) == set(NOMBRES)
    assert resultado["bancos"]["040165"] == {
        "ccb": 268.07,
        "ccf": 268.07,
        "icap": 268.07,
        "categoria": "I",
    }
    assert resultado["bancos"]["040012"] == {
        "ccb": 16.93,
        "ccf": 16.93,
        "icap": 20.42,
        "categoria": "I",
    }
    assert resultado["total"] == {
        "ccb": 18.75,
        "ccf": 17.22,
        "icap": 20.77,
        "categoria": "I",
    }


def test_respeta_el_orden_de_las_columnas_del_encabezado():
    texto = """Institución ICAP 4/
%
CCF 3/
%
CCB 2/
%
Categoría 5/
BBVA México 20.42 16.93 16.93 I
Total Banca Múltiple 20.77 17.22 18.75 I
"""

    resultado = _parse(texto, "202608", NOMBRES, "ICAP_BM_202608.pdf", n_bancos=1)

    assert resultado["bancos"]["040012"]["icap"] == 20.42
    assert resultado["bancos"]["040012"]["ccb"] == 16.93
    assert resultado["total"]["ccb"] == 18.75


def test_falta_una_columna_del_encabezado_falla():
    texto = ENCABEZADO.replace("CCF 3/", "Otro 3/")
    with pytest.raises(SystemExit, match="CCF"):
        _parse(texto + FILAS, "202608", NOMBRES, "ICAP_BM_202608.pdf")


def test_falta_el_renglon_total_falla():
    texto = ENCABEZADO + FILAS.replace("Total Banca Múltiple 18.75 17.22 20.77 I\n", "")
    with pytest.raises(SystemExit, match="Total"):
        _parse(texto, "202608", NOMBRES, "ICAP_BM_202608.pdf")


def test_sin_filas_de_bancos_falla():
    with pytest.raises(SystemExit, match="filas"):
        _parse(ENCABEZADO, "202608", NOMBRES, "ICAP_BM_202608.pdf")


def test_nombre_del_pdf_no_reconocido_falla_con_el_nombre():
    texto = ENCABEZADO + "Banco Fantasma 10.00 10.00 10.00 I\n" + FILAS.splitlines()[-1]
    with pytest.raises(SystemExit, match="Banco Fantasma"):
        _parse(texto, "202608", NOMBRES, "ICAP_BM_202608.pdf")


def test_numero_de_bancos_distinto_de_54_falla():
    with pytest.raises(SystemExit, match="54 bancos"):
        _parse(ENCABEZADO + FILAS, "202608", NOMBRES, "ICAP_BM_202608.pdf")


def test_pdf_real_extrae_54_bancos_y_total():
    ruta_pdf = DIR_ENTRADAS / PDF_ICAP
    ruta_be = DIR_ENTRADAS / BE_UNIVERSO
    if not (ruta_pdf.is_file() and ruta_be.is_file()):
        pytest.skip("Se necesitan el PDF de ICAP y el BE en entradas/")
    nombres = {reg["clave"]: reg["nombre"] for reg in leer_universo(ruta_be)}

    resultado = leer_icap(ruta_pdf, nombres)

    assert resultado["fecha"] == "202609"
    assert len(resultado["bancos"]) == 54
    assert set(resultado["bancos"]) == set(nombres)
    assert resultado["total"]["icap"] == 20.43
    assert resultado["bancos"]["040138"]["icap"] == 28.83  # Ualá
    assert resultado["bancos"]["040012"]["icap"] == 19.52  # BBVA
    assert resultado["bancos"]["040014"]["icap"] == 19.13  # Santander
    assert resultado["total"]["categoria"] == "I"
