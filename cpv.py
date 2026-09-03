"""Lectura y resúmenes comunes para indicadores del CPV 2024."""

from collections.abc import Callable, Iterable

import pandas as pd

from comun import cargar_configuracion, ruta_fuente


EDAD_MINIMA = 16
EDAD_MAXIMA = 28
GESTION = 2024

MAPA_AREA = {1: "urbana", 2: "rural"}
MAPA_SEXO = {1: "mujer", 2: "hombre"}
DIMENSIONES_JOVENES = ["codigo_municipio", "area", "edad", "sexo"]


def formar_codigo_municipio(datos: pd.DataFrame) -> pd.Series:
    """Une departamento, provincia y municipio en un código de cinco dígitos."""

    componentes = (
        datos[["idep", "iprov", "imun"]]
        .apply(pd.to_numeric)
        .astype("int64")
        .astype("string")
    )
    return (
        componentes["idep"]
        + componentes["iprov"].str.zfill(2)
        + componentes["imun"].str.zfill(2)
    )


def cargar_personas(
    columnas: Iterable[str] = (),
    *,
    columnas_vivienda: Iterable[str] = (),
    solo_jovenes: bool = True,
) -> pd.DataFrame:
    """Lee personas del CPV y añade municipio, área, edad y sexo armonizados."""

    columnas = list(dict.fromkeys(columnas))
    columnas_vivienda = list(dict.fromkeys(columnas_vivienda))
    configuracion = cargar_configuracion()
    personas_path = ruta_fuente(configuracion, "cpv2024", "persona.parquet")
    viviendas_path = ruta_fuente(configuracion, "cpv2024", "vivienda.parquet")
    columnas_base = ["i00", "idep", "iprov", "imun", "p26_edad", "p25_sexo"]

    personas = pd.read_parquet(
        personas_path,
        columns=list(dict.fromkeys(columnas_base + columnas)),
    )
    if solo_jovenes:
        personas = personas.loc[
            lambda datos: datos["p26_edad"].between(EDAD_MINIMA, EDAD_MAXIMA)
        ]

    return (
        personas.assign(i00=lambda datos: pd.to_numeric(datos["i00"]))
        .merge(
            pd.read_parquet(
                viviendas_path,
                columns=list(dict.fromkeys(["i00", "urbrur", *columnas_vivienda])),
            ),
            on="i00",
            how="inner",
            validate="many_to_one",
        )
        .assign(
            codigo_municipio=formar_codigo_municipio,
            area=lambda datos: datos["urbrur"].map(MAPA_AREA),
            edad=lambda datos: datos["p26_edad"],
            sexo=lambda datos: datos["p25_sexo"].map(MAPA_SEXO),
        )
    )


def calcular_porcentaje(
    datos: pd.DataFrame,
    *,
    caso: Callable[[pd.DataFrame], pd.Series],
    dimensiones: Iterable[str],
    valido: Callable[[pd.DataFrame], pd.Series] | None = None,
) -> pd.DataFrame:
    """Calcula numerador, denominador y porcentaje para cada grupo."""

    dimensiones = list(dimensiones)
    base = datos.loc[valido(datos)] if valido else datos
    return (
        base.assign(es_caso=lambda tabla: caso(tabla).astype("int64"))
        .groupby(dimensiones, as_index=False, dropna=False)
        .agg(numerador=("es_caso", "sum"), denominador=("es_caso", "size"))
        .assign(
            gestion=GESTION,
            valor=lambda tabla: 100 * tabla["numerador"] / tabla["denominador"],
        )
        .loc[:, ["gestion", *dimensiones, "numerador", "denominador", "valor"]]
    )


def calcular_distribucion(
    datos: pd.DataFrame,
    *,
    categoria: str,
    dimensiones: Iterable[str],
) -> pd.DataFrame:
    """Calcula el número y porcentaje de cada categoría dentro de cada grupo."""

    dimensiones = list(dimensiones)
    return (
        datos.dropna(subset=[categoria])
        .groupby([*dimensiones, categoria], as_index=False, dropna=False)
        .size()
        .rename(columns={"size": "numerador"})
        .assign(
            denominador=lambda tabla: tabla.groupby(dimensiones, dropna=False)[
                "numerador"
            ].transform("sum"),
            gestion=GESTION,
            valor=lambda tabla: 100 * tabla["numerador"] / tabla["denominador"],
        )
        .loc[
            :,
            [
                "gestion",
                *dimensiones,
                categoria,
                "numerador",
                "denominador",
                "valor",
            ],
        ]
    )


def calcular_media(
    datos: pd.DataFrame,
    *,
    variable: str,
    dimensiones: Iterable[str],
) -> pd.DataFrame:
    """Calcula número de observaciones y media para cada grupo."""

    dimensiones = list(dimensiones)
    return (
        datos.dropna(subset=[variable])
        .groupby(dimensiones, as_index=False, dropna=False)
        .agg(observaciones=(variable, "size"), valor=(variable, "mean"))
        .assign(gestion=GESTION)
        .loc[:, ["gestion", *dimensiones, "observaciones", "valor"]]
    )
