"""Calcula la violencia ejercida por personas distintas de la pareja."""

from pathlib import Path
from comun import escribir_resultados, validar_ficha
from edsa import DIMENSIONES_JOVENES, GESTION, cargar_individuales
from encuestas import estimar_porcentaje

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
AGRESION = "agresion"
VIOLENCIA_SEXUAL = "violencia_sexual"
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
    datos = cargar_individuales(
        {AGRESION: "ms11_1132", VIOLENCIA_SEXUAL: "ms11_1135"},
        {AGRESION: "vs08_0824", VIOLENCIA_SEXUAL: "vs08_0827"},
    )
    return estimar_porcentaje(
        datos,
        caso=lambda d: d[AGRESION].isin([1, 2, 3, 96]) | d[VIOLENCIA_SEXUAL].eq(1),
        valido=lambda d: d[AGRESION].isin([1, 2, 3, 4, 96])
        & d[VIOLENCIA_SEXUAL].isin([1, 2]),
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
