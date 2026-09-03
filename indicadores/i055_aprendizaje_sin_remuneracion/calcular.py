"""Calcula el aprendizaje sin remuneración entre jóvenes ocupados."""

from pathlib import Path

from comun import escribir_resultados, validar_ficha
from ece import DIMENSIONES_JOVENES
from empleo_ece import calcular_porcentaje_ocupados

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
CATEGORIA_OCUPACIONAL = "s2_18"
COLUMNAS_RESULTADO = [
    "gestion",
    *DIMENSIONES_JOVENES,
    "observaciones",
    "numerador",
    "denominador",
    "valor",
    "cv",
]


def calcular():
    return calcular_porcentaje_ocupados(
        CATEGORIA_OCUPACIONAL,
        caso=lambda d: d[CATEGORIA_OCUPACIONAL].eq(6),
        valido=lambda d: d[CATEGORIA_OCUPACIONAL].isin(range(1, 8)),
    )


def main() -> None:
    validar_ficha(FICHA_PATH)
    escribir_resultados(
        calcular(),
        RESULTADOS_PATH,
        columnas=COLUMNAS_RESULTADO,
        ordenar_por=DIMENSIONES_JOVENES,
    )


if __name__ == "__main__":
    main()
