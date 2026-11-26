"""Lectura de boletines financieros y del universo de Banca Múltiple."""

from __future__ import annotations

import datetime as dt
import re

from .config import HOJA_INDICADORES_BE, HOJA_UNIVERSO
from .utilidades import _a_numero, _norm, normalizar_clave
from .xlsx_lector import _abrir_hoja


def leer_universo(ruta) -> list[dict]:
    """Lee los 54 bancos del BE desde ``Evaluación Calidad Detallada``."""
    hoja = _abrir_hoja(ruta, HOJA_UNIVERSO)
    registros = []
    for num in sorted(hoja):
        fila = hoja[num]
        ranking = fila.get("B")
        clave_cruda = fila.get("C")
        nombre = fila.get("D")
        if not isinstance(clave_cruda, str):
            continue
        clave_cruda = clave_cruda.strip()
        if not re.fullmatch(r"040\d{3}", clave_cruda):
            continue
        if _a_numero(ranking) is None:
            continue
        registros.append(
            {
                "consecutivo": int(_a_numero(ranking)),
                "clave": normalizar_clave(clave_cruda),
                "nombre": str(nombre).strip() if nombre is not None else "",
                "fecha_autorizacion": None,
                "nivel": "n.d.",
                "federacion": "n.d.",
                "estatus": "En operación",
                "tipo": "n.d.",
            }
        )
    return registros


def _serial_a_fecha(serial) -> str | None:
    if serial is None:
        return None
    try:
        fecha = dt.date(1899, 12, 30) + dt.timedelta(days=int(serial))
    except (ValueError, TypeError):
        return None
    return f"{fecha.year}{fecha.month:02d}"


def leer_roa_roe_be(ruta) -> list[dict]:
    """Lee ROA/ROE publicados del BE por banco y Sistema."""
    hoja = _abrir_hoja(ruta, HOJA_INDICADORES_BE)
    # Localiza la fila de fechas (contiene seriales Excel) y la de etiquetas.
    fila_fechas = None
    for num in sorted(hoja):
        vals = hoja[num]
        if any(isinstance(v, (int, float)) and v > 40000 for v in vals.values()):
            fila_fechas = num
            break
    if fila_fechas is None:
        return []

    fechas_roa = []
    fechas_roe = []
    for col, val in hoja[fila_fechas].items():
        if isinstance(val, (int, float)) and val > 40000:
            # Columnas C-E corresponden a ROA, F-H a ROE por posición.
            pass
    # Determinar columnas por letra: C,D,E = ROA; F,G,H = ROE
    for col in ["C", "D", "E"]:
        f = _serial_a_fecha(hoja[fila_fechas].get(col))
        if f:
            fechas_roa.append((col, f))
    for col in ["F", "G", "H"]:
        f = _serial_a_fecha(hoja[fila_fechas].get(col))
        if f:
            fechas_roe.append((col, f))

    universo = leer_universo(ruta)
    por_nombre = {_norm(r["nombre"]): r["clave"] for r in universo}

    resultados = []
    for num in sorted(hoja):
        if num <= fila_fechas:
            continue
        fila = hoja[num]
        nombre = fila.get("B")
        if not isinstance(nombre, str) or not nombre.strip():
            continue
        nombre = nombre.strip()
        clave = por_nombre.get(_norm(nombre))
        if clave is None and _norm(nombre).startswith("sistema"):
            clave = "5"
        for col, fecha in fechas_roa:
            val = fila.get(col)
            if isinstance(val, (int, float)):
                resultados.append(
                    {
                        "nombre": nombre,
                        "clave": clave,
                        "fecha": fecha,
                        "indicador": "roa_pub",
                        "valor": float(val),
                    }
                )
        for col, fecha in fechas_roe:
            val = fila.get(col)
            if isinstance(val, (int, float)):
                resultados.append(
                    {
                        "nombre": nombre,
                        "clave": clave,
                        "fecha": fecha,
                        "indicador": "roe_pub",
                        "valor": float(val),
                    }
                )
    return resultados