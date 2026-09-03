"""Definiciones comunes para indicadores laborales de la ECE 2025."""

from collections.abc import Callable

import pandas as pd

from ece import DIMENSIONES_JOVENES, GESTION, cargar_personas
from encuestas import estimar_distribucion, estimar_porcentaje


CONDICION_ACTIVIDAD = "condact"
CATEGORIA_OCUPACIONAL = "s2_18"


def calcular_porcentaje_ocupados(
    variable: str,
    *,
    caso: Callable[[pd.DataFrame], pd.Series],
    valido: Callable[[pd.DataFrame], pd.Series],
) -> pd.DataFrame:
    """Estima un porcentaje entre jóvenes ocupados con respuesta válida."""

    datos = cargar_personas([CONDICION_ACTIVIDAD, variable])
    return estimar_porcentaje(
        datos,
        caso=caso,
        valido=lambda d: d[CONDICION_ACTIVIDAD].eq(1) & valido(d),
        dimensiones=DIMENSIONES_JOVENES,
        gestion=GESTION,
    )


def calcular_distribucion_ocupados(
    variable: str, categoria: str, mapa: dict
) -> pd.DataFrame:
    """Estima una distribución laboral y reemplaza códigos por etiquetas."""

    datos = (
        cargar_personas([CONDICION_ACTIVIDAD, variable])
        .loc[lambda d: d[CONDICION_ACTIVIDAD].eq(1)]
        .assign(**{categoria: lambda d: d[variable].map(mapa)})
    )
    return estimar_distribucion(
        datos, categoria=categoria, dimensiones=DIMENSIONES_JOVENES, gestion=GESTION
    )


def calcular_porcentaje_asalariados(
    variable: str,
    *,
    caso: Callable[[pd.DataFrame], pd.Series],
    valido: Callable[[pd.DataFrame], pd.Series],
) -> pd.DataFrame:
    """Estima un porcentaje entre asalariados con respuesta válida."""

    datos = cargar_personas([CONDICION_ACTIVIDAD, CATEGORIA_OCUPACIONAL, variable])
    return estimar_porcentaje(
        datos,
        caso=caso,
        valido=lambda d: d[CONDICION_ACTIVIDAD].eq(1)
        & d[CATEGORIA_OCUPACIONAL].isin([1, 7])
        & valido(d),
        dimensiones=DIMENSIONES_JOVENES,
        gestion=GESTION,
    )
