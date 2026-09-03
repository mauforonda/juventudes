"""Calcula el porcentaje de jóvenes que habla una lengua indígena."""

from pathlib import Path

import pandas as pd

from comun import escribir_resultados, validar_codigos_municipales, validar_ficha
from cpv import DIMENSIONES_JOVENES, calcular_porcentaje, cargar_personas

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
VARIABLES = ["p331_idiohab1_cod", "p332_idiohab2_cod", "p333_idiohab3_cod"]
COLUMNAS_RESULTADO = [
    "gestion",
    *DIMENSIONES_JOVENES,
    "numerador",
    "denominador",
    "valor",
]


def calcular():
    datos = cargar_personas(VARIABLES).assign(
        **{
            variable: lambda tabla, variable=variable: pd.to_numeric(
                tabla[variable], errors="coerce"
            )
            for variable in VARIABLES
        }
    )
    habla_indigena = lambda tabla: pd.concat(
        [
            tabla[variable].between(1, 37) & tabla[variable].ne(6)
            for variable in VARIABLES
        ],
        axis=1,
    ).any(axis=1)
    respuesta_valida = lambda tabla: tabla[VARIABLES].notna().any(axis=1) & ~tabla[
        VARIABLES
    ].eq(999).all(axis=1)
    return calcular_porcentaje(
        datos,
        caso=habla_indigena,
        valido=respuesta_valida,
        dimensiones=DIMENSIONES_JOVENES,
    )


def main() -> None:
    validar_ficha(FICHA_PATH)
    resultados = calcular()
    validar_codigos_municipales(resultados, "codigo_municipio")
    escribir_resultados(
        resultados,
        RESULTADOS_PATH,
        columnas=COLUMNAS_RESULTADO,
        ordenar_por=DIMENSIONES_JOVENES,
    )


if __name__ == "__main__":
    main()
