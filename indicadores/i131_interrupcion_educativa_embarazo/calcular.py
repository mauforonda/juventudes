"""Calcula la interrupción educativa durante embarazos."""

from pathlib import Path
from comun import escribir_resultados, validar_ficha
from edsa import DIMENSIONES_JOVENES, GESTION, cargar_mujeres
from encuestas import estimar_porcentaje

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
PRIMERA = "interrupcion_primera"
SIGUIENTES = "interrupcion_siguientes"
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
    datos = cargar_mujeres({PRIMERA: "ms02_0211", SIGUIENTES: "ms02_0212"})
    return estimar_porcentaje(
        datos,
        caso=lambda d: d[[PRIMERA, SIGUIENTES]].eq(1).any(axis=1),
        valido=lambda d: d[PRIMERA].isin([1, 2, 3]) | d[SIGUIENTES].isin([1, 2, 3, 4]),
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
