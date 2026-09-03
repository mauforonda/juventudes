"""Calcula el rezago educativo de la población joven."""

from pathlib import Path

import pandas as pd

from comun import escribir_resultados, validar_codigos_municipales, validar_ficha
from cpv import DIMENSIONES_JOVENES, calcular_porcentaje, cargar_personas

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
NIVEL = "p41a_nivel"
CURSO = "p41b_curso"
COLUMNAS_RESULTADO = [
    "gestion",
    *DIMENSIONES_JOVENES,
    "numerador",
    "denominador",
    "valor",
]


def anios_escolares_aprobados(datos):
    return (
        pd.Series(pd.NA, index=datos.index, dtype="Int64")
        .mask(datos[NIVEL].isin([1, 2, 3]), 0)
        .mask(datos[NIVEL].eq(4), datos[CURSO])
        .mask(datos[NIVEL].eq(5), 5 + datos[CURSO])
        .mask(datos[NIVEL].eq(6), 8 + datos[CURSO])
        .mask(datos[NIVEL].eq(7), datos[CURSO])
        .mask(datos[NIVEL].eq(8), 6 + datos[CURSO])
        .mask(datos[NIVEL].between(9, 13), 12)
    )


def calcular():
    datos = (
        cargar_personas([NIVEL, CURSO])
        .loc[lambda tabla: tabla[NIVEL].between(1, 13) & tabla[CURSO].ne(9)]
        .assign(
            anios_aprobados=anios_escolares_aprobados,
            anios_esperados=lambda tabla: (tabla["edad"] - 6).clip(upper=12),
        )
    )
    return calcular_porcentaje(
        datos,
        caso=lambda tabla: tabla["anios_aprobados"].lt(tabla["anios_esperados"]),
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
