#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Estructura base del generador de indicadores de Banca Múltiple.

El código vive en el paquete banca_multiple/; este archivo solo lo invoca.
La lógica se implementará siguiendo el flujo spec-driven (spec 001).
"""

from __future__ import annotations

import sys

from banca_multiple.main import main

if __name__ == "__main__":
    sys.exit(main())
