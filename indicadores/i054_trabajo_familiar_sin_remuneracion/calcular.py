"""Calcula el trabajo familiar sin remuneración entre jóvenes ocupados."""

from pathlib import Path

from comun import escribir_resultados, validar_codigos_municipales, validar_ficha
from cpv import DIMENSIONES_JOVENES
from empleo_cpv import CATEGORIA_OCUPACIONAL, calcular_porcentaje_ocupados

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
COLUMNAS_RESULTADO = [
    "gestion",
    *DIMENSIONES_JOVENES,
    "numerador",
    "denominador",
    "valor",
]


def calcular():
    return calcular_porcentaje_ocupados(
        CATEGORIA_OCUPACIONAL,
        caso=lambda d: d[CATEGORIA_OCUPACIONAL].eq(4),
        valido=lambda d: d[CATEGORIA_OCUPACIONAL].isin(range(1, 7)),
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
