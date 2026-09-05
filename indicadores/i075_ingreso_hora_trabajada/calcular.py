"""Calcula la media y mediana del ingreso por hora trabajada."""

from pathlib import Path
import pandas as pd
from comun import escribir_resultados, validar_ficha
from ece import DIMENSIONES_JOVENES, GESTION, cargar_personas
from encuestas import estimar_media, estimar_mediana, sumar_ponderadores

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
CONDICION_ACTIVIDAD = "condact"
INGRESO = "ylab"
HORAS = "tothrs"
INGRESO_HORA = "ingreso_hora"
COLUMNAS_RESULTADO = [
    "gestion",
    *DIMENSIONES_JOVENES,
    "estadistico",
    "observaciones",
    "poblacion_estimada",
    "valor",
    "cv",
]


def calcular():
    datos = (
        cargar_personas([CONDICION_ACTIVIDAD, INGRESO, HORAS])
        .loc[
            lambda d: d[CONDICION_ACTIVIDAD].eq(1)
            & d[INGRESO].gt(0)
            & d[HORAS].between(1, 168)
        ]
        .assign(ingreso_hora=lambda d: d[INGRESO] / (d[HORAS] * 52 / 12))
    )
    return (
        pd.concat([
            estimar_media(
                datos,
                variable=INGRESO_HORA,
                dimensiones=DIMENSIONES_JOVENES,
                gestion=GESTION,
            ).assign(estadistico="media"),
            estimar_mediana(
                datos,
                variable=INGRESO_HORA,
                dimensiones=DIMENSIONES_JOVENES,
                gestion=GESTION,
            ).assign(estadistico="mediana"),
        ], ignore_index=True)
        .merge(
            sumar_ponderadores(datos, dimensiones=DIMENSIONES_JOVENES),
            on=DIMENSIONES_JOVENES,
            validate="many_to_one",
        )
        .loc[:, COLUMNAS_RESULTADO]
    )


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
