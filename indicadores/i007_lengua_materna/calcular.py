"""Calcula la distribución de jóvenes por código de lengua materna."""

from pathlib import Path

import pandas as pd

from comun import escribir_resultados, validar_codigos_municipales, validar_ficha
from cpv import DIMENSIONES_JOVENES, calcular_distribucion, cargar_personas


BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
VARIABLE = "idioma_mat"
CATEGORIA = "codigo_lengua_materna"
COLUMNAS_RESULTADO = [
    "gestion",
    *DIMENSIONES_JOVENES,
    CATEGORIA,
    "numerador",
    "denominador",
    "valor",
]


def calcular():
    """Distribuye las respuestas válidas según el código oficial de lengua."""

    datos = (
        cargar_personas([VARIABLE])
        .loc[lambda tabla: tabla[VARIABLE].ne(999)]
        .assign(
            **{
                CATEGORIA: lambda tabla: pd.to_numeric(tabla[VARIABLE])
                .astype("Int64")
                .astype("string")
                .str.zfill(3)
            }
        )
    )
    return calcular_distribucion(
        datos,
        categoria=CATEGORIA,
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
        ordenar_por=[*DIMENSIONES_JOVENES, CATEGORIA],
    )


if __name__ == "__main__":
    main()
