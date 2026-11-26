"""Validaciones de estructura, contenido y formato del libro Excel generado."""

from __future__ import annotations

from pathlib import Path

from openpyxl import load_workbook

from .config import ND
from .estilos import ENC_CATALOGO, FILA_DATOS, FILA_ENC
from .fichas import FICHAS, FICHAS_SEMAFORO, TOTAL_REGLAS


def hojas_esperadas(filas: dict[int, list[dict]]) -> list[str]:
    anios = sorted(filas, reverse=True)
    return (
        ["Catálogo"]
        + [f"Datos Fuente {a}" for a in anios]
        + [f"Indicadores {a}" for a in anios]
        + ["Diccionario", "Semáforos"]
    )


def validar_libro(ruta: Path, universo: list[dict], filas: dict[int, list[dict]]) -> bool:
    ok = True
    wb = load_workbook(ruta)

    print("\n=== Validación del libro generado ===")
    print(f"  hojas: {wb.sheetnames}")

    esperadas = hojas_esperadas(filas)
    if wb.sheetnames != esperadas:
        print(f"  ERROR: se esperaban {esperadas}.")
        ok = False

    cat = wb["Catálogo"]
    dic = wb["Diccionario"]
    sem = wb["Semáforos"]

    encabezados = [
        cat.cell(row=FILA_ENC, column=j).value
        for j in range(1, len(ENC_CATALOGO) + 1)
    ]
    if encabezados != ENC_CATALOGO:
        print(f"  ERROR: encabezados del Catálogo: {encabezados!r}")
        ok = False

    filas_cat = sum(
        1 for r in range(FILA_DATOS, FILA_DATOS + len(universo))
        if cat.cell(row=r, column=2).value
    )
    print(f"  Catálogo: {filas_cat} filas (esperado {len(universo)})")
    if filas_cat != len(universo):
        ok = False

    for anio, lista in filas.items():
        datos = wb[f"Datos Fuente {anio}"]
        ind = wb[f"Indicadores {anio}"]

        filas_datos = sum(
            1 for r in range(FILA_DATOS, FILA_DATOS + len(lista))
            if datos.cell(row=r, column=1).value is not None
        )
        filas_ind = sum(
            1 for r in range(FILA_DATOS, FILA_DATOS + len(lista))
            if ind.cell(row=r, column=1).value is not None
        )
        print(
            f"  Datos Fuente {anio}: {filas_datos} filas · "
            f"Indicadores {anio}: {filas_ind} (esperado {len(lista)})"
        )
        if filas_datos != len(lista) or filas_ind != len(lista):
            ok = False

        desalineadas = [
            r for r in range(FILA_DATOS, FILA_DATOS + len(lista))
            if (
                datos.cell(row=r, column=2).value != ind.cell(row=r, column=2).value
                or datos.cell(row=r, column=4).value != ind.cell(row=r, column=4).value
                or datos.cell(row=r, column=5).value != ind.cell(row=r, column=5).value
            )
        ]
        print(f"    filas desalineadas: {len(desalineadas)}")
        if desalineadas:
            ok = False

        meses = {}
        for r in range(FILA_DATOS, FILA_DATOS + len(lista)):
            mes = datos.cell(row=r, column=4).value
            meses[mes] = meses.get(mes, 0) + 1
        esperado = len({f["clave"] for f in lista})
        malos = {m: c for m, c in meses.items() if c != esperado}
        print(f"    meses: {len(meses)} · {'todas con ' + str(esperado) if not malos else malos}")
        if malos:
            ok = False

        r0 = FILA_DATOS
        for col, esperado_formula in [
            (9, f'=IFERROR(H{r0}/G{r0},"{ND}")'),
            (16, f'=IFERROR(N{r0}-O{r0},"{ND}")'),
        ]:
            valor = datos.cell(row=r0, column=col).value
            if valor != esperado_formula:
                print(f"      ERROR: Datos Fuente {anio} col{col} = {valor!r}")
                ok = False

        for col in (5, 10, 17, 35):
            if datos.cell(row=r0, column=col).value is None:
                print(f"      ERROR: Datos Fuente {anio} col{col} vacía")
                ok = False

        if ind.cell(row=r0, column=5).value is None:
            print(f"      ERROR: Indicadores {anio} col5 vacía")
            ok = False
        for col in range(6, 17):
            valor = ind.cell(row=r0, column=col).value
            if not (isinstance(valor, str) and valor.startswith("=")):
                print(f"      ERROR: Indicadores {anio} col{col} no es fórmula: {valor!r}")
                ok = False

        formula_gastos = ind.cell(row=r0, column=15).value
        if '"n.a."' not in str(formula_gastos):
            print(f"      ERROR: Indicadores {anio} O{r0} no maneja n.a.: {formula_gastos!r}")
            ok = False

        if ind.cell(row=FILA_ENC, column=14).value != "Crédito Neto / Captación\n(%)":
            print(f"      ERROR: Indicadores {anio} no tiene el orden de columnas esperado.")
            ok = False

    filas_dic = sum(
        1 for r in range(FILA_DATOS, FILA_DATOS + len(FICHAS))
        if dic.cell(row=r, column=1).value
    )
    print(f"  Diccionario: {filas_dic} indicadores (esperado {len(FICHAS)})")
    if filas_dic != len(FICHAS):
        ok = False

    bloques = sum(
        1 for r in range(FILA_DATOS, sem.max_row + 1)
        if sem.cell(row=r, column=1).value == "Umbral"
    )
    print(f"  Semáforos: {bloques} bloques (esperado {len(FICHAS_SEMAFORO)})")
    if bloques != len(FICHAS_SEMAFORO):
        ok = False

    for anio in filas:
        ind = wb[f"Indicadores {anio}"]
        reglas = sum(
            len(lista_reglas)
            for lista_reglas in ind.conditional_formatting._cf_rules.values()
        )
        print(f"  formato condicional {anio}: {reglas} reglas (esperado {TOTAL_REGLAS})")
        if reglas != TOTAL_REGLAS:
            ok = False

    return ok