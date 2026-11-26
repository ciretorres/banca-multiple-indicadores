"""Pruebas de tolerancia de diferencias en la validación de datos."""

from banca_multiple.tablero import Tablero
from banca_multiple.validacion_datos import _tolera_dif, validar_datos


def _fila(clave="040002", anio=2026, mes="Enero", **campos):
    base = {"clave": clave, "anio": anio, "mes": mes}
    base.update(campos)
    return base


def _tablero(valores):
    return Tablero(valores=valores, sector={})


def test_dif_grande_con_publicado_enorme_tolerada():
    assert _tolera_dif(125.75, 16_772_979.0)


def test_dif_pequena_con_publicado_pequeno_falla():
    assert not _tolera_dif(0.03, 1.0)


def test_dif_dentro_de_la_tolerancia_absoluta():
    assert _tolera_dif(0.015, 1.0)


def test_validar_datos_basico():
    valores = {
        ("040002", "202601"): {
            "resultado_12m": 100.0,
            "activos_prom_12m": 100.0,
        }
    }
    tablero = _tablero(valores)
    filas = {2026: [_fila(roa_pub=100.0)]}
    universo = [{"clave": "040002", "consecutivo": 1, "nombre": "Banco"}]
    # ROA calculado 100 vs publicado 100 -> OK
    assert validar_datos(tablero, filas, universo, {}) is True


def test_min_publicado_no_ajustado_valida():
    valores = {
        ("040002", "202601"): {
            "margen_fin_12m": 100.0,
            "activo_prod_prom_12m": 1000.0,
        }
    }
    tablero = _tablero(valores)
    filas = {2026: [_fila(min_pub=10.0)]}
    universo = [{"clave": "040002", "consecutivo": 1, "nombre": "Banco"}]
    assert validar_datos(tablero, filas, universo, {}) is True


ICAP = {
    "fecha": "202608",
    "bancos": {
        "040002": {
            "icap": 20.42,
            "ccb": 16.93,
            "ccf": 16.93,
            "categoria": "I",
        }
    },
    "total": {"icap": 20.77, "ccb": 18.75, "ccf": 17.22, "categoria": "I"},
}


def _tablero_con_icap(icap_total=20.768):
    return Tablero(
        valores={
            ("040002", "202608"): {
                "icap_pub": 20.4192,
                "ccb_pub": 16.9318,
                "ccf_pub": 16.9318,
            }
        },
        sector={
            ("202608", "icap_pub"): icap_total,
            ("202608", "ccb_pub"): 18.7453,
            ("202608", "ccf_pub"): 17.223,
        },
    )


UNIVERSO_ICAP = [{"clave": "040002", "consecutivo": 1, "nombre": "Banco"}]
FILAS_ICAP = {2026: [_fila(mes="Agosto")]}


def test_pdf_vs_tablero_dentro_de_tolerancia(capsys):
    ok = validar_datos(
        _tablero_con_icap(), FILAS_ICAP, UNIVERSO_ICAP, {}, icap=ICAP
    )

    assert ok is True
    assert "ICAP / CCB / CCF del PDF vs tablero (202608)" in capsys.readouterr().out


def test_pdf_vs_tablero_fuera_de_tolerancia(capsys):
    ok = validar_datos(
        _tablero_con_icap(icap_total=21.0),
        FILAS_ICAP,
        UNIVERSO_ICAP,
        {},
        icap=ICAP,
    )

    assert ok is False
    assert "DIF" in capsys.readouterr().out


def test_sin_pdf_no_se_agrega_la_seccion(capsys):
    assert validar_datos(_tablero_con_icap(), FILAS_ICAP, UNIVERSO_ICAP, {}) is True
    assert "PDF vs tablero" not in capsys.readouterr().out
