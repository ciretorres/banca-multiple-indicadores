"""Validación de los datos leídos contra el boletín y el tablero."""

from __future__ import annotations

from .config import CAMPOS_SECTOR, CLAVE_SECTOR, GRUPOS, MES_NUM

from .utilidades import _norm, fecha_mes

def _num(x) -> bool:
    return isinstance(x, (int, float))


def _tolera_dif(dif: float, publicado: float) -> bool:
    return dif <= 0.02 or dif <= 1e-5 * abs(publicado)


PARESES_PDF = (("icap", "icap_pub"), ("ccb", "ccb_pub"), ("ccf", "ccf_pub"))


def _validar_icap_pdf(tablero, universo, icap) -> bool:
    fecha = icap.get("fecha")
    bancos = icap.get("bancos", {})
    total = icap.get("total", {})
    if not fecha or not bancos or not total:
        return True

    print(f"\n  ICAP / CCB / CCF del PDF vs tablero ({fecha}):")
    ok = True
    peor = 0.0
    peor_origen = ""

    def revisar(etiqueta, valores_pdf, valores_tabla):
        nonlocal ok, peor, peor_origen
        diferencias = [
            abs(valores_tabla[campo] - valores_pdf[campo_pdf])
            for campo_pdf, campo in PARESES_PDF
            if _num(valores_tabla.get(campo)) and _num(valores_pdf.get(campo_pdf))
        ]
        if not diferencias:
            return
        diferencia = max(diferencias)
        if diferencia > peor:
            peor, peor_origen = diferencia, etiqueta
        estado = "OK" if diferencia <= 0.02 else "DIF"
        if estado == "DIF":
            ok = False
        print(f"    {etiqueta:<32} peor dif {diferencia:,.4f} pts · {estado}")

    for registro in universo:
        clave = registro["clave"]
        valores_pdf = bancos.get(clave)
        if not valores_pdf:
            print(f"    {clave} · sin dato en el PDF")
            ok = False
            continue
        revisar(
            f"{clave} {registro['nombre']}",
            valores_pdf,
            tablero.valores.get((clave, fecha), {}),
        )

    valores_sector = {
        campo: tablero.sector.get((fecha, campo)) for _, campo in PARESES_PDF
    }
    revisar("5 Total Banca Múltiple", total, valores_sector)
    print(
        f"    peor diferencia: {peor:,.4f} pts ({peor_origen}) · "
        f"{'OK' if ok else 'DIF'}"
    )
    return ok


