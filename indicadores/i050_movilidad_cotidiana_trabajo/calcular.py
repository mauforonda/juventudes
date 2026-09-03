"""Calcula la movilidad cotidiana de jóvenes por motivos de trabajo."""

from pathlib import Path

from comun import escribir_resultados, validar_codigos_municipales, validar_ficha
from cpv import DIMENSIONES_JOVENES, calcular_porcentaje, cargar_personas

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
CONDICION_ACTIVIDAD = "condact_19"
LUGAR_TRABAJO = "p52_mov"
COLUMNAS_RESULTADO = [
    "gestion",
    *DIMENSIONES_JOVENES,
    "numerador",
    "denominador",
    "valor",
]


def calcular():
    datos = cargar_personas([CONDICION_ACTIVIDAD, LUGAR_TRABAJO])
    return calcular_porcentaje(
        datos,
        caso=lambda d: d[LUGAR_TRABAJO].isin([3, 4]),
        valido=lambda d: d[CONDICION_ACTIVIDAD].eq(1)
        & d[LUGAR_TRABAJO].isin([1, 2, 3, 4]),
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
