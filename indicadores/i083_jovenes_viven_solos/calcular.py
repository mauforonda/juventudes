"""Calcula la proporción de jóvenes que viven solos."""

from pathlib import Path
from comun import escribir_resultados, validar_codigos_municipales, validar_ficha
from cpv import DIMENSIONES_JOVENES, calcular_porcentaje, cargar_personas

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
COLUMNAS_RESULTADO = [
    "gestion",
    *DIMENSIONES_JOVENES,
    "numerador",
    "denominador",
    "valor",
]


def calcular():
    datos = (
        cargar_personas(solo_jovenes=False)
        .assign(tamano_hogar=lambda d: d.groupby("i00")["i00"].transform("size"))
        .loc[lambda d: d["edad"].between(16, 28)]
    )
    return calcular_porcentaje(
        datos, caso=lambda d: d["tamano_hogar"].eq(1), dimensiones=DIMENSIONES_JOVENES
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
