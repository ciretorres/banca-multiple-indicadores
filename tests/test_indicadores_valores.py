"""Pruebas del cálculo en Python de los 11 indicadores (sin fórmulas)."""

import statistics

import pytest

from banca_multiple.config import ND
from banca_multiple.hojas.indicadores import (
    NOMBRES_INDICADORES,
    calcular_indicadores,
    calcular_mediana_min,
)


def _fila(**cambios):
    fila = {
        "capital_neto": 12.0,
        "activos_riesgo": 200.0,
        "cartera_e3": 10.0,
        "cartera_total": 100.0,
        "estimaciones": -2.0,
        "resultado_12m": 6.0,
        "activos_prom_12m": 300.0,
        "capital_prom_12m": 120.0,
        "margen_ajustado_12m": 15.0,
        "activo_prod_prom_12m": 500.0,
        "captacion_total": 110.0,
        "captacion_prev_anio": 100.0,
        "cartera_total_prev_anio": 80.0,
        "cartera_neta": 90.0,
        "captacion_tradicional": 60.0,
        "gastos_adm": 20.0,
        "ingresos_operacion": 100.0,
        "ccl": 1.45,
    }
    fila.update(cambios)
    return fila


def test_los_11_nombres_siguen_el_orden_del_libro():
    assert list(NOMBRES_INDICADORES) == [
        "ICAP", "IMOR", "ICOR", "ROA", "ROE", "MIN",
        "Crec. captación", "Crec. cartera", "Crédito neto/captación",
        "Índice de eficiencia", "CCL/LCR",
    ]


def test_calcular_indicadores_devuelve_la_arithmetica_de_las_formulas():
    esperado = {
        "ICAP": 0.06,
        "IMOR": 0.10,
        "ICOR": 0.20,
        "ROA": 0.02,
        "ROE": 0.05,
        "MIN": 0.03,
        "Crec. captación": 0.10,
        "Crec. cartera": 0.25,
        "Crédito neto/captación": 1.5,
        "Índice de eficiencia": 0.20,
        "CCL/LCR": 1.45,
    }

    calculado = calcular_indicadores(_fila())

    assert list(calculado) == list(NOMBRES_INDICADORES)
    assert calculado == pytest.approx(esperado)


@pytest.mark.parametrize(
    ("cambios", "indicador"),
    [
        ({"capital_neto": None}, "ICAP"),
        ({"activos_riesgo": 0}, "ICAP"),
        ({"activos_riesgo": "sin dato"}, "ICAP"),
        ({"cartera_total": 0}, "IMOR"),
        ({"estimaciones": None}, "ICOR"),
        ({"activos_prom_12m": 0}, "ROA"),
        ({"capital_prom_12m": None}, "ROE"),
        ({"activo_prod_prom_12m": 0}, "MIN"),
        ({"captacion_prev_anio": None}, "Crec. captación"),
        ({"cartera_total_prev_anio": 0}, "Crec. cartera"),
        ({"captacion_tradicional": None}, "Crédito neto/captación"),
        ({"gastos_adm": None}, "Índice de eficiencia"),
        ({"ccl": None}, "CCL/LCR"),
    ],
)
def test_division_segura_devuelve_nd_si_falta_operando_o_denominador_cero(cambios, indicador):
    assert calcular_indicadores(_fila(**cambios))[indicador] == ND


@pytest.mark.parametrize("ingresos", [0, -5])
def test_eficiencia_con_ingresos_no_positivos_es_na_y_no_nd(ingresos):
    valor = calcular_indicadores(_fila(ingresos_operacion=ingresos))["Índice de eficiencia"]
    assert valor == "n.a."
    assert valor != ND


def test_min_es_el_de_cada_banco_no_una_mediana_repetida():
    primero = calcular_indicadores(_fila())["MIN"]
    segundo = calcular_indicadores(_fila(margen_ajustado_12m=60.0))["MIN"]
    assert primero == pytest.approx(0.03)
    assert segundo == pytest.approx(0.12)
    assert primero != segundo


def test_calcular_indicadores_no_modifica_la_fila():
    fila = _fila()
    original = dict(fila)
    calcular_indicadores(fila)
    assert fila == original


def test_mediana_min_incluye_los_valores_negativos():
    filas = [
        _fila(margen_ajustado_12m=-50.0, activo_prod_prom_12m=1.0)
        for _ in range(30)
    ] + [
        _fila(margen_ajustado_12m=1.0, activo_prod_prom_12m=100.0)
        for _ in range(24)
    ]

    calculada = calcular_mediana_min(filas)

    assert calculada == pytest.approx(statistics.median([-50.0] * 30 + [0.01] * 24))
    assert calculada != pytest.approx(0.01)


def test_mediana_min_ignora_operadores_invalidos_y_sin_datos_devuelve_cero():
    filas = [_fila(margen_ajustado_12m=None), _fila(activo_prod_prom_12m=0)]
    assert calcular_mediana_min(filas) == 0.0
    assert calcular_mediana_min([]) == 0.0
