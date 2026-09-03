"""Definiciones comunes para indicadores laborales del CPV 2024."""

from collections.abc import Callable

import pandas as pd

from cpv import (
    DIMENSIONES_JOVENES,
    calcular_distribucion,
    calcular_porcentaje,
    cargar_personas,
)


CONDICION_ACTIVIDAD = "condact_19"
CATEGORIA_OCUPACIONAL = "p50_semp"


def calcular_porcentaje_ocupados(
    variable: str,
    *,
    caso: Callable[[pd.DataFrame], pd.Series],
    valido: Callable[[pd.DataFrame], pd.Series],
) -> pd.DataFrame:
    """Calcula un porcentaje entre jóvenes ocupados con respuesta válida."""

    datos = cargar_personas([CONDICION_ACTIVIDAD, variable])
    return calcular_porcentaje(
        datos,
        caso=caso,
        valido=lambda d: d[CONDICION_ACTIVIDAD].eq(1) & valido(d),
        dimensiones=DIMENSIONES_JOVENES,
    )


def calcular_distribucion_ocupados(
    variable: str, categoria: str, mapa: dict
) -> pd.DataFrame:
    """Calcula una distribución laboral y reemplaza códigos por etiquetas."""

    datos = (
        cargar_personas([CONDICION_ACTIVIDAD, variable])
        .loc[lambda d: d[CONDICION_ACTIVIDAD].eq(1)]
        .assign(**{categoria: lambda d: d[variable].map(mapa)})
    )
    return calcular_distribucion(
        datos, categoria=categoria, dimensiones=DIMENSIONES_JOVENES
    )
