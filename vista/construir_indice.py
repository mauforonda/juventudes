#!/usr/bin/env python3
"""Construye el índice mínimo consumido por la vista estática."""

from __future__ import annotations

import json
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
INDICADORES = BASE / "indicadores"
SALIDA = Path(__file__).resolve().parent / "indice.json"
CONFIGURACIONES = Path(__file__).resolve().parent / "configuraciones"
DICCIONARIOS = BASE / "diccionarios"
CAMPOS = ("nombre", "definicion_conceptual", "fuente")


def cargar_diccionario(nombre: str) -> dict:
    return json.loads((DICCIONARIOS / nombre).read_text(encoding="utf-8"))


def construir_indice() -> dict:
    indicadores = {}
    temas = cargar_diccionario("temas.json")
    espacios = cargar_diccionario("espacios_politica.json")
    for ruta in sorted(INDICADORES.glob("*/ficha.json")):
        ficha = json.loads(ruta.read_text(encoding="utf-8"))
        faltantes = [campo for campo in CAMPOS if not ficha.get(campo)]
        if faltantes:
            campos = ", ".join(faltantes)
            raise ValueError(f"{ruta}: faltan campos obligatorios: {campos}")
        slug = ruta.parent.name
        indicadores[slug] = {
                "slug": slug,
                "tiene_config": (CONFIGURACIONES / f"{ruta.parent.name}.json").is_file(),
                "temas": ficha.get("temas", []),
                "espacios_politica": ficha.get("espacios_politica", []),
                **{campo: ficha[campo] for campo in CAMPOS},
            }
    for grupo, campo in ((temas, "temas"), (espacios, "espacios_politica")):
        for clave, datos in grupo.items():
            datos["indicadores"] = [
                slug for slug, indicador in indicadores.items()
                if clave in indicador.get(campo, [])
            ]
    return {
        "indicadores": indicadores,
        "temas": [
            {"id": clave, **datos}
            for clave, datos in temas.items()
        ],
        "espacios_politica": [
            {"id": clave, **datos}
            for clave, datos in espacios.items()
        ],
    }


if __name__ == "__main__":
    datos = construir_indice()
    SALIDA.write_text(
        json.dumps(datos, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"{len(datos['indicadores'])} indicadores escritos en {SALIDA}")
