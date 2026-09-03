"""Calcula la recepción de aguinaldo entre jóvenes asalariados."""

from pathlib import Path
from comun import escribir_resultados, validar_ficha
from ece import DIMENSIONES_JOVENES
from empleo_ece import calcular_porcentaje_asalariados

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
AGUINALDO = "s2_36c"
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
    return calcular_porcentaje_asalariados(
        AGUINALDO,
        caso=lambda d: d[AGUINALDO].eq(1),
        valido=lambda d: d[AGUINALDO].isin([1, 2]),
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
