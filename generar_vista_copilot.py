#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera el libro compañero de cortes trimestrales para Copilot."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from banca_multiple.be import leer_universo
from banca_multiple.config import (
    ANIOS,
    BE_UNIVERSO,
    CSV_TABLERO,
    CORTES_TRIMESTRALES,
    DIR_ENTRADAS,
    PDF_ICAP,
    SALIDA_VISTA_COPILOT,
)
from banca_multiple.filas import preparar_filas
from banca_multiple.pdf_icap import leer_icap
from banca_multiple.tablero import leer_tablero
from banca_multiple.utilidades import fecha_anterior, fecha_anterior_anio, fecha_mes
from banca_multiple.vista_copilot import escribir_vista_copilot


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Genera el Excel de cortes trimestrales para Copilot."
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=SALIDA_VISTA_COPILOT,
        help=f"Ruta exacta del .xlsx (por defecto {SALIDA_VISTA_COPILOT})",
    )
    args = parser.parse_args()

    ruta_universo = DIR_ENTRADAS / BE_UNIVERSO
    ruta_csv = DIR_ENTRADAS / CSV_TABLERO
    ruta_pdf = DIR_ENTRADAS / PDF_ICAP
    faltantes = [
        str(ruta) for ruta in (ruta_universo, ruta_csv, ruta_pdf) if not ruta.exists()
    ]
    if faltantes:
        raise SystemExit("Faltan archivos de entrada: " + ", ".join(faltantes))

    universo = leer_universo(ruta_universo)
    nombres = {reg["clave"]: reg["nombre"] for reg in universo}
    datos_icap = leer_icap(ruta_pdf, nombres)

    anios = sorted({anio for _, anio, _, _ in CORTES_TRIMESTRALES})
    fechas: set[str] = set()
    for anio in anios:
        for mes in ANIOS[anio]:
            fecha = fecha_mes(anio, mes)
            fechas.update((fecha, fecha_anterior(fecha), fecha_anterior_anio(fecha)))

    tablero = leer_tablero(ruta_csv, fechas)
    filas = {
        anio: preparar_filas(tablero, universo, nombres, anio, icap=datos_icap)
        for anio in anios
    }

    escribir_vista_copilot(filas, args.out)

    print(f"Entradas: {DIR_ENTRADAS} · {len(universo)} bancos")
    print(f"Cortes: {len(CORTES_TRIMESTRALES)} · 54 bancos por corte")
    print(f"Archivo generado: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
