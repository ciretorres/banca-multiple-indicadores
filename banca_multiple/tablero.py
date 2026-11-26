"""Lectura del tablero de información financiera de la CNBV."""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path

from .config import CLAVE_SECTOR, CONCEPTOS, GRUPOS, TIPO_SALDO
from .utilidades import _a_numero, normalizar_clave


@dataclass
class Tablero:
    valores: dict[tuple[str, str], dict[str, float]]
    sector: dict[tuple[str, str], float]
    grupos: dict[tuple[str, str], dict[str, float]] = field(default_factory=dict)

    def dato(self, clave: str, fecha: str, campo: str):
        return self.valores.get((clave, fecha), {}).get(campo)

    def dato_grupo(self, grupo: str, fecha: str, campo: str):
        return self.grupos.get((grupo, fecha), {}).get(campo)

    def dato_sector(self, fecha: str, campo: str):
        return self.sector.get((fecha, campo))


def leer_tablero(ruta, fechas: set[str]) -> Tablero:
    valores: dict[tuple[str, str], dict[str, float]] = {}
    sector: dict[tuple[str, str], float] = {}
    grupos: dict[tuple[str, str], dict[str, float]] = {}
    leidas = 0

    with open(ruta, newline="", encoding="utf-8-sig") as f:
        for registro in csv.DictReader(f):
            if registro.get("tipo_saldo") != TIPO_SALDO:
                continue

            fecha = registro.get("fecha", "")
            if fecha not in fechas:
                continue

            campo = CONCEPTOS.get(registro.get("concepto", ""))
            if not campo:
                continue

            valor = _a_numero(registro.get("saldo_se"))
            if valor is None:
                continue

            institucion = str(registro.get("institucion", "")).strip()
            leidas += 1

            if institucion == CLAVE_SECTOR:
                sector[(fecha, campo)] = valor
                continue

            if institucion in GRUPOS:
                grupos.setdefault((institucion, fecha), {})[campo] = valor
                continue

            clave = normalizar_clave(institucion)
            valores.setdefault((clave, fecha), {})[campo] = valor

    print(
        f"  tablero: {leidas:,} registros útiles de {Path(ruta).name} "
        f"({len(fechas)} meses)"
    )
    return Tablero(valores=valores, sector=sector, grupos=grupos)