#!/usr/bin/env python3
"""Construye el índice mínimo consumido por la vista estática."""

from __future__ import annotations

import json
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
INDICADORES = BASE / "indicadores"
SALIDA = Path(__file__).resolve().parent / "indice.json"
CAMPOS = ("nombre", "definicion_conceptual", "fuente")


def construir_indice() -> list[dict[str, str]]:
    indice = []
    for ruta in sorted(INDICADORES.glob("*/ficha.json")):
        ficha = json.loads(ruta.read_text(encoding="utf-8"))
        faltantes = [campo for campo in CAMPOS if not ficha.get(campo)]
        if faltantes:
            campos = ", ".join(faltantes)
            raise ValueError(f"{ruta}: faltan campos obligatorios: {campos}")
        indice.append(
            {
                "slug": ruta.parent.name,
                **{campo: ficha[campo] for campo in CAMPOS},
            }
        )
    return indice


if __name__ == "__main__":
    datos = construir_indice()
    SALIDA.write_text(
        json.dumps(datos, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"{len(datos)} indicadores escritos en {SALIDA}")
