"""Calcula la carga del alquiler en hogares encabezados por jóvenes."""

from pathlib import Path
import pandas as pd
from comun import escribir_resultados, validar_ficha
from eh import DIMENSIONES_JOVENES, GESTION, cargar_personas_con_hogar
from encuestas import estimar_media, estimar_mediana

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
PARENTESCO = "s01a_05"
INGRESO_HOGAR = "yhog"
TENENCIA = "s06a_02"
ALQUILER = "s06a_02b"
CARGA = "carga_alquiler"
COLUMNAS_RESULTADO = [
    "gestion",
    *DIMENSIONES_JOVENES,
    "estadistico",
    "observaciones",
    "valor",
    "cv",
]


def calcular():
    datos = (
        cargar_personas_con_hogar(
            "EH2025_Vivienda_1.parquet",
            columnas_persona=[PARENTESCO, INGRESO_HOGAR],
            columnas_hogar=[TENENCIA, ALQUILER],
        )
        .loc[
            lambda d: d[PARENTESCO].eq(1)
            & d[TENENCIA].eq(3)
            & d[ALQUILER].gt(0)
            & d[INGRESO_HOGAR].gt(0)
        ]
        .assign(carga_alquiler=lambda d: 100 * d[ALQUILER] / d[INGRESO_HOGAR])
    )
    return pd.concat(
        [
            estimar_media(
                datos, variable=CARGA, dimensiones=DIMENSIONES_JOVENES, gestion=GESTION
            ).assign(estadistico="media"),
            estimar_mediana(
                datos, variable=CARGA, dimensiones=DIMENSIONES_JOVENES, gestion=GESTION
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
