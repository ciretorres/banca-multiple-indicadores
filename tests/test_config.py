"""Pruebas de la configuración: conceptos y años."""

from banca_multiple.config import (
    ANIOS,
    CONCEPTOS,
    CORTES_TRIMESTRALES,
    DIR_SALIDAS,
    PDF_ICAP,
    SALIDA_DEFECTO,
    SALIDA_VISTA_COPILOT,
)


def test_conceptos_claves_sin_duplicadas():
    assert len(CONCEPTOS) == len(set(CONCEPTOS))


def test_conceptos_tiene_claves_solo_digitos():
    assert all(clave.isdigit() for clave in CONCEPTOS)


def test_conceptos_valores_unicos():
    valores = list(CONCEPTOS.values())
    assert len(valores) == len(set(valores))


def test_pdf_icap_es_el_nombre_del_archivo_de_agosto():
    assert PDF_ICAP == "ICAP_BM_202608.pdf"


def test_conceptos_incluye_ccb_y_ccf_publicados():
    assert CONCEPTOS["4021754"] == "ccb_pub"
    assert CONCEPTOS["4021755"] == "ccf_pub"


def test_anios_son_enteros_con_meses_ordenados():
    for anio, meses in ANIOS.items():
        assert isinstance(anio, int)
        assert list(meses) == sorted(set(meses))
        assert all(1 <= mes <= 12 for mes in meses)


def test_salida_vista_copilot_es_un_archivo_nuevo_en_salidas():
    assert SALIDA_VISTA_COPILOT == (
        DIR_SALIDAS / "Bancos_Multiples_Cortes_Trimestrales.xlsx"
    )
    assert SALIDA_VISTA_COPILOT != SALIDA_DEFECTO


def test_cortes_trimestrales_son_siete_y_estan_ordenados():
    assert [corte[0] for corte in CORTES_TRIMESTRALES] == [
        "2025 Q1", "2025 Q2", "2025 Q3", "2025 Q4",
        "2026 Q1", "2026 Q2", "2026 Q3",
    ]


def test_cortes_trimestrales_cierran_en_mar_jun_sep_dic():
    assert list(CORTES_TRIMESTRALES) == [
        ("2025 Q1", 2025, 1, 3),
        ("2025 Q2", 2025, 2, 6),
        ("2025 Q3", 2025, 3, 9),
        ("2025 Q4", 2025, 4, 12),
        ("2026 Q1", 2026, 1, 3),
        ("2026 Q2", 2026, 2, 6),
        ("2026 Q3", 2026, 3, 9),
    ]
    assert all(mes in (3, 6, 9, 12) for _, _, _, mes in CORTES_TRIMESTRALES)


def test_cortes_derivan_de_los_meses_de_anios():
    for _, anio, _, mes in CORTES_TRIMESTRALES:
        assert mes in ANIOS[anio]
