"""Pruebas del libro compañero de cortes trimestrales para Copilot."""

import statistics
import subprocess
import sys
from pathlib import Path

import pytest
from openpyxl import load_workbook

from banca_multiple.config import ANIOS, CORTES_TRIMESTRALES, MESES, ND, NOTA_ICAP_PDF
from banca_multiple.hojas.indicadores import (
    NOMBRES_INDICADORES,
    calcular_indicadores,
    calcular_mediana_min,
)

RAIZ = Path(__file__).resolve().parent.parent
ENC_ESPERADO = [
    "No.", "Banco", "Mes de corte", "Trimestre", *NOMBRES_INDICADORES,
]
CORTES = [nombre for nombre, _, _, _ in CORTES_TRIMESTRALES]


def _filas_sinteticas():
    filas = {}
    for anio, meses in ANIOS.items():
        registros = []
        for mes in meses:
            for n in range(1, 55):
                negativo = anio == 2025 and mes == 3 and n <= 30
                registros.append(
                    {
                        "no": n,
                        "banco": f"Banco {n:02d}",
                        "anio": anio,
                        "mes": MESES[mes],
                        "trimestre": f"T{(mes - 1) // 3 + 1}",
                        "capital_neto": 12.0,
                        "activos_riesgo": 200.0,
                        "cartera_e3": 10.0,
                        "cartera_total": 100.0,
                        "estimaciones": -2.0,
                        "resultado_12m": 6.0,
                        "activos_prom_12m": 300.0,
                        "capital_prom_12m": 120.0,
                        "margen_ajustado_12m": -50.0 if negativo else 15.0 + n,
                        "activo_prod_prom_12m": 1.0 if negativo else 500.0,
                        "captacion_total": 110.0,
                        "captacion_prev_anio": 100.0,
                        "cartera_total_prev_anio": 80.0,
                        "cartera_neta": 90.0,
                        "captacion_tradicional": 60.0,
                        "gastos_adm": 20.0,
                        "ingresos_operacion": -5.0 if anio == 2026 and mes == 9 and n == 2 else 100.0,
                        "ccl": 1.45,
                    }
                )
                if anio == 2026 and mes == 9:
                    registros[-1]["icap_pdf"] = 20.43
        filas[anio] = registros
    return filas


@pytest.fixture
def libro(tmp_path):
    from banca_multiple.vista_copilot import escribir_vista_copilot

    ruta = tmp_path / "vista.xlsx"
    escribir_vista_copilot(_filas_sinteticas(), ruta)
    return load_workbook(ruta)


def test_el_libro_tiene_los_siete_cortes_y_leyenda_al_final(libro):
    assert libro.sheetnames == [*CORTES, "Leyenda"]


@pytest.mark.parametrize("nombre", CORTES)
def test_cada_corte_tiene_54_filas_y_15_columnas(libro, nombre):
    ws = libro[nombre]
    assert ws.max_row == 58
    assert ws.max_column == 15
    assert [ws.cell(row=4, column=j).value for j in range(1, 16)] == ENC_ESPERADO


def test_las_columnas_base_identifican_el_corte(libro):
    ws = libro["2025 Q1"]
    assert ws["A5"].value == 1
    assert ws["B5"].value == "Banco 01"
    assert ws["C5"].value == "Marzo"
    assert ws["D5"].value == "T1"


def test_los_indicadores_son_valores_sin_formulas_ni_celdas_vacias(libro):
    for nombre in CORTES:
        ws = libro[nombre]
        for fila in ws.iter_rows(min_row=5, max_row=58, min_col=5, max_col=15):
            for celda in fila:
                assert celda.data_type != "f"
                assert celda.value is not None
                assert isinstance(celda.value, (int, float)) or celda.value in (ND, "n.a.")


def test_valores_de_indicadores_coinciden_con_el_calculo_en_python(libro):
    fila = next(
        f for f in _filas_sinteticas()[2025]
        if f["mes"] == "Marzo" and f["no"] == 1
    )
    esperado = calcular_indicadores(fila)
    ws = libro["2025 Q1"]
    assert ws["E5"].value == pytest.approx(esperado["ICAP"])
    assert ws["J5"].value == pytest.approx(esperado["MIN"])
    assert ws["O5"].value == pytest.approx(esperado["CCL/LCR"])


