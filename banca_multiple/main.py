"""Genera y valida el libro Excel de indicadores de Banca Múltiple."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from .be import leer_roa_roe_be, leer_universo
from .config import (
    ANIOS,
    BE_UNIVERSO,
    CSV_TABLERO,
    DIR_ENTRADAS,
    DIR_SALIDAS,
    PDF_ICAP,
    SALIDA_DEFECTO,
)
from .filas import preparar_filas
from .hojas import escribir_xlsx
from .pdf_icap import leer_icap
from .tablero import leer_tablero
from .utilidades import fecha_anterior, fecha_anterior_anio, fecha_mes
from .validacion_datos import validar_datos
from .validacion_libro import validar_libro


def parse_anios(texto: str | None) -> dict[int, tuple[int, ...]]:
    if texto is None:
        return ANIOS

    rango = re.fullmatch(r"(\d{4})(?:-(\d{4}))?", texto)
    if not rango:
        raise SystemExit(f"--anios inválido: {texto!r} (usa AAAA o AAAA-AAAA)")

    inicio = int(rango.group(1))
    fin = int(rango.group(2) or inicio)
    if inicio > fin:
        raise SystemExit(f"--anios inválido: {texto!r} (rango descendente)")

    elegidos = range(inicio, fin + 1)
    faltantes = [a for a in elegidos if a not in ANIOS]
    if faltantes:
        raise SystemExit(
            f"--anios: año no contemplado {faltantes[0]} "
            f"(disponibles: {', '.join(str(a) for a in sorted(ANIOS))})"
        )

    return {a: ANIOS[a] for a in elegidos}


def ruta_pdf_icap(args, dir_entradas: Path) -> Path:
    if args.pdf_icap:
        return args.pdf_icap.expanduser().resolve()
    return dir_entradas / PDF_ICAP


def fecha_en_anios(fecha: str, anios: dict[int, tuple[int, ...]]) -> bool:
    return any(
        fecha == fecha_mes(anio, mes)
        for anio, meses in anios.items()
        for mes in meses
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Genera el Excel de indicadores de Banca Múltiple."
    )
    parser.add_argument(
        "--entradas",
        type=Path,
        default=DIR_ENTRADAS,
        help="Carpeta con el BE y la carpeta tablero/",
    )
    parser.add_argument(
        "--salidas",
        type=Path,
        default=DIR_SALIDAS,
        help="Carpeta donde se escribe el .xlsx",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Ruta exacta del .xlsx",
    )
    parser.add_argument(
        "--tablero",
        type=Path,
        default=None,
        help="Ruta exacta del CSV 040_TO.csv",
    )
    parser.add_argument(
        "--anios",
        default=None,
        help="Años a incluir: AAAA o AAAA-AAAA",
    )
    parser.add_argument(
        "--pdf-icap",
        type=Path,
        default=None,
        help=f"Ruta exacta del PDF de ICAP (por defecto {PDF_ICAP} en entradas/)",
    )
    args = parser.parse_args()

    anios_sel = parse_anios(args.anios)

    dir_entradas = args.entradas.expanduser().resolve()
    if not dir_entradas.is_dir():
        raise SystemExit(f"No existe la carpeta de entradas: {dir_entradas}")

    ruta_csv = (
        args.tablero.expanduser().resolve()
        if args.tablero
        else dir_entradas / CSV_TABLERO
    )
    ruta_universo = dir_entradas / BE_UNIVERSO
    ruta_pdf = ruta_pdf_icap(args, dir_entradas)

    faltantes = [
        str(ruta) for ruta in (ruta_csv, ruta_universo, ruta_pdf) if not ruta.exists()
    ]
    if faltantes:
        disponibles = sorted(archivo.name for archivo in dir_entradas.iterdir() if archivo.is_file())
        raise SystemExit(
            "Faltan archivos:\n  - "
            + "\n  - ".join(faltantes)
            + "\nContenido actual de entradas/:\n  - "
            + ("\n  - ".join(disponibles) or "(vacía)")
        )

    salida = args.out or (args.salidas.expanduser().resolve() / SALIDA_DEFECTO.name)

    universo = leer_universo(ruta_universo)
    roa_roe_be = leer_roa_roe_be(ruta_universo)
    bajas = []
    nombres = {reg["clave"]: reg["nombre"] for reg in universo}

    print(f"Entradas: {dir_entradas}")
    print(f"Universo: {len(universo)} bancos · {ruta_universo.name}")

    datos_icap = leer_icap(ruta_pdf, nombres)
    print(f"PDF de ICAP: {ruta_pdf.name} · corte {datos_icap['fecha']}")
    if not fecha_en_anios(datos_icap["fecha"], anios_sel):
        raise SystemExit(
            f"La fecha del PDF de ICAP ({datos_icap['fecha']}) no está entre "
            "los meses generados; ajusta --pdf-icap o --anios."
        )

    fechas: set[str] = set()
    for anio, meses in anios_sel.items():
        for mes in meses:
            fecha = fecha_mes(anio, mes)
            fechas.add(fecha)
            fechas.add(fecha_anterior(fecha))
            fechas.add(fecha_anterior_anio(fecha))

    print(f"\nLeyendo tablero: {ruta_csv.name} ...")
    tablero = leer_tablero(ruta_csv, fechas)

    filas = {
        anio: preparar_filas(tablero, universo, nombres, anio, icap=datos_icap)
        for anio in anios_sel
    }
    print(
        "  filas preparadas: "
        + " · ".join(f"{anio}: {len(registros)}" for anio, registros in filas.items())
    )

    todo_ok = validar_datos(tablero, filas, universo, roa_roe_be, icap=datos_icap)
    escribir_xlsx(universo, bajas, nombres, filas, salida)
    todo_ok &= validar_libro(salida, universo, filas)

    print(f"\nArchivo generado: {salida}")
    print("Validación general:", "OK" if todo_ok else "CON OBSERVACIONES")
    return 0 if todo_ok else 2