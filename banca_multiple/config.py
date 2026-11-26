"""Configuración de rutas, periodos y campos usados por el proyecto."""

from __future__ import annotations

from pathlib import Path


# Rutas principales del repositorio y archivos de entrada y salida.
AQUI = Path(__file__).resolve().parent.parent
DIR_ENTRADAS = AQUI / "entradas"
DIR_SALIDAS = AQUI / "salidas"
SALIDA_DEFECTO = DIR_SALIDAS / "Bancos_Multiples_Indicadores_Datos.xlsx"
SALIDA_VISTA_COPILOT = DIR_SALIDAS / "Bancos_Multiples_Cortes_Trimestrales.xlsx"

# Archivos que se leen durante la generación y validación del libro.
BE_UNIVERSO = "BE BM 202609.xlsx"
PDF_ICAP = "ICAP_BM_202608.pdf"
CSV_TABLERO = Path("tablero") / "sh_datos_csv_40_i" / "040_TO.csv"
CATALOGO_CONCEPTOS = Path("tablero") / "sh_datos_csv_40_i" / "catalogo_conceptos_040.xlsx"
CATALOGO_INSTITUCIONES = Path("tablero") / "sh_datos_csv_40_i" / "catalogo_instituciones_040.csv"

# Hojas del boletín electrónico que se leen.
HOJA_UNIVERSO = "Evaluación Calidad Detallada"
HOJA_INDICADORES_BE = "Indicadores"

# Parámetros para interpretar los datos del tablero.
TIPO_SALDO = "Consolidado con SOFOMER"
CLAVE_SECTOR = "5"
GRUPOS = ["59", "60", "61", "62", "63", "64"]
MILES = 1_000_000.0

# Relación entre el número del mes y su nombre, y su inversa.
MESES = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre",
}
MES_NUM = {nombre: numero for numero, nombre in MESES.items()}

# Años y meses que se incluirán en el libro.
ANIOS = {
    2025: tuple(range(1, 13)),
    2026: tuple(range(1, 10)),
}

# Cortes de cierre trimestral (mar/jun/sep/dic) derivados de ANIOS: (hoja, año, trimestre, mes).
CORTES_TRIMESTRALES = tuple(
    (f"{anio} Q{mes // 3}", anio, mes // 3, mes)
    for anio, meses in ANIOS.items()
    for mes in meses
    if mes in (3, 6, 9, 12)
)

# Relaciona las claves CNBV del tablero con los nombres internos de los campos.
CONCEPTOS = {
    "4030211": "capital_neto",
    "4030249": "activos_riesgo",
    "4021750": "icap_pub",
    "4021754": "ccb_pub",
    "4021755": "ccf_pub",
    "40100001": "activos",
    "40200004": "activos_prom_12m",
    "40100002": "capital_contable",
    "40200005": "capital_prom_12m",
    "40100185": "cartera_total",
    "40100341": "cartera_e3",
    "40100551": "cartera_neta",
    "40100031": "estimaciones",
    "40100013": "resultado_neto",
    "40200015": "resultado_12m",
    "40100008": "margen_fin",
    "40100009": "margen_ajustado",
    "40200010": "margen_fin_12m",
    "40200011": "margen_ajustado_12m",
    "40100006": "ingresos_int",
    "40100007": "gastos_int",
    "40100011": "gastos_adm",
    "40100170": "ingresos_operacion",
    "40100085": "captacion_tradicional",
    "40100042": "captacion_total",
    "40200240": "activo_prod_prom_12m",
    "40200017": "imor_pub",
    "40200096": "icor_pub",
    "40200001": "roa_pub",
    "40200002": "roe_pub",
    "4040001": "min_pub",
    "601": "ccl",
    "610": "cfen",
}

# Campos para los que se calculan o leen los totales del sector.
CAMPOS_SECTOR = [
    "capital_neto",
    "activos_riesgo",
    "activos",
    "cartera_total",
    "cartera_e3",
    "cartera_neta",
    "estimaciones",
    "resultado_neto",
    "margen_ajustado",
    "ingresos_int",
    "gastos_int",
    "gastos_adm",
    "ingresos_operacion",
    "captacion_tradicional",
    "captacion_total",
]

# Texto que se muestra cuando un dato no está disponible.
ND = "n.d."

# Notas de liquidez, compartidas por Datos Fuente, Indicadores y README.
NOTA_LIQUIDEZ = [
    "CCL/LCR = Cobertura de Liquidez = Activos líquidos de alta calidad / "
    "Salidas netas de efectivo a 30 días.",
    "CFEN/NSFR = Financiamiento Estable Neto = Financiación estable disponible / "
    "Financiación estable requerida a 1 año.",
    "CCL y CFEN se publican solo en cierres trimestrales (mar/jun/sep/dic), "
    "con desfase de un trimestre; último dato 202606 → n.d. en septiembre de 2026.",
]