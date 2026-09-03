"""Lectura y armonización común para la Encuesta de Hogares 2025."""

from collections.abc import Iterable

import pandas as pd

from comun import cargar_configuracion, ruta_fuente


GESTION = 2025
MAPA_AREA = {1: "urbana", 2: "rural"}
MAPA_SEXO = {1: "hombre", 2: "mujer"}
DIMENSIONES_JOVENES = ["codigo_departamento", "area", "edad", "sexo"]
COLUMNAS_DISENO = ["factor", "estrato", "upm"]


def cargar_personas(columnas: Iterable[str] = ()) -> pd.DataFrame:
    """Lee jóvenes de la EH y armoniza territorio, edad, sexo y diseño."""

    configuracion = cargar_configuracion()
    ruta = ruta_fuente(configuracion, "eh2025", "EH2025_Persona.parquet")
    columnas_base = [
        "depto",
        "area",
        "s01a_02",
        "s01a_03",
        *COLUMNAS_DISENO,
    ]
    return (
        pd.read_parquet(
            ruta,
            columns=list(dict.fromkeys([*columnas_base, *columnas])),
        )
        .loc[lambda datos: datos["s01a_03"].between(16, 28)]
        .assign(
            codigo_departamento=lambda datos: datos["depto"]
            .astype("int64")
            .astype("string"),
            area=lambda datos: datos["area"].map(MAPA_AREA),
            edad=lambda datos: datos["s01a_03"],
            sexo=lambda datos: datos["s01a_02"].map(MAPA_SEXO),
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


def cargar_personas_con_hogar(
    archivo_hogar: str,
    *,
    columnas_persona: Iterable[str] = (),
    columnas_hogar: Iterable[str] = (),
) -> pd.DataFrame:
    """Une jóvenes con una tabla de hogar mediante el folio."""

    configuracion = cargar_configuracion()
    personas = cargar_personas(["folio", *columnas_persona])
    hogar = pd.read_parquet(
        ruta_fuente(configuracion, "eh2025", archivo_hogar),
        columns=list(dict.fromkeys(["folio", *columnas_hogar])),
    )
    return personas.merge(hogar, on="folio", how="inner", validate="many_to_one")


def cargar_discriminacion(columnas: Iterable[str] = ()) -> pd.DataFrame:
    """Lee el módulo aplicado a una persona seleccionada de cada hogar."""

    configuracion = cargar_configuracion()
    ruta = ruta_fuente(configuracion, "eh2025", "EH2025_Discriminacion.parquet")
    seleccion = pd.read_parquet(
        ruta,
        columns=list(
            dict.fromkeys(
                [
                    "folio",
                    "nro",
                    "depto",
                    "area",
                    "ponderador",
                    "estrato",
                    "upm",
                    *columnas,
                ]
            )
        ),
    )
    personas = pd.read_parquet(
        ruta_fuente(configuracion, "eh2025", "EH2025_Persona.parquet"),
        columns=["folio", "nro", "s01a_02", "s01a_03"],
    )
    return (
        seleccion.merge(
            personas, on=["folio", "nro"], how="inner", validate="one_to_one"
        )
        .loc[lambda d: d["s01a_03"].between(16, 28)]
        .assign(
            codigo_departamento=lambda d: d["depto"].astype("int64").astype("string"),
            area=lambda d: d["area"].map(MAPA_AREA),
            edad=lambda d: d["s01a_03"].astype("int64"),
            sexo=lambda d: d["s01a_02"].map(MAPA_SEXO),
            factor=lambda d: d["ponderador"],
            estrato=lambda d: d["estrato"].astype("string"),
            upm=lambda d: d["upm"].astype("string"),
        )
    )
