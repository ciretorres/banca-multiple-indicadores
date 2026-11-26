"""Preparación de las filas del libro."""

from __future__ import annotations

from .config import ANIOS, MESES, ND
from .tablero import Tablero
from .utilidades import a_millones, fecha_anterior, fecha_anterior_anio, fecha_mes, trimestre


def preparar_filas(
    tablero: Tablero,
    universo: list[dict],
    nombres: dict[str, str],
    anio: int,
    icap: dict | None = None,
) -> list[dict]:
    filas: list[dict] = []
    fecha_pdf = (icap or {}).get("fecha")
    bancos_pdf = (icap or {}).get("bancos", {})

    for mes in ANIOS[anio]:
        fecha = fecha_mes(anio, mes)
        previa = fecha_anterior(fecha)
        previa_anio = fecha_anterior_anio(fecha)
        es_mes_pdf = fecha == fecha_pdf

        for reg in universo:
            clave = reg["clave"]
            del_pdf = bancos_pdf.get(clave, {}) if es_mes_pdf else {}
            v = tablero.valores.get((clave, fecha), {})
            icap_pdf = (
                del_pdf.get("icap")
                if es_mes_pdf and v.get("icap_pub") is None
                else None
            )
            p = tablero.valores.get((clave, previa), {})
            pa = tablero.valores.get((clave, previa_anio), {})

            filas.append(
                {
                    "no": reg["consecutivo"],
                    "clave": clave,
                    "banco": nombres.get(clave, reg["nombre"]),
                    "federacion": reg.get("federacion", "n.d."),
                    "nivel": reg.get("nivel", "n.d."),
                    "estatus": reg.get("estatus", "n.d."),
                    "tipo": reg.get("tipo", "n.d."),
                    "anio": anio,
                    "mes": MESES[mes],
                    "trimestre": trimestre(mes),
                    "activos": a_millones(v.get("activos")),
                    "activos_riesgo": a_millones(v.get("activos_riesgo")),
                    "capital_neto": a_millones(v.get("capital_neto")),
                    "icap_pub": v.get("icap_pub"),
                    "icap_pdf": icap_pdf,
                    "cartera_total": a_millones(v.get("cartera_total")),
                    "cartera_e3": a_millones(v.get("cartera_e3")),
                    "cartera_neta": a_millones(v.get("cartera_neta")),
                    "estimaciones": a_millones(v.get("estimaciones")),
                    "ingresos_int": a_millones(v.get("ingresos_int")),
                    "gastos_int": a_millones(v.get("gastos_int")),
                    "margen_fin": a_millones(v.get("margen_fin")),
                    "margen_ajustado": a_millones(v.get("margen_ajustado")),
                    "gastos_adm": a_millones(v.get("gastos_adm")),
                    "resultado_neto": a_millones(v.get("resultado_neto")),
                    "captacion_tradicional": a_millones(v.get("captacion_tradicional")),
                    "captacion_total": a_millones(v.get("captacion_total")),
                    "captacion_prev": a_millones(p.get("captacion_total")),
                    "cartera_total_prev": a_millones(
                        p.get("cartera_total")
                    ),
                    "captacion_prev_anio": a_millones(pa.get("captacion_total")),
                    "cartera_total_prev_anio": a_millones(pa.get("cartera_total")),
                    "activos_prom_12m": a_millones(v.get("activos_prom_12m")),
                    "capital_contable": a_millones(v.get("capital_contable")),
                    "capital_prom_12m": a_millones(v.get("capital_prom_12m")),
                    "resultado_12m": a_millones(v.get("resultado_12m")),
                    "margen_fin_12m": a_millones(v.get("margen_fin_12m")),
                    "margen_ajustado_12m": a_millones(v.get("margen_ajustado_12m")),
                    "activo_prod_prom_12m": a_millones(v.get("activo_prod_prom_12m")),
                    "ingresos_operacion": a_millones(v.get("ingresos_operacion")),
                    "imor_pub": v.get("imor_pub"),
                    "icor_pub": v.get("icor_pub"),
                    "roa_pub": v.get("roa_pub"),
                    "roe_pub": v.get("roe_pub"),
                    "min_pub": v.get("min_pub"),
                    "ccl": v.get("ccl"),
                    "cfen": v.get("cfen"),
                    "ccb": del_pdf.get("ccb", ND),
                    "ccf": del_pdf.get("ccf", ND),
                    "categoria": del_pdf.get("categoria", ND),
                    "tiene_datos": bool(v),
                }
            )

    return filas