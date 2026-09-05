"""Calcula la brecha del ingreso laboral por hora entre mujeres y hombres."""

from pathlib import Path
import numpy as np
from comun import escribir_resultados, validar_ficha
from ece import GESTION, cargar_personas
from encuestas import estimar_media, estimar_mediana

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
DIMENSIONES = ["codigo_departamento", "area", "edad"]
CONDICION_ACTIVIDAD = "condact"
INGRESO = "ylab"
HORAS = "tothrs"
INGRESO_HORA = "ingreso_hora"
COLUMNAS_RESULTADO = [
    "gestion",
    *DIMENSIONES,
    "observaciones_mujeres",
    "observaciones_hombres",
    "poblacion_mujeres",
    "poblacion_hombres",
    "media_mujeres",
    "media_hombres",
    "mediana_mujeres",
    "mediana_hombres",
    "brecha_media",
    "cv_brecha_media",
    "brecha_mediana",
    "cv_brecha_mediana",
]


def separar_sexo(estimaciones, sexo, sufijo):
    columnas = [
        "observaciones",
        "poblacion",
        "media",
        "cv_media",
        "mediana",
        "cv_mediana",
    ]
    return (
        estimaciones.loc[lambda d: d["sexo"].eq(sexo)]
        .drop(columns="sexo")
        .rename(columns={columna: f"{columna}_{sufijo}" for columna in columnas})
    )


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
    dimensiones_sexo = [*DIMENSIONES, "sexo"]
    estimaciones = (
        estimar_media(
            datos,
            variable=INGRESO_HORA,
            dimensiones=dimensiones_sexo,
            gestion=GESTION,
        )
        .rename(columns={"valor": "media", "cv": "cv_media"})
        .merge(
            estimar_mediana(
                datos,
                variable=INGRESO_HORA,
                dimensiones=dimensiones_sexo,
                gestion=GESTION,
            ).rename(
                columns={
                    "observaciones": "observaciones_mediana",
                    "valor": "mediana",
                    "cv": "cv_mediana",
                }
            ),
            on=["gestion", *dimensiones_sexo],
            validate="one_to_one",
        )
        .merge(
            datos.groupby(dimensiones_sexo, as_index=False, dropna=False).agg(
                poblacion=("factor", "sum")
            ),
            on=dimensiones_sexo,
            validate="one_to_one",
        )
        .drop(columns="observaciones_mediana")
    )
    mujeres = separar_sexo(estimaciones, "mujer", "mujeres")
    hombres = separar_sexo(estimaciones, "hombre", "hombres")
    return (
        mujeres.merge(
            hombres,
            on=["gestion", *DIMENSIONES],
            how="outer",
            validate="one_to_one",
        )
        .assign(
            brecha_media=lambda d: 100 * (1 - d["media_mujeres"] / d["media_hombres"]),
            error_media=lambda d: 100
            * np.sqrt(
                (d["media_mujeres"] * d["cv_media_mujeres"] / d["media_hombres"]) ** 2
                + (
                    d["media_mujeres"]
                    * d["media_hombres"]
                    * d["cv_media_hombres"]
                    / d["media_hombres"] ** 2
                )
                ** 2
            ),
            cv_brecha_media=lambda d: d["error_media"]
            .div(d["brecha_media"].abs())
            .where(d["brecha_media"].ne(0)),
            brecha_mediana=lambda d: 100
            * (1 - d["mediana_mujeres"] / d["mediana_hombres"]),
            error_mediana=lambda d: 100
            * np.sqrt(
                (d["mediana_mujeres"] * d["cv_mediana_mujeres"] / d["mediana_hombres"])
                ** 2
                + (
                    d["mediana_mujeres"]
                    * d["mediana_hombres"]
                    * d["cv_mediana_hombres"]
                    / d["mediana_hombres"] ** 2
                )
                ** 2
            ),
            cv_brecha_mediana=lambda d: d["error_mediana"]
            .div(d["brecha_mediana"].abs())
            .where(d["brecha_mediana"].ne(0)),
        )
        .loc[:, COLUMNAS_RESULTADO]
    )


def main() -> None:
    validar_ficha(FICHA_PATH)
    escribir_resultados(
        calcular(),
        RESULTADOS_PATH,
        columnas=COLUMNAS_RESULTADO,
        ordenar_por=DIMENSIONES,
    )


if __name__ == "__main__":
    main()
