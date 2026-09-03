"""Lectura y armonización común para la ECE del cuarto trimestre de 2025."""

from collections.abc import Iterable

import pandas as pd

from comun import cargar_configuracion, ruta_fuente


GESTION = 2025
MAPA_AREA = {1: "urbana", 2: "rural"}
MAPA_SEXO = {1: "hombre", 2: "mujer"}
DIMENSIONES_JOVENES = ["codigo_departamento", "area", "edad", "sexo"]


def cargar_personas(columnas: Iterable[str] = ()) -> pd.DataFrame:
    """Lee jóvenes de la ECE y armoniza territorio, edad, sexo y diseño."""

    configuracion = cargar_configuracion()
    ruta = ruta_fuente(configuracion, "ece_4t2025", "ECE_4T2025.parquet")
    columnas_base = [
        "depto",
        "area",
        "s1_02",
        "s1_03a",
        "fact_trim_act",
        "estrato",
        "upm",
    ]
    return (
        pd.read_parquet(
            ruta,
            columns=list(dict.fromkeys([*columnas_base, *columnas])),
        )
        .loc[lambda datos: datos["s1_03a"].between(16, 28)]
        .assign(
            codigo_departamento=lambda datos: datos["depto"]
            .astype("int64")
            .astype("string"),
            area=lambda datos: datos["area"].map(MAPA_AREA),
            edad=lambda datos: datos["s1_03a"],
            sexo=lambda datos: datos["s1_02"].map(MAPA_SEXO),
            factor=lambda datos: datos["fact_trim_act"],
            estrato=lambda datos: datos["estrato"].astype("string"),
            upm=lambda datos: datos["upm"].astype("string"),
        )
    )


def convertir_a_meses(cantidad: pd.Series, unidad: pd.Series) -> pd.Series:
    """Convierte semanas, meses y años a una duración común en meses."""

    return (
        cantidad.where(unidad.eq(4))
        .fillna(cantidad.where(unidad.eq(2)).div(52 / 12))
        .fillna(cantidad.where(unidad.eq(8)).mul(12))
    )


def clasificar_duracion(meses: pd.Series) -> pd.Series:
    """Agrupa una duración mensual en cinco tramos legibles."""

    return pd.cut(
        meses,
        bins=[0, 1, 3, 6, 12, float("inf")],
        labels=[
            "hasta_1_mes",
            "mas_1_hasta_3_meses",
            "mas_3_hasta_6_meses",
            "mas_6_hasta_12_meses",
            "mas_de_12_meses",
        ],
        include_lowest=True,
    ).astype("string")
