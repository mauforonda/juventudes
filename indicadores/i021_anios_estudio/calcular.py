"""Calcula el promedio de años de estudio aprobados."""

from pathlib import Path

from comun import escribir_resultados, validar_codigos_municipales, validar_ficha
from cpv import DIMENSIONES_JOVENES, calcular_media, cargar_personas

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
VARIABLE = "aestudio"
COLUMNAS_RESULTADO = ["gestion", *DIMENSIONES_JOVENES, "observaciones", "valor"]


def calcular():
    datos = cargar_personas([VARIABLE]).loc[
        lambda tabla: tabla["edad"].between(19, 28) & tabla[VARIABLE].between(0, 23)
    ]
    return calcular_media(
        datos,
        variable=VARIABLE,
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
