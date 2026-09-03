"""Calcula el acceso juvenil a agua proveniente de una red."""

from pathlib import Path
from comun import escribir_resultados, validar_codigos_municipales, validar_ficha
from cpv import DIMENSIONES_JOVENES, calcular_porcentaje, cargar_personas

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
AGUA = "v07_aguapro"
COLUMNAS_RESULTADO = [
    "gestion",
    *DIMENSIONES_JOVENES,
    "numerador",
    "denominador",
    "valor",
]


def calcular():
    datos = cargar_personas(columnas_vivienda=[AGUA])
    return calcular_porcentaje(
        datos,
        caso=lambda d: d[AGUA].eq(1),
        valido=lambda d: d[AGUA].between(1, 9),
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
