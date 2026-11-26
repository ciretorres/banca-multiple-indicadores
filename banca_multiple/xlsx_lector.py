"""Utilidades para leer hojas de cálculo XLSX directamente desde su contenido XML."""

from __future__ import annotations

import posixpath
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

from .utilidades import _a_numero, _norm

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
RNS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
NS_REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"


def _col_letra(ref: str) -> str:
    m = re.match(r"[A-Z]+", ref or "")
    return m.group(0) if m else ""


def _leer_shared_strings(z: zipfile.ZipFile) -> list[str]:
    try:
        raiz = ET.fromstring(z.read("xl/sharedStrings.xml"))
    except KeyError:
        return []

    return [
        "".join(t.text or "" for t in si.iter(NS + "t"))
        for si in raiz.findall(NS + "si")
    ]


def _rutas_de_hojas(z: zipfile.ZipFile) -> dict[str, str]:
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    mapa = {
        r.get("Id"): r.get("Target")
        for r in rels.findall(NS_REL + "Relationship")
    }

    rutas = {}
    for hoja in wb.find(NS + "sheets"):
        destino = mapa[hoja.get(RNS + "id")]
        if destino.startswith("/"):
            ruta = destino.lstrip("/")
        else:
            ruta = posixpath.normpath(posixpath.join("xl", destino))
        rutas[hoja.get("name")] = ruta

    return rutas


def _leer_hoja(
    z: zipfile.ZipFile,
    ruta: str,
    shared: list[str],
) -> dict[int, dict[str, object]]:
    raiz = ET.fromstring(z.read(ruta))
    filas: dict[int, dict[str, object]] = {}

    for fila in raiz.iter(NS + "row"):
        numero = int(fila.get("r"))
        celdas: dict[str, object] = {}

        for celda in fila.findall(NS + "c"):
            col = _col_letra(celda.get("r"))
            tipo = celda.get("t")
            v = celda.find(NS + "v")

            if tipo == "inlineStr":
                valor = "".join(t.text or "" for t in celda.iter(NS + "t"))
            elif v is None:
                continue
            elif tipo == "s":
                valor = shared[int(v.text)]
            elif tipo in ("str", "e"):
                valor = v.text
            else:
                num = _a_numero(v.text)
                valor = num if num is not None else v.text

            celdas[col] = valor

        filas[numero] = celdas

    return filas


def _abrir_hoja(ruta, nombre: str) -> dict[int, dict[str, object]]:
    ruta = Path(ruta)
    with zipfile.ZipFile(ruta) as z:
        shared = _leer_shared_strings(z)
        rutas = _rutas_de_hojas(z)

        if nombre not in rutas:
            raise SystemExit(
                f"No se encontró la hoja '{nombre}' en {ruta.name}. "
                f"Hojas: {sorted(rutas)}"
            )

        return _leer_hoja(z, rutas[nombre], shared)


def _fila_encabezado(hoja, texto: str) -> int:
    objetivo = _norm(texto)
    for num in sorted(hoja):
        if _norm(hoja[num].get("D", "")).startswith(objetivo):
            return num
    raise SystemExit(f"No se localizó el encabezado '{texto}' en la columna D.")