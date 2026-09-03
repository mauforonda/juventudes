"""Calcula la continuidad del servicio de agua en hogares con jóvenes."""

from pathlib import Path
import pandas as pd
from comun import escribir_resultados, validar_ficha
from eh import DIMENSIONES_JOVENES, GESTION, cargar_personas_con_hogar
from encuestas import estimar_media

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
DIAS = "s06a_08a"
HORAS = "s06a_08b"
COLUMNAS_RESULTADO = [
    "gestion",
    *DIMENSIONES_JOVENES,
    "medida",
    "observaciones",
    "valor",
    "cv",
]


def calcular():
    datos = cargar_personas_con_hogar(
        "EH2025_Vivienda_1.parquet", columnas_hogar=[DIAS, HORAS]
    )
    return pd.concat(
        [
            estimar_media(
                datos.loc[lambda d: d[DIAS].between(1, 7)],
                variable=DIAS,
                dimensiones=DIMENSIONES_JOVENES,
                gestion=GESTION,
            ).assign(medida="dias_por_semana"),
            estimar_media(
                datos.loc[lambda d: d[HORAS].between(1, 24)],
                variable=HORAS,
                dimensiones=DIMENSIONES_JOVENES,
                gestion=GESTION,
            ).assign(medida="horas_por_dia"),
        ],
        ignore_index=True,
    ).loc[:, COLUMNAS_RESULTADO]


def main() -> None:
    validar_ficha(FICHA_PATH)
    escribir_resultados(
        calcular(),
        RESULTADOS_PATH,
        columnas=COLUMNAS_RESULTADO,
        ordenar_por=[*DIMENSIONES_JOVENES, "medida"],
    )


if __name__ == "__main__":
    main()
