"""Calcula la antigüedad de jóvenes ocupados en la empresa actual."""

from pathlib import Path

from comun import escribir_resultados, validar_ficha
from eh import (
    DIMENSIONES_JOVENES,
    GESTION,
    cargar_personas,
    clasificar_duracion,
    convertir_a_meses,
)
from encuestas import estimar_distribucion

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
TIEMPO = "s04b_11aa"
UNIDAD_TIEMPO = "s04b_11ab"
CATEGORIA = "antiguedad_empresa"
COLUMNAS_RESULTADO = [
    "gestion",
    *DIMENSIONES_JOVENES,
    CATEGORIA,
    "observaciones",
    "numerador",
    "denominador",
    "valor",
    "cv",
]


def calcular():
    datos = cargar_personas([TIEMPO, UNIDAD_TIEMPO]).assign(
        duracion_meses=lambda d: convertir_a_meses(d[TIEMPO], d[UNIDAD_TIEMPO]),
        antiguedad_empresa=lambda d: clasificar_duracion(d["duracion_meses"]),
    )
    return estimar_distribucion(
        datos, categoria=CATEGORIA, dimensiones=DIMENSIONES_JOVENES, gestion=GESTION
    )


def main() -> None:
    validar_ficha(FICHA_PATH)
    escribir_resultados(
        calcular(),
        RESULTADOS_PATH,
        columnas=COLUMNAS_RESULTADO,
        ordenar_por=[*DIMENSIONES_JOVENES, CATEGORIA],
    )


if __name__ == "__main__":
    main()
