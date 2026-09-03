"""Calcula el consumo reciente de comida rápida entre jóvenes."""

from pathlib import Path
from comun import escribir_resultados, validar_ficha
from edsa import DIMENSIONES_JOVENES, GESTION, cargar_individuales
from encuestas import estimar_porcentaje

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
CONSUMO = "consumo"
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
    datos = cargar_individuales({CONSUMO: "ms05_0503_A"}, {CONSUMO: "vs01_0131_A"})
    return estimar_porcentaje(
        datos,
        caso=lambda d: d[CONSUMO].eq(1),
        valido=lambda d: d[CONSUMO].isin([1, 2]),
        dimensiones=DIMENSIONES_JOVENES,
        gestion=GESTION,
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