def test_min_es_distinto_por_banco(libro):
    ws = libro["2025 Q1"]
    valores = [ws.cell(row=r, column=10).value for r in (35, 36, 37)]
    assert len(set(valores)) == 3


def test_2026_q3_usa_el_icap_del_pdf_y_mantiene_ccl_en_nd(libro):
    ws = libro["2026 Q3"]
    for fila in ws.iter_rows(min_row=5, max_row=58, min_col=5, max_col=15):
        assert fila[0].value == pytest.approx(0.2043)
        assert fila[10].value == ND
    assert isinstance(libro["2026 Q2"]["E5"].value, (int, float))
    assert isinstance(libro["2026 Q2"]["O5"].value, (int, float))


def test_2026_q3_no_fuerza_nd_si_no_hay_icap_del_pdf(tmp_path):
    from banca_multiple.vista_copilot import escribir_vista_copilot

    filas = _filas_sinteticas()
    for fila in filas[2026]:
        fila.pop("icap_pdf", None)
    ruta = tmp_path / "vista_sin_pdf.xlsx"
    escribir_vista_copilot(filas, ruta)
    libro = load_workbook(ruta)

    assert libro["2026 Q3"]["E5"].value == pytest.approx(12.0 / 200.0)
    assert libro["2026 Q3"]["O5"].value == ND


def test_leyenda_documenta_la_fuente_alternativa_del_icap(libro):
    texto = " ".join(
        str(celda.value)
        for fila in libro["Leyenda"].iter_rows()
        for celda in fila
        if celda.value is not None
    )

    assert NOTA_ICAP_PDF in texto


def test_eficiencia_con_ingresos_no_positivos_se_escribe_na(libro):
    ws = libro["2026 Q3"]
    assert ws["N6"].value == "n.a."
    assert ws["N6"].value != ND


def test_leyenda_explica_siglas_desfase_nd_y_min(libro):
    texto = " ".join(
        str(celda.value)
        for fila in libro["Leyenda"].iter_rows()
        for celda in fila
        if celda.value is not None
    )
    for esperado in (
        "CCL/LCR = Cobertura de Liquidez",
        "CFEN/NSFR = Financiamiento Estable Neto",
        "202606",
        "septiembre de 2026",
        "n.d.",
        "MIN",
        "mediana",
        "negativos",
    ):
        assert esperado in texto


def test_leyenda_registra_la_mediana_de_los_54_con_negativos(libro):
    ws = libro["Leyenda"]
    mediana = {
        ws.cell(row=r, column=1).value: ws.cell(row=r, column=3).value
        for r in range(1, ws.max_row + 1)
        if ws.cell(row=r, column=1).value in CORTES
    }
    assert set(mediana) == set(CORTES)

    mar = [
        f for f in _filas_sinteticas()[2025] if f["mes"] == "Marzo"
    ]
    esperada = calcular_mediana_min(mar)
    negatives = [-50.0] * 30
    positivas = [(15 + n) / 500 for n in range(31, 55)]
    assert esperada == pytest.approx(statistics.median(negatives + positivas))
    assert mediana["2025 Q1"] == pytest.approx(esperada)


def test_el_help_documenta_la_opcion_out():
    proc = subprocess.run(
        [sys.executable, str(RAIZ / "generar_vista_copilot.py"), "--help"],
        capture_output=True,
        text=True,
        cwd=RAIZ,
    )
    assert proc.returncode == 0
    assert "--out" in proc.stdout


def test_out_respeta_la_ruta_dada(tmp_path):
    destino = tmp_path / "vista_elegida.xlsx"
    proc = subprocess.run(
        [
            sys.executable,
            str(RAIZ / "generar_vista_copilot.py"),
            "--out",
            str(destino),
        ],
        capture_output=True,
        text=True,
        cwd=RAIZ,
    )
    assert proc.returncode == 0, proc.stderr
    assert destino.exists()
    libro = load_workbook(destino)
    assert libro.sheetnames == [*CORTES, "Leyenda"]
    assert all(libro[n].max_row == 58 for n in CORTES)
