"""Pruebas de coherencia entre Semáforos, formato condicional y FICHAS."""

import re
from types import SimpleNamespace

import pytest
from openpyxl import Workbook

from banca_multiple.config import ANIOS
from banca_multiple.estilos import FILA_DATOS
from banca_multiple.fichas import COND_NA, FICHAS_SEMAFORO, TOTAL_REGLAS
from banca_multiple.hojas.indicadores import aplicar_formato_condicional
from banca_multiple.hojas.semaforos import escribir_semaforos

REF = re.compile(r"[A-Z]+\d+")
PORC = re.compile(r"(\d+(?:\.\d+)?)%")
NUM = re.compile(r"-?\d+(?:\.\d+)?")
ENVOLTURA = re.compile(r"^AND\(ISNUMBER\([A-Z]+\d+\),(.*)\)$")

PREFIJO_NOTA = "Excel (fracción): "


@pytest.fixture(scope="module")
def libro():
    wb = Workbook()
    escribir_semaforos(wb, sorted(ANIOS, reverse=True))
    ws = wb["Semáforos"]

    umbrales = []
    conds = []

    for fila in ws.iter_rows(min_col=1, max_col=4):
        valor = fila[0].value
        if valor == "Umbral":
            umbrales.append([celda.value for celda in fila[1:]])
        elif isinstance(valor, str) and valor.startswith(PREFIJO_NOTA):
            conds.append(valor[len(PREFIJO_NOTA):])

    ws_ind = wb.create_sheet("Indicadores")
    aplicar_formato_condicional(ws_ind, nfilas=10)
    formulas = [
        regla.formula[0]
        for cf in ws_ind.conditional_formatting
        for regla in cf.rules
    ]

    return SimpleNamespace(ws=ws, umbrales=umbrales, conds=conds, formulas=formulas)


def _sin_refs(texto):
    return REF.sub("", texto)


def _porcentajes(texto):
    return {float(x) / 100 for x in PORC.findall(_sin_refs(texto))}


def _numeros(texto):
    return {float(x) for x in NUM.findall(_sin_refs(texto))}


def _desenvuelve(formula):
    return ENVOLTURA.sub(r"\1", formula)


def _etiquetas(umbral):
    return [etiqueta for celda in umbral if celda and celda != "—" for etiqueta in celda.split(" · ")]


def _pares(nota):
    return [tuple(par.split(" → ", 1)) for par in nota.split(" · ")]


def _nota_prosa(ws, prefijo):
    for fila in ws.iter_rows(min_col=1, max_col=1):
        valor = fila[0].value
        if isinstance(valor, str) and valor.startswith(prefijo):
            return valor
    raise AssertionError(f"No hay nota que empiece con {prefijo!r}")


def test_la_hoja_tiene_un_bloque_por_ficha(libro):
    assert len(libro.umbrales) == len(FICHAS_SEMAFORO)
    assert len(libro.conds) == len(FICHAS_SEMAFORO)


def test_etiquetas_conciden_con_condiciones_y_con_formato_condicional(libro):
    inicio = 0
    for ficha, umbral, nota in zip(FICHAS_SEMAFORO, libro.umbrales, libro.conds):
        fin = inicio + len(ficha.tramos)
        bloque = libro.formulas[inicio:fin]
        inicio = fin

        etiquetas = _etiquetas(umbral)
        assert set(etiquetas) == {texto for texto, _, _ in ficha.tramos}

        numeros_nota = set()
        for _, condicion in _pares(nota):
            numeros_nota |= _numeros(condicion)

        numeros_cf = set()
        for formula in bloque:
            numeros_cf |= _numeros(formula)

        assert _porcentajes(" · ".join(etiquetas)) == numeros_nota
        assert numeros_nota == numeros_cf


def test_condiciones_de_la_nota_son_verbatim_a_las_formulas_cf(libro):
    inicio = 0
    for ficha, nota in zip(FICHAS_SEMAFORO, libro.conds):
        fin = inicio + len(ficha.tramos)
        condiciones_nota = [condicion for _, condicion in _pares(nota)]
        condiciones_cf = [_desenvuelve(formula) for formula in libro.formulas[inicio:fin]]
        inicio = fin
        assert condiciones_nota == condiciones_cf


def test_numero_de_reglas_cf_es_total_reglas(libro):
    assert TOTAL_REGLAS == 34
    assert len(libro.formulas) == TOTAL_REGLAS


def test_tramo_na_no_tiene_numeros(libro):
    idx = [f.indicador for f in FICHAS_SEMAFORO].index("Índice de Eficiencia")
    ficha = FICHAS_SEMAFORO[idx]
    etiqueta, condicion = _pares(libro.conds[idx])[-1]

    assert "n.a." in etiqueta
    assert condicion == COND_NA.format(c=ficha.columna + str(FILA_DATOS))
    assert _numeros(condicion) == set()


def test_notas_en_prosa_coinciden_con_los_tramos(libro):
    pass


def test_limite_superior_amarillo_de_seis_indicadores(libro):
    pass


def test_resultado_neto_no_tiene_semaforo(libro):
    pass