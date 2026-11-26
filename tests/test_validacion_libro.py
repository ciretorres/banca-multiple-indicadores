"""Pruebas de las hojas esperadas derivadas de los años de filas."""

from banca_multiple.validacion_libro import hojas_esperadas


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