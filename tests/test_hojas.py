"""Pruebas de las columnas nuevas y las notas de liquidez de las hojas."""

from openpyxl import Workbook

from banca_multiple.config import ND, NOTA_ICAP_PDF
from banca_multiple.estilos import ENC_CATALOGO, ENC_DATOS, FMT_PORC, FILA_DATOS
from banca_multiple.hojas.catalogo import escribir_catalogo
from banca_multiple.hojas.datos_fuente import escribir_datos_fuente
from banca_multiple.hojas.indicadores import escribir_indicadores

CAMPOS_NUMERICOS = (
    "activos", "activos_riesgo", "capital_neto", "cartera_total", "cartera_e3",
    "cartera_neta", "estimaciones", "ingresos_int", "gastos_int",
    "margen_ajustado", "gastos_adm", "resultado_neto", "captacion_tradicional",
    "captacion_total", "captacion_prev", "cartera_total_prev", "capital_contable",
    "resultado_12m", "activos_prom_12m", "capital_prom_12m", "margen_fin_12m",
    "activo_prod_prom_12m", "ingresos_operacion", "captacion_prev_anio",
    "cartera_total_prev_anio", "ccl", "cfen", "margen_ajustado_12m",
)


def _fila(**campos):
    fila = {campo: 1.0 for campo in CAMPOS_NUMERICOS}
    fila.update(
        no=1,
        banco="Banco de prueba",
        anio=2026,
        mes="Agosto",
        trimestre="T3",
        ccb=ND,
        ccf=ND,
        categoria=ND,
    )
    fila.update(campos)
    return fila


def _notas(ws):
    return " ".join(
        str(ws.cell(row=fila, column=1).value or "")
        for fila in range(FILA_DATOS + 2, ws.max_row + 1)
    )


UNIVERSO_CATALOGO = [
    {"clave": "040002", "consecutivo": 1, "nombre": "Banco Uno"},
    {"clave": "040009", "consecutivo": 2, "nombre": "Banco Dos"},
]
DATOS_ICAP = {
    "fecha": "202609",
    "bancos": {"040002": {"categoria": "I", "icap": 28.83}},
    "total": {"categoria": "I"},
}


def test_encabezados_nuevos_van_al_final_de_datos_fuente():
    assert len(ENC_DATOS) == 38
    assert ENC_DATOS[35:] == ["CCB\n(%)", "CCF\n(%)", "Categoría"]


def test_escribe_ccb_ccf_y_categoria_del_pdf():
    wb = Workbook()
    escribir_datos_fuente(
        wb, [_fila(ccb=16.93, ccf=16.9318, categoria="I")], 2026, 1
    )
    ws = wb["Datos Fuente 2026"]

    assert ws.cell(row=FILA_DATOS, column=36).value == 0.1693
    assert ws.cell(row=FILA_DATOS, column=36).number_format == FMT_PORC
    assert ws.cell(row=FILA_DATOS, column=37).value == 0.169318
    assert ws.cell(row=FILA_DATOS, column=38).value == "I"
    assert ws.cell(row=FILA_DATOS, column=38).number_format == "@"


def test_escribe_nd_en_meses_sin_pdf():
    wb = Workbook()
    escribir_datos_fuente(wb, [_fila()], 2026, 1)
    ws = wb["Datos Fuente 2026"]

    assert ws.cell(row=FILA_DATOS, column=36).value == ND
    assert ws.cell(row=FILA_DATOS, column=37).value == ND
    assert ws.cell(row=FILA_DATOS, column=38).value == ND


def test_catalogo_tiene_siete_columnas_sin_federacion_ni_nivel():
    assert ENC_CATALOGO == [
        "No.", "Clave CASFIM", "Banco", "Categoría", "Estatus", "Tipo",
        "Fecha de Autorización",
    ]

    wb = Workbook()
    escribir_catalogo(wb, UNIVERSO_CATALOGO, {}, [], datos_icap=DATOS_ICAP)
    ws = wb["Catálogo"]

    assert [ws.cell(row=4, column=j).value for j in range(1, 8)] == ENC_CATALOGO
    assert ws.max_column == 7


def test_catalogo_toma_la_categoria_del_pdf_y_n_d_si_falta():
    wb = Workbook()
    escribir_catalogo(wb, UNIVERSO_CATALOGO, {}, [], datos_icap=DATOS_ICAP)
    ws = wb["Catálogo"]

    assert ws.cell(row=FILA_DATOS, column=4).value == "I"
    assert ws.cell(row=FILA_DATOS + 1, column=4).value == ND
    assert ws.cell(row=FILA_DATOS, column=5).value == ND
    assert ws.cell(row=FILA_DATOS, column=6).value == ND
    assert ws.cell(row=FILA_DATOS, column=7).value == ND


def test_icap_del_pdf_se_escribe_como_numero_en_ratio():
    wb = Workbook()
    escribir_datos_fuente(wb, [_fila(mes="Septiembre", icap_pdf=20.43)], 2026, 1)
    ws = wb["Datos Fuente 2026"]

    celda = ws.cell(row=FILA_DATOS, column=9)
    assert celda.value == 0.2043
    assert celda.number_format == FMT_PORC
    assert celda.data_type == "n"


def test_los_demes_meses_conservan_la_formula_de_icap():
    wb = Workbook()
    escribir_datos_fuente(wb, [_fila()], 2026, 1)
    ws = wb["Datos Fuente 2026"]

    celda = ws.cell(row=FILA_DATOS, column=9)
    assert celda.value == '=IFERROR(H5/G5,"n.d.")'
    assert celda.data_type == "f"


def test_nota_del_icap_del_pdf_en_datos_fuente_e_indicadores():
    wb = Workbook()
    escribir_datos_fuente(wb, [_fila()], 2026, 1)
    escribir_indicadores(wb, [_fila()], 2026)

    assert NOTA_ICAP_PDF in _notas(wb["Datos Fuente 2026"])
    assert NOTA_ICAP_PDF in _notas(wb["Indicadores 2026"])


def test_nota_de_liquidez_en_datos_fuente():
    wb = Workbook()
    escribir_datos_fuente(wb, [_fila()], 2026, 1)
    texto = _notas(wb["Datos Fuente 2026"])

    assert "Cobertura de Liquidez" in texto
    assert "Financiamiento Estable Neto" in texto
    assert "202606" in texto
    assert "n.d. en septiembre de 2026" in texto


def test_nota_de_liquidez_en_indicadores_reemplaza_a_V1():
    wb = Workbook()
    escribir_indicadores(wb, [_fila()], 2026)
    texto = _notas(wb["Indicadores 2026"])

    assert "n.d. en V1" not in texto
    assert "Cobertura de Liquidez" in texto
    assert "Financiamiento Estable Neto" in texto
    assert "202606" in texto
