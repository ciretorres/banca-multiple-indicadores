"""Funciones auxiliares para normalizar y convertir datos."""

from __future__ import annotations

import re
import unicodedata

from .config import MILES


def _a_numero(texto):
    if texto is None:
        return None
    if isinstance(texto, (int, float)):
        return float(texto)
    try:
        return float(str(texto).replace(",", "").replace("$", "").strip())
    except ValueError:
        return None


def _norm(texto) -> str:
    s = unicodedata.normalize("NFKD", str(texto or ""))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s).strip().lower()


def normalizar_clave(valor) -> str:
    digitos = re.sub(r"\D", "", str(valor))
    return digitos.zfill(6)


def trimestre(mes: int) -> str:
    return f"T{((mes - 1) // 3) + 1}"


def fecha_mes(anio: int, mes: int) -> str:
    return f"{anio}{mes:02d}"


def fecha_anterior(fecha: str) -> str:
    anio, mes = int(fecha[:4]), int(fecha[4:])
    mes -= 1
    if mes == 0:
        anio, mes = anio - 1, 12
    return f"{anio}{mes:02d}"


def fecha_anterior_anio(fecha: str) -> str:
    return f"{int(fecha[:4]) - 1}{fecha[4:]}"


def enumerar(valores) -> str:
    v = list(valores)
    if not v:
        return ""
    if len(v) == 1:
        return v[0]
    return ", ".join(v[:-1]) + " e " + v[-1]


def a_millones(valor):
    if valor is None:
        return None
    return round(float(valor) / MILES, 2)
