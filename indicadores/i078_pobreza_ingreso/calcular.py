"""Calcula la pobreza por ingreso entre jóvenes."""

from pathlib import Path
from comun import escribir_resultados, validar_ficha
from eh import DIMENSIONES_JOVENES, GESTION, cargar_personas
from encuestas import estimar_porcentaje

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
POBREZA = "p0"
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
    datos = cargar_personas([POBREZA])
    return estimar_porcentaje(
        datos,
        caso=lambda d: d[POBREZA].eq(1),
        valido=lambda d: d[POBREZA].isin([0, 1]),
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
