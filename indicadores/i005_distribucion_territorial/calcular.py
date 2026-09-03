"""Calcula la distribución territorial de la población joven."""

from pathlib import Path

from comun import escribir_resultados, validar_codigos_municipales, validar_ficha
from cpv import GESTION, cargar_personas


BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
DIMENSIONES = ["codigo_municipio", "area"]
COLUMNAS_RESULTADO = [
    "gestion",
    *DIMENSIONES,
    "numerador",
    "denominador",
    "valor",
]


def calcular():
    """Cuenta jóvenes por municipio y área y calcula su peso nacional."""

    return (
        cargar_personas()
        .groupby(DIMENSIONES, as_index=False)
        .size()
        .rename(columns={"size": "numerador"})
        .assign(
            gestion=GESTION,
            denominador=lambda datos: datos["numerador"].sum(),
            valor=lambda datos: 100 * datos["numerador"] / datos["denominador"],
        )
        .loc[:, COLUMNAS_RESULTADO]
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
