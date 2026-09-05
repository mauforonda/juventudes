"""Calcula el gasto anual directo en salud de cada joven."""

from pathlib import Path
import pandas as pd
from comun import escribir_resultados, validar_ficha
from eh import DIMENSIONES_JOVENES, GESTION, cargar_personas
from encuestas import estimar_media, estimar_mediana, sumar_ponderadores

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
COMPONENTES = ["s02a_03a", "s02a_03b", "s02a_03c", "s02a_03d", "s02a_03e"]
GASTO = "gasto_salud"
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
    datos = cargar_personas(COMPONENTES).assign(
        gasto_salud=lambda d: d[COMPONENTES].sum(axis=1, min_count=len(COMPONENTES))
    )
    return (
        pd.concat([
            estimar_media(
                datos, variable=GASTO, dimensiones=DIMENSIONES_JOVENES, gestion=GESTION
            ).assign(estadistico="media"),
            estimar_mediana(
                datos, variable=GASTO, dimensiones=DIMENSIONES_JOVENES, gestion=GESTION
            ).assign(estadistico="mediana"),
        ], ignore_index=True)
        .merge(
            sumar_ponderadores(
                datos.dropna(subset=[GASTO]),
                dimensiones=DIMENSIONES_JOVENES,
            ),
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
