"""Definiciones comunes de educación y trabajo en el CPV 2024."""

from collections.abc import Callable

import pandas as pd

from cpv import DIMENSIONES_JOVENES, calcular_porcentaje, cargar_personas


ASISTENCIA = "asiste"
CONDICION_ACTIVIDAD = "condact_19"
RESPUESTAS_VALIDAS = [1, 2, 3, 4]


def cargar_base() -> pd.DataFrame:
    """Lee las variables comunes de asistencia y condición de actividad."""

    return cargar_personas([ASISTENCIA, CONDICION_ACTIVIDAD])


def calcular(
    caso: Callable[[pd.DataFrame], pd.Series],
    *,
    valido: Callable[[pd.DataFrame], pd.Series] | None = None,
) -> pd.DataFrame:
    """Calcula un porcentaje sobre respuestas educativas y laborales válidas."""

    return calcular_porcentaje(
        cargar_base(),
        caso=caso,
        valido=valido
        or (
            lambda datos: datos[ASISTENCIA].isin([1, 2])
            & datos[CONDICION_ACTIVIDAD].isin(RESPUESTAS_VALIDAS)
        ),
        dimensiones=DIMENSIONES_JOVENES,
    )
