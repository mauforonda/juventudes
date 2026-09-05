"""Calcula el número de grupos de alimentos consumidos por jóvenes."""

from pathlib import Path
from comun import escribir_resultados, validar_ficha
from edsa import (
    DIMENSIONES_JOVENES,
    GESTION,
    armonizar_ponderadores_individuales,
    cargar_individuales,
)
from encuestas import estimar_media, sumar_ponderadores

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
LETRAS = list("ABCDEFGHIJKLMNOPQRS")
VARIABLES = [f"alimento_{letra.lower()}" for letra in LETRAS]
MAPA_MUJER = dict(zip(VARIABLES, [f"ms05_0502_{letra}" for letra in LETRAS]))
MAPA_HOMBRE = dict(zip(VARIABLES, [f"vs01_0130_{letra}" for letra in LETRAS]))
GRUPOS = [
    list("ABC"),
    list("DEF"),
    list("GH"),
    ["I"],
    list("JKL"),
    list("MNO"),
    list("PQ"),
    list("RS"),
]
DIVERSIDAD = "grupos_consumidos"
COLUMNAS_RESULTADO = [
    "gestion",
    *DIMENSIONES_JOVENES,
    "observaciones",
    "poblacion_estimada",
    "valor",
    "cv",
]


def calcular():
    datos = armonizar_ponderadores_individuales(
        cargar_individuales(MAPA_MUJER, MAPA_HOMBRE)
    ).loc[lambda d: d[VARIABLES].isin([1, 2]).all(axis=1)]
    consumo = [
        datos[[f"alimento_{letra.lower()}" for letra in grupo]].eq(1).any(axis=1)
        for grupo in GRUPOS
    ]
    datos = datos.assign(
        grupos_consumidos=sum(serie.astype("int64") for serie in consumo)
    )
    return estimar_media(
        datos, variable=DIVERSIDAD, dimensiones=DIMENSIONES_JOVENES, gestion=GESTION
    ).merge(
        sumar_ponderadores(datos, dimensiones=DIMENSIONES_JOVENES),
        on=DIMENSIONES_JOVENES,
        validate="one_to_one",
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