def validar_datos(tablero, filas, universo, be_por_archivo, icap=None) -> bool:
    ok = True
    print("\n=== Validación de datos ===")
    claves = [u["clave"] for u in universo]

    print("\n  Cobertura por mes:")
    for anio, lista in filas.items():
        por_mes: dict[str, int] = {}
        for f in lista:
            por_mes[f["mes"]] = por_mes.get(f["mes"], 0) + 1
        malos = {m: c for m, c in por_mes.items() if c != len(universo)}
        print(
            f"    {anio}: {len(lista)} filas · {len(por_mes)} meses · "
            f"{'todas con ' + str(len(universo)) if not malos else malos}"
        )
        if malos:
            ok = False

    print("\n  Consistencia del tablero: suma de los 54 bancos vs total 5 y grupos 59-64:")
    tolerancia = 1_000_000.0
    for referencia in [CLAVE_SECTOR] + list(GRUPOS):
        for campo in CAMPOS_SECTOR:
            comparaciones = 0
            peor = 0.0
            for anio, lista in filas.items():
                for mes in sorted({MES_NUM[f["mes"]] for f in lista}):
                    fecha = fecha_mes(anio, mes)
                    if referencia == CLAVE_SECTOR:
                        esperado = tablero.sector.get((fecha, campo))
                    else:
                        esperado = tablero.grupos.get((referencia, fecha), {}).get(campo)
                    if esperado is None:
                        continue
                    suma = sum(
                        tablero.valores.get((clave, fecha), {}).get(campo, 0.0)
                        for clave in claves
                    )
                    comparaciones += 1
                    peor = max(peor, abs(suma - esperado))
                    if (
                        referencia == CLAVE_SECTOR
                        and not str(fecha).startswith("2025")
                        and abs(suma - esperado) > tolerancia
                    ):
                        ok = False
            estado = "OK" if peor <= tolerancia else f"DIF {peor:,.2f}"
            print(
                f"    {referencia:>2} · {campo:<28} {comparaciones:>2} meses · "
                f"peor dif {peor:,.2f} · {estado}"
            )

    def crudo(f):
        return tablero.valores.get((f["clave"], fecha_mes(f["anio"], MES_NUM[f["mes"]])), {})

    def _indexar_be(be_por_archivo):
        indice = {}

        def agregar(reg):
            if not isinstance(reg, dict):
                return
            clave = reg.get("clave", reg.get("clave_banco", reg.get("institucion")))
            if clave is None:
                nombre = reg.get("nombre")
                if isinstance(nombre, str) and _norm(nombre).startswith("sistema"):
                    clave = CLAVE_SECTOR
            if clave is None:
                return
            fecha = reg.get("fecha")
            indicador = reg.get("indicador")
            valor = reg.get("valor")
            if valor is None and indicador in ("roa_pub", "roe_pub"):
                valor = reg.get(indicador)
            if fecha is None or indicador is None or valor is None:
                return
            indice[(str(clave), str(fecha), str(indicador))] = valor

        if isinstance(be_por_archivo, dict):
            for clave, valor in be_por_archivo.items():
                if isinstance(valor, (list, tuple)):
                    for reg in valor:
                        agregar(reg)
                elif isinstance(valor, dict):
                    if "valor" in valor and "indicador" in valor:
                        reg = dict(valor)
                        reg.setdefault("clave", clave)
                        agregar(reg)
                    else:
                        for fecha, vals in valor.items():
                            if isinstance(vals, dict):
                                for indicador, val in vals.items():
                                    indice[(str(clave), str(fecha), str(indicador))] = val
        elif isinstance(be_por_archivo, (list, tuple)):
            for reg in be_por_archivo:
                agregar(reg)
        return indice

    indice_be = _indexar_be(be_por_archivo)

    # ROA / ROE
    print("\n  ROA / ROE calculados vs publicados (BE):")
    if not indice_be:
        print("    (sin datos del BE: se omite)")
    else:
        for nombre, num, den, pub in [
            ("ROA", "resultado_12m", "activos_prom_12m", "roa_pub"),
            ("ROE", "resultado_12m", "capital_prom_12m", "roe_pub"),
        ]:
            comparaciones = 0
            peor = 0.0
            peor_fila = None
            # Bancos del universo
            for anio, lista in filas.items():
                for f in lista:
                    fecha = fecha_mes(f["anio"], MES_NUM[f["mes"]])
                    be_val = indice_be.get((str(f["clave"]), fecha, pub))
                    v = crudo(f)
                    if not (_num(v.get(num)) and _num(v.get(den)) and _num(be_val)):
                        continue
                    if v.get(den) == 0:
                        continue
                    calculado = v[num] / v[den] * 100
                    dif = abs(calculado - be_val)
                    comparaciones += 1
                    if dif > peor:
                        peor, peor_fila = dif, f
            # Sistema
            for anio, lista in filas.items():
                for mes in sorted({MES_NUM[f["mes"]] for f in lista}):
                    fecha = fecha_mes(anio, mes)
                    be_val = indice_be.get((CLAVE_SECTOR, fecha, pub))
                    vres = tablero.sector.get((fecha, num))
                    vden = tablero.sector.get((fecha, den))
                    if not (_num(vres) and _num(vden) and _num(be_val)):
                        continue
                    if vden == 0:
                        continue
                    calculado = vres / vden * 100
                    dif = abs(calculado - be_val)
                    comparaciones += 1
                    if dif > peor:
                        peor, peor_fila = dif, "Sistema"
            estado = "OK" if peor <= 0.02 else f"DIF {peor:,.4f}"
            if comparaciones and peor > 0.02:
                ok = False
            if peor_fila == "Sistema":
                extra = " (Sistema)"
            elif peor_fila:
                extra = f" ({peor_fila['clave']} {peor_fila['mes']} {peor_fila['anio']})"
            else:
                extra = ""
            print(f"    {nombre}: {comparaciones:>3} comparaciones · peor dif {peor:,.4f} pts · {estado}{extra}")

    # ICAP / IMOR / ICOR / MIN
    print("\n  ICAP / IMOR / ICOR / MIN publicado calculados vs publicados:")
    pruebas = [
        ("ICAP", lambda v: v["capital_neto"] / v["activos_riesgo"] * 100, "icap_pub", ("capital_neto", "activos_riesgo")),
        ("IMOR", lambda v: v["cartera_e3"] / v["cartera_total"] * 100, "imor_pub", ("cartera_e3", "cartera_total")),
        ("ICOR", lambda v: abs(v["estimaciones"]) / v["cartera_e3"] * 100, "icor_pub", ("estimaciones", "cartera_e3")),
        ("MIN publicado (no ajustado)", lambda v: v["margen_fin_12m"] / v["activo_prod_prom_12m"] * 100, "min_pub", ("margen_fin_12m", "activo_prod_prom_12m")),
    ]
    for nombre, calculo, campo_pub, requeridos in pruebas:
        comparaciones = 0
        peor = 0.0
        peor_fila = None
        peor_falla = 0.0
        peor_falla_fila = None
        for anio, lista in filas.items():
            for f in lista:
                v = crudo(f)
                if not all(_num(v.get(c)) for c in requeridos):
                    continue
                if not _num(f.get(campo_pub)):
                    continue
                if nombre == "ICAP" and (not v.get("activos_riesgo")):
                    continue
                if nombre.startswith(("IMOR", "ICOR", "MIN")) and not v.get(requeridos[-1] if nombre != "IMOR" else "cartera_total"):
                    continue
                if nombre == "ICOR" and v.get("cartera_e3") == 0:
                    continue
                dif = abs(calculo(v) - f[campo_pub])
                comparaciones += 1
                if dif > peor:
                    peor, peor_fila = dif, f
                tol = 0.05 if nombre == "IMOR" else 0.02
                if dif > tol and dif > peor_falla:
                    peor_falla, peor_falla_fila = dif, f
        hay_falla = peor_falla_fila is not None
        if hay_falla:
            ok = False
        mostrar = peor_falla if hay_falla else peor
        mostrar_fila = peor_falla_fila if hay_falla else peor_fila
        estado = "OK" if not hay_falla else f"DIF {mostrar:,.4f}"
        extra = f" ({mostrar_fila['clave']} {mostrar_fila['mes']} {mostrar_fila['anio']})" if mostrar_fila else ""
        print(f"    {nombre}: {comparaciones:>3} comparaciones · peor dif {peor:,.4f} pts · {estado}{extra}")

    print(
        "  Nota: el MIN publicado por la CNBV (4040001) usa Margen Financiero "
        "12M (no ajustado); el libro muestra MIN con Margen Financiero "
        "Ajustado 12M según la spec."
    )

    if icap:
        ok &= _validar_icap_pdf(tablero, universo, icap)

    _ = claves
    return ok