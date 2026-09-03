"""Calcula la afiliación y aporte actual para jubilación."""

from pathlib import Path
from comun import escribir_resultados, validar_ficha
from ece import DIMENSIONES_JOVENES, GESTION, cargar_personas
from encuestas import estimar_porcentaje

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
CONDICION_ACTIVIDAD = "condact"
AFILIACION = "s2_64"
APORTE = "s2_64a"
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
    datos = cargar_personas([CONDICION_ACTIVIDAD, AFILIACION, APORTE])
    return estimar_porcentaje(
        datos,
        caso=lambda d: d[AFILIACION].eq(1) & d[APORTE].isin([1, 2]),
        valido=lambda d: d[CONDICION_ACTIVIDAD].eq(1) & d[AFILIACION].isin([1, 2]),
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
