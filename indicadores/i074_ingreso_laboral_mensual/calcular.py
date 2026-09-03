"""Calcula la media y mediana del ingreso laboral mensual."""

from pathlib import Path
import pandas as pd
from comun import escribir_resultados, validar_ficha
from ece import DIMENSIONES_JOVENES, GESTION, cargar_personas
from encuestas import estimar_media, estimar_mediana

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
CONDICION_ACTIVIDAD = "condact"
INGRESO = "ylab"
COLUMNAS_RESULTADO = [
    "gestion",
    *DIMENSIONES_JOVENES,
    "estadistico",
    "observaciones",
    "valor",
    "cv",
]


def calcular():
    datos = cargar_personas([CONDICION_ACTIVIDAD, INGRESO]).loc[
        lambda d: d[CONDICION_ACTIVIDAD].eq(1) & d[INGRESO].gt(0)
    ]
    return pd.concat(
        [
            estimar_media(
                datos,
                variable=INGRESO,
                dimensiones=DIMENSIONES_JOVENES,
                gestion=GESTION,
            ).assign(estadistico="media"),
            estimar_mediana(
                datos,
                variable=INGRESO,
                dimensiones=DIMENSIONES_JOVENES,
                gestion=GESTION,
            ).assign(estadistico="mediana"),
        ],
        ignore_index=True,
    ).loc[:, COLUMNAS_RESULTADO]


def main() -> None:
    validar_ficha(FICHA_PATH)
    escribir_resultados(
        calcular(),
        RESULTADOS_PATH,
        columnas=COLUMNAS_RESULTADO,
        ordenar_por=[*DIMENSIONES_JOVENES, "estadistico"],
    )


if __name__ == "__main__":
    main()
