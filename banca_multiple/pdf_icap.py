"""Lectura del PDF de indicadores de capitalización de Banco de México."""

from __future__ import annotations

import re
from pathlib import Path

from pypdf import PdfReader

from .utilidades import _norm

CAMPOS = ("ccb", "ccf", "icap", "categoria")
N_BANCOS = 54

_RE_FECHA = re.compile(r"ICAP_BM_(\d{6})\.pdf$", re.IGNORECASE)
_RE_NUMERO = re.compile(r"\d+(?:[.,]\d+)?")
_RE_CATEGORIA = re.compile(r"[a-z]+")
_RE_TOTAL = re.compile(r"totalbancamultiple")


def _fecha_del_nombre(ruta) -> str:
    nombre = Path(ruta).name
    hallazgo = _RE_FECHA.search(nombre)
    if not hallazgo:
        raise SystemExit(
            f"No se pudo derivar la fecha del PDF {nombre!r}; "
            "se esperaba un archivo ICAP_BM_YYYYMM.pdf"
        )
    return hallazgo.group(1)


def _clave_nombre(texto: str) -> str:
    """Nombre sin acentos ni espacios, comparable con el catálogo del BE."""
    return re.sub(r"\s+", "", _norm(texto))


def _es_fila(linea: str) -> bool:
    tokens = _norm(linea).split()
    return (
        len(tokens) >= 5
        and _RE_CATEGORIA.fullmatch(tokens[-1]) is not None
        and all(_RE_NUMERO.fullmatch(t) for t in tokens[-4:-1])
    )


def _columnas(texto: str, archivo: str) -> list[str]:
    lineas = [linea.strip() for linea in texto.splitlines() if linea.strip()]
    inicio = next(
        (i for i, linea in enumerate(lineas) if "institucion" in _norm(linea)),
        None,
    )
    if inicio is None:
        raise SystemExit(f"{archivo}: no se encontró el encabezado 'Institución'.")

    # El encabezado ocupa varias líneas: nombre, nota al pie y '%'.
    bloque = []
    for linea in lineas[inicio:]:
        if _es_fila(linea):
            break
        bloque.append(_norm(linea))

    orden = []
    for hallazgo in re.finditer(r"ccb|ccf|icap|categoria", " ".join(bloque)):
        campo = hallazgo.group(0)
        if campo not in orden:
            orden.append(campo)

    faltan = [campo for campo in CAMPOS if campo not in orden]
    if faltan:
        raise SystemExit(
            f"{archivo}: faltan columnas en el encabezado: "
            f"{', '.join(campo.upper() for campo in faltan)}."
        )
    return orden


def _parse(
    texto: str,
    fecha: str,
    nombres: dict[str, str],
    archivo: str,
    n_bancos: int = N_BANCOS,
) -> dict:
    orden = _columnas(texto, archivo)
    por_nombre = {_clave_nombre(nombre): clave for clave, nombre in nombres.items()}
    bancos: dict[str, dict] = {}
    total = None
    no_mapeados: set[str] = set()

    for linea in texto.splitlines():
        if not _es_fila(linea):
            continue
        tokens = _norm(linea).split()
        nombre = _clave_nombre(" ".join(tokens[:-4]))
        valores = {
            campo: (
                token.upper()
                if campo == "categoria"
                else float(token.replace(",", "."))
            )
            for campo, token in zip(orden, tokens[-4:])
        }
        if _RE_TOTAL.fullmatch(nombre):
            total = valores
            continue
        clave = por_nombre.get(nombre)
        if clave is None:
            no_mapeados.add(" ".join(linea.split()[:-4]))
            continue
        bancos[clave] = valores

    if no_mapeados:
        raise SystemExit(
            f"{archivo}: nombres del PDF no reconocidos en el catálogo: "
            + ", ".join(sorted(no_mapeados))
        )
    if not bancos:
        raise SystemExit(f"{archivo}: no se encontraron filas de bancos.")
    if total is None:
        raise SystemExit(
            f"{archivo}: no se encontró el renglón 'Total Banca Múltiple'."
        )
    if len(bancos) != n_bancos:
        raise SystemExit(
            f"{archivo}: se esperaban {n_bancos} bancos además del Total; "
            f"se extrajeron {len(bancos)}. Revisa el formato del PDF."
        )
    return {"fecha": fecha, "bancos": bancos, "total": total}


def leer_icap(ruta_pdf, nombres: dict[str, str]) -> dict:
    """Lee el PDF e indexa ICAP, CCB, CCF y categoría por clave ``040xxx``."""
    ruta = Path(ruta_pdf)
    if not ruta.is_file():
        raise SystemExit(f"No existe el PDF de ICAP: {ruta}")
    fecha = _fecha_del_nombre(ruta)
    lector = PdfReader(str(ruta))
    texto = "\n".join((pagina.extract_text() or "") for pagina in lector.pages)
    return _parse(texto, fecha, nombres, ruta.name)
