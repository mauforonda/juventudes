"""Calcula el peso de la juventud en la población."""

from pathlib import Path

from comun import escribir_resultados, validar_codigos_municipales, validar_ficha
from cpv import calcular_porcentaje, cargar_personas


BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
DIMENSIONES = ["codigo_municipio", "area", "sexo"]
COLUMNAS_RESULTADO = [
    "gestion",
    *DIMENSIONES,
    "numerador",
    "denominador",
    "valor",
]


def calcular():
    """Cuenta jóvenes dentro de la población de cada territorio y sexo."""

    return calcular_porcentaje(
        cargar_personas(solo_jovenes=False),
        caso=lambda datos: datos["edad"].between(16, 28),
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
        ordenar_por=DIMENSIONES,
    )


if __name__ == "__main__":
    main()
