"""Calcula el promedio y la mediana de edad al primer hijo."""

from pathlib import Path
import pandas as pd
from comun import escribir_resultados, validar_ficha
from edsa import (
    DIMENSIONES_JOVENES,
    GESTION,
    armonizar_ponderadores_individuales,
    cargar_hombres,
    cargar_mujeres,
)
from encuestas import estimar_media, estimar_mediana, sumar_ponderadores

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
EDAD_PRIMER_HIJO = "edad_primer_hijo"
COLUMNAS_RESULTADO = [
    "gestion",
    *DIMENSIONES_JOVENES,
    "medida",
    "observaciones",
    "poblacion_estimada",
    "valor",
    "cv",
]


def cargar_edades():
    mujeres = cargar_mujeres(
        {
            "nacimiento_primer_hijo_cmc": "b3_01",
            "nacimiento_madre_cmc": "v011",
        }
    ).assign(
        **{
            EDAD_PRIMER_HIJO: lambda d: (
                (d["nacimiento_primer_hijo_cmc"] - d["nacimiento_madre_cmc"]) // 12
            )
        }
    )
    hombres = cargar_hombres({EDAD_PRIMER_HIJO: "vs02_0216"})
    columnas = [*DIMENSIONES_JOVENES, "factor", "estrato", "upm", EDAD_PRIMER_HIJO]
    return armonizar_ponderadores_individuales(
        pd.concat([mujeres[columnas], hombres[columnas]], ignore_index=True)
    ).loc[lambda d: d[EDAD_PRIMER_HIJO].between(10, d["edad"])]


def calcular():
    datos = cargar_edades()
    return (
        pd.concat([
            estimar_media(
                datos,
                variable=EDAD_PRIMER_HIJO,
                dimensiones=DIMENSIONES_JOVENES,
                gestion=GESTION,
            ).assign(medida="promedio"),
            estimar_mediana(
                datos,
                variable=EDAD_PRIMER_HIJO,
                dimensiones=DIMENSIONES_JOVENES,
                gestion=GESTION,
            ).assign(medida="mediana"),
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
        ordenar_por=[*DIMENSIONES_JOVENES, "medida"],
    )


if __name__ == "__main__":
    main()
