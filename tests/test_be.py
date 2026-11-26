"""Pruebas de lectura del boletín electrónico de Banca Múltiple."""

from banca_multiple.be import leer_roa_roe_be, leer_universo
from banca_multiple.config import DIR_ENTRADAS, BE_UNIVERSO


RUTA_BE = DIR_ENTRADAS / BE_UNIVERSO


def test_leer_universo():
    universo = leer_universo(RUTA_BE)
    assert len(universo) == 54
    assert all(u["clave"].startswith("040") and len(u["clave"]) == 6 for u in universo)


def test_leer_roa_roe_be():
    datos = leer_roa_roe_be(RUTA_BE)
    assert datos
    sistemas = [r for r in datos if r.get("clave") == "5"]
    bancos = [r for r in datos if r.get("clave", "").startswith("040")]
    assert any(r.get("indicador") == "roa_pub" for r in sistemas)
    assert any(r.get("indicador") == "roe_pub" for r in sistemas)
    assert len(bancos) > 0
    assert any(r.get("indicador") in ("roa_pub", "roe_pub") for r in bancos)