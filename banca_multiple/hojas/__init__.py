"""Construcción y guardado del libro Excel de Banca Múltiple."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from openpyxl import Workbook

from .catalogo import escribir_catalogo
from .datos_fuente import escribir_datos_fuente
from .diccionario import escribir_diccionario
from .indicadores import escribir_indicadores
from .semaforos import escribir_semaforos


def escribir_xlsx(
    universo: list[dict],
    bajas: list[dict],
    nombres: dict[str, str],
    filas: dict[int, list[dict]],
    ruta: Path,
    datos_icap: dict | None = None,
) -> None:
    anios = sorted(filas, reverse=True)
    n_entidades = len(universo) + len(bajas)

    wb = Workbook()
    wb.remove(wb.active)

    escribir_catalogo(wb, universo, nombres, bajas, datos_icap=datos_icap)
    for a in anios:
        escribir_datos_fuente(wb, filas[a], a, n_entidades)
    for a in anios:
        escribir_indicadores(wb, filas[a], a)
    escribir_diccionario(wb, anios)
    escribir_semaforos(wb, anios)

    rango = f"{min(anios)}-{max(anios)}" if len(anios) > 1 else str(anios[0])
    wb.properties.title = f"Bancos Multiples - Indicadores {rango}"
    wb.properties.creator = "Generador automatico (tablero CNBV + BE)"

    wb.calculation.fullCalcOnLoad = True

    ruta.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("wb", suffix=".xlsx", dir=ruta.parent, delete=False) as tmp:
        wb.save(tmp.name)
        temporal = tmp.name

    os.replace(temporal, ruta)