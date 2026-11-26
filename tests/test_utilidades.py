"""Pruebas de las utilidades de fechas y conversión."""

from banca_multiple.utilidades import a_millones, enumerar, fecha_anterior, fecha_mes


def test_fecha_mes_concatena_anio_y_mes():
    assert fecha_mes(2026, 1) == "202601"
    assert fecha_mes(2026, 12) == "202612"


def test_fecha_anterior_cruza_el_anio():
    assert fecha_anterior("202601") == "202512"
    assert fecha_anterior("202608") == "202607"


def test_a_millones_convierte_pesos_a_millones():
    assert a_millones(1_000_000) == 1.0
    assert a_millones(None) is None


def test_enumerar_con_un_elemento_devuelve_el_valor():
    assert enumerar(["Indicadores 2026"]) == "Indicadores 2026"


def test_enumerar_con_dos_elementos_usa_e_verbatim():
    assert enumerar(["Indicadores 2026", "Indicadores 2025"]) == "Indicadores 2026 e Indicadores 2025"


def test_enumerar_con_tres_elementos_separa_con_comas_y_e():
    assert enumerar(["A", "B", "C"]) == "A, B e C"


def test_enumerar_con_lista_vacia_devuelve_vacio():
    assert enumerar([]) == ""