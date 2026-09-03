"""Calcula la composición por sexo de la población joven."""

from pathlib import Path

from comun import escribir_resultados, validar_codigos_municipales, validar_ficha
from cpv import calcular_distribucion, cargar_personas


BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
DIMENSIONES = ["codigo_municipio", "area", "edad"]
COLUMNAS_RESULTADO = [
    "gestion",
    *DIMENSIONES,
    "sexo",
    "numerador",
    "denominador",
    "valor",
]


def calcular():
    """Distribuye a los jóvenes de cada territorio y edad por sexo."""

    return calcular_distribucion(
        cargar_personas(),
        categoria="sexo",
        dimensiones=DIMENSIONES,
    )


def main() -> None:
    validar_ficha(FICHA_PATH)
    resultados = calcular()
    validar_codigos_municipales(resultados, "codigo_municipio")
    escribir_resultados(
        resultados,
        RESULTADOS_PATH,
        columnas=COLUMNAS_RESULTADO,
        ordenar_por=[*DIMENSIONES, "sexo"],
    )


if __name__ == "__main__":
    main()
