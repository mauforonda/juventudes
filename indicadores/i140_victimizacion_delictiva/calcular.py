"""Calcula la victimización delictiva durante los últimos 12 meses."""

from pathlib import Path
from comun import escribir_resultados, validar_ficha
from eh import DIMENSIONES_JOVENES, GESTION, cargar_discriminacion
from encuestas import estimar_porcentaje

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
PRIMER_DELITO = "s09b_02a"
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
    return estimar_porcentaje(
        cargar_discriminacion([PRIMER_DELITO]),
        caso=lambda d: d[PRIMER_DELITO].isin(range(1, 7)),
        valido=lambda d: d[PRIMER_DELITO].isin(range(1, 9)),
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
