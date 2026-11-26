"""Definiciones de indicadores y rangos para los semáforos del libro."""

from __future__ import annotations

from dataclasses import dataclass

from .estilos import (
    AMARILLO_FILL,
    AMARILLO_FONT,
    ROJO_FILL,
    ROJO_FONT,
    VERDE_FILL,
    VERDE_FONT,
)


COLORES = {
    "verde": (VERDE_FILL, VERDE_FONT),
    "amarillo": (AMARILLO_FILL, AMARILLO_FONT),
    "rojo": (ROJO_FILL, ROJO_FONT),
}


@dataclass(frozen=True)
class Ficha:
    indicador: str
    columna: str
    formula: str
    grupo: str
    descripcion: str
    tramos: tuple[tuple[str, str, str], ...] = ()


COND_NA = '{c}="n.a."'


FICHAS: list[Ficha] = [
    Ficha(
        indicador="ICAP",
        columna="F",
        formula="Capital Neto / Activos sujetos a riesgo",
        grupo="Solvencia",
        descripcion="Capital neto entre activos sujetos a riesgo.",
        tramos=(
            ("≥ 12%", "{c}>=0.12", "verde"),
            ("10% – < 12%", "AND({c}>=0.1,{c}<0.12)", "amarillo"),
            ("< 10%", "{c}<0.1", "rojo"),
        ),
    ),
    Ficha(
        indicador="IMOR",
        columna="G",
        formula="Cartera etapa 3 / Cartera Total",
        grupo="Calidad del activo",
        descripcion="Proporción de cartera vencida.",
        tramos=(
            ("≤ 3%", "{c}<=0.03", "verde"),
            ("> 3% – 5%", "AND({c}>0.03,{c}<=0.05)", "amarillo"),
            ("> 5%", "{c}>0.05", "rojo"),
        ),
    ),
    Ficha(
        indicador="ICOR",
        columna="H",
        formula="ABS(Estimaciones) / Cartera etapa 3",
        grupo="Cobertura",
        descripcion="Cobertura de estimaciones sobre cartera vencida.",
        tramos=(
            ("≥ 100%", "{c}>=1", "verde"),
            ("80% – < 100%", "AND({c}>=0.8,{c}<1)", "amarillo"),
            ("< 80%", "{c}<0.8", "rojo"),
        ),
    ),
    Ficha(
        indicador="ROA",
        columna="I",
        formula="Resultado Neto 12M / Activos promedio 12M",
        grupo="Rentabilidad",
        descripcion="Rendimiento del activo.",
        tramos=(
            ("≥ 1%", "{c}>=0.01", "verde"),
            ("> 0% – < 1%", "AND({c}>0,{c}<0.01)", "amarillo"),
            ("≤ 0%", "{c}<=0", "rojo"),
        ),
    ),
    Ficha(
        indicador="ROE",
        columna="J",
        formula="Resultado Neto 12M / Capital contable promedio 12M",
        grupo="Rentabilidad",
        descripcion="Rendimiento del patrimonio.",
        tramos=(
            ("≥ 15%", "{c}>=0.15", "verde"),
            ("> 0% – < 15%", "AND({c}>0,{c}<0.15)", "amarillo"),
            ("≤ 0%", "{c}<=0", "rojo"),
        ),
    ),
    Ficha(
        indicador="MIN",
        columna="K",
        formula="Margen Financiero Ajustado 12M / Activo productivo promedio 12M",
        grupo="Rentabilidad",
        descripcion="Margen de interés neto frente a la mediana de los 54 bancos.",
        tramos=(
            ("≥ 100% de la mediana", "{c}>=$Q5*1", "verde"),
            ("80% – < 100% de la mediana", "AND({c}>=$Q5*0.8,{c}<$Q5*1)", "amarillo"),
            ("< 80% de la mediana", "{c}<$Q5*0.8", "rojo"),
        ),
    ),
    Ficha(
        indicador="Crecimiento de Captación",
        columna="L",
        formula="(Captación Total / Captación Total mismo mes año anterior) − 1",
        grupo="Crecimiento",
        descripcion="Variación anual de la captación total.",
        tramos=(
            ("> 0%", "{c}>0", "verde"),
            ("= 0%", "{c}=0", "amarillo"),
            ("< 0%", "{c}<0", "rojo"),
        ),
    ),
    Ficha(
        indicador="Crecimiento de Cartera",
        columna="M",
        formula="(Cartera Total / Cartera Total mismo mes año anterior) − 1",
        grupo="Crecimiento",
        descripcion="Variación anual de la cartera total.",
        tramos=(
            ("> 0%", "{c}>0", "verde"),
            ("= 0%", "{c}=0", "amarillo"),
            ("< 0%", "{c}<0", "rojo"),
        ),
    ),
    Ficha(
        indicador="Crédito Neto / Captación",
        columna="N",
        formula="Cartera Neta / Captación Tradicional",
        grupo="Estructura",
        descripcion="Peso de la cartera neta sobre la captación tradicional.",
        tramos=(
            ("70% – 90%", "AND({c}>=0.7,{c}<=0.9)", "verde"),
            ("60% – < 70% o > 90% – 100%", "OR(AND({c}>=0.6,{c}<0.7),AND({c}>0.9,{c}<=1))", "amarillo"),
            ("< 60% o > 100%", "OR({c}<0.6,{c}>1)", "rojo"),
        ),
    ),
    Ficha(
        indicador="Índice de Eficiencia",
        columna="O",
        formula="Gastos de administración y promoción / Ingresos totales de la operación",
        grupo="Eficiencia",
        descripcion="Costo operativo por peso de ingresos de operación.",
        tramos=(
            ("≤ 55%", "{c}<=0.55", "verde"),
            ("> 55% – 70%", "AND({c}>0.55,{c}<=0.7)", "amarillo"),
            ("> 70%", "{c}>0.7", "rojo"),
            ("Ingresos ≤ 0 (n.a.)", COND_NA, "rojo"),
        ),
    ),
    Ficha(
        indicador="CCL/LCR",
        columna="P",
        formula="Activos líquidos de alta calidad / Salidas netas a 30 días",
        grupo="Liquidez",
        descripcion="Coeficiente de cobertura de liquidez (n.d. en V1).",
        tramos=(
            ("≥ 120%", "{c}>=1.2", "verde"),
            ("100% – < 120%", "AND({c}>=1,{c}<1.2)", "amarillo"),
            ("< 100%", "{c}<1", "rojo"),
        ),
    ),
]

FICHAS_SEMAFORO = [f for f in FICHAS if f.tramos]
TOTAL_REGLAS = sum(len(f.tramos) for f in FICHAS_SEMAFORO)