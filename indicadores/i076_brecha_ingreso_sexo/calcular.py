"""Calcula la brecha del ingreso laboral por hora entre mujeres y hombres."""

from pathlib import Path
import numpy as np
from comun import escribir_resultados, validar_ficha
from ece import GESTION, cargar_personas
from encuestas import estimar_mediana

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
    "mediana_mujeres",
    "mediana_hombres",
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
    medianas = estimar_mediana(
        datos,
        variable=INGRESO_HORA,
        dimensiones=[*DIMENSIONES, "sexo"],
        gestion=GESTION,
    )
    mujeres = medianas.loc[lambda d: d["sexo"].eq("mujer")].rename(
        columns={
            "observaciones": "observaciones_mujeres",
            "valor": "mediana_mujeres",
            "cv": "cv_mujeres",
        }
    )
    hombres = medianas.loc[lambda d: d["sexo"].eq("hombre")].rename(
        columns={
            "observaciones": "observaciones_hombres",
            "valor": "mediana_hombres",
            "cv": "cv_hombres",
        }
    )
    return (
        mujeres.merge(hombres, on=["gestion", *DIMENSIONES], validate="one_to_one")
        .assign(
            valor=lambda d: 100 * (1 - d["mediana_mujeres"] / d["mediana_hombres"]),
            error=lambda d: 100
            * np.sqrt(
                (d["mediana_mujeres"] * d["cv_mujeres"] / d["mediana_hombres"]) ** 2
                + (
                    d["mediana_mujeres"]
                    * d["mediana_hombres"]
                    * d["cv_hombres"]
                    / d["mediana_hombres"] ** 2
                )
                ** 2
            ),
            cv=lambda d: d["error"].div(d["valor"].abs()).where(d["valor"].ne(0)),
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
