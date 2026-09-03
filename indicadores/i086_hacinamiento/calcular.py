"""Calcula el hacinamiento en los hogares donde viven jóvenes."""

from pathlib import Path
from comun import escribir_resultados, validar_codigos_municipales, validar_ficha
from cpv import DIMENSIONES_JOVENES, calcular_porcentaje, cargar_personas

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
DORMITORIOS = "v14_dormit"
COLUMNAS_RESULTADO = [
    "gestion",
    *DIMENSIONES_JOVENES,
    "numerador",
    "denominador",
    "valor",
]


def calcular():
    datos = (
        cargar_personas(columnas_vivienda=[DORMITORIOS], solo_jovenes=False)
        .assign(personas_hogar=lambda d: d.groupby("i00")["i00"].transform("size"))
        .loc[lambda d: d["edad"].between(16, 28)]
    )
    return calcular_porcentaje(
        datos,
        caso=lambda d: d["personas_hogar"].div(d[DORMITORIOS]).gt(3),
        valido=lambda d: d[DORMITORIOS].gt(0),
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
