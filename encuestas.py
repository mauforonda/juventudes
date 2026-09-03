"""Estimaciones comunes para encuestas con diseño muestral complejo."""

from collections.abc import Callable, Iterable
from math import sqrt

import pandas as pd


def _varianza_proporcion(
    grupo: pd.DataFrame,
    diseno: pd.DataFrame,
    proporcion: float,
    denominador: float,
    *,
    peso: str,
    estrato: str,
    upm: str,
) -> float:
    """Calcula la varianza de una proporción mediante linealización de Taylor."""

    totales_upm = (
        grupo.assign(lineal=lambda datos: datos[peso] * (datos["es_caso"] - proporcion))
        .groupby([estrato, upm], as_index=False)["lineal"]
        .sum()
    )
    lineales = (
        diseno.merge(totales_upm, on=[estrato, upm], how="left")
        .fillna({"lineal": 0})
        .assign(
            upm_estrato=lambda datos: datos.groupby(estrato)[upm].transform("size"),
            media_estrato=lambda datos: datos.groupby(estrato)["lineal"].transform(
                "mean"
            ),
        )
    )
    componentes = lineales.loc[lambda datos: datos["upm_estrato"].gt(1)].assign(
        componente=lambda datos: datos["upm_estrato"]
        / (datos["upm_estrato"] - 1)
        * (datos["lineal"] - datos["media_estrato"]) ** 2
    )
    return componentes["componente"].sum() / denominador**2


def estimar_porcentaje(
    datos: pd.DataFrame,
    *,
    caso: Callable[[pd.DataFrame], pd.Series],
    dimensiones: Iterable[str],
    valido: Callable[[pd.DataFrame], pd.Series] | None = None,
    peso: str = "factor",
    estrato: str = "estrato",
    upm: str = "upm",
    gestion: int,
) -> pd.DataFrame:
    """Estima porcentajes y CV para cada combinación de dimensiones."""

    dimensiones = list(dimensiones)
    diseno = datos[[estrato, upm]].drop_duplicates()
    base = (datos.loc[valido(datos)] if valido else datos).assign(
        es_caso=lambda tabla: caso(tabla).astype("int64")
    )
    filas = []

    for claves, grupo in base.groupby(dimensiones, dropna=False, observed=True):
        claves = claves if isinstance(claves, tuple) else (claves,)
        denominador = grupo[peso].sum()
        numerador = grupo.loc[grupo["es_caso"].eq(1), peso].sum()
        proporcion = numerador / denominador
        varianza = _varianza_proporcion(
            grupo,
            diseno,
            proporcion,
            denominador,
            peso=peso,
            estrato=estrato,
            upm=upm,
        )
        filas.append(
            {
                "gestion": gestion,
                **dict(zip(dimensiones, claves)),
                "observaciones": len(grupo),
                "numerador": numerador,
                "denominador": denominador,
                "valor": 100 * proporcion,
                "cv": sqrt(varianza) / proporcion if proporcion > 0 else pd.NA,
            }
        )

    return pd.DataFrame(filas)


def estimar_distribucion(
    datos: pd.DataFrame,
    *,
    categoria: str,
    dimensiones: Iterable[str],
    gestion: int,
) -> pd.DataFrame:
    """Estima la distribución porcentual de una variable categórica."""

    base = datos.dropna(subset=[categoria])
    resultados = [
        estimar_porcentaje(
            base,
            caso=lambda tabla, valor=valor: tabla[categoria].eq(valor),
            dimensiones=dimensiones,
            gestion=gestion,
        ).assign(**{categoria: valor})
        for valor in sorted(base[categoria].unique())
    ]
    columnas = [
        "gestion",
        *dimensiones,
        categoria,
        "observaciones",
        "numerador",
        "denominador",
        "valor",
        "cv",
    ]
    return pd.concat(resultados, ignore_index=True).loc[:, columnas]


def cuantila_ponderada(
    valores: pd.Series, pesos: pd.Series, probabilidad: float
) -> float:
    """Calcula una cuantila a partir de la distribución ponderada."""

    orden = valores.argsort()
    valores_ordenados = valores.iloc[orden].reset_index(drop=True)
    pesos_ordenados = pesos.iloc[orden].reset_index(drop=True)
    posicion = pesos_ordenados.cumsum().ge(probabilidad * pesos_ordenados.sum())
    return valores_ordenados.loc[posicion.idxmax()]


def estimar_media(
    datos: pd.DataFrame,
    *,
    variable: str,
    dimensiones: Iterable[str],
    gestion: int,
    peso: str = "factor",
    estrato: str = "estrato",
    upm: str = "upm",
) -> pd.DataFrame:
    """Estima medias y CV mediante linealización de Taylor."""

    dimensiones = list(dimensiones)
    diseno = datos[[estrato, upm]].drop_duplicates()
    filas = []
    for claves, grupo in datos.dropna(subset=[variable]).groupby(
        dimensiones, dropna=False, observed=True
    ):
        claves = claves if isinstance(claves, tuple) else (claves,)
        denominador = grupo[peso].sum()
        media = (grupo[variable] * grupo[peso]).sum() / denominador
        varianza = _varianza_proporcion(
            grupo.assign(es_caso=lambda d: d[variable]),
            diseno,
            media,
            denominador,
            peso=peso,
            estrato=estrato,
            upm=upm,
        )
        filas.append(
            {
                "gestion": gestion,
                **dict(zip(dimensiones, claves)),
                "observaciones": len(grupo),
                "valor": media,
                "cv": sqrt(varianza) / abs(media) if media else pd.NA,
            }
        )
    return pd.DataFrame(filas)


def estimar_mediana(
    datos: pd.DataFrame,
    *,
    variable: str,
    dimensiones: Iterable[str],
    gestion: int,
    peso: str = "factor",
    estrato: str = "estrato",
    upm: str = "upm",
) -> pd.DataFrame:
    """Estima medianas y CV con la varianza de su distribución acumulada."""

    dimensiones = list(dimensiones)
    diseno = datos[[estrato, upm]].drop_duplicates()
    filas = []
    for claves, grupo in datos.dropna(subset=[variable]).groupby(
        dimensiones, dropna=False, observed=True
    ):
        claves = claves if isinstance(claves, tuple) else (claves,)
        denominador = grupo[peso].sum()
        mediana = cuantila_ponderada(grupo[variable], grupo[peso], 0.5)
        inferior = cuantila_ponderada(grupo[variable], grupo[peso], 0.25)
        superior = cuantila_ponderada(grupo[variable], grupo[peso], 0.75)
        proporcion = grupo.loc[grupo[variable].le(mediana), peso].sum() / denominador
        varianza_acumulada = _varianza_proporcion(
            grupo.assign(es_caso=lambda d: d[variable].le(mediana).astype("int64")),
            diseno,
            proporcion,
            denominador,
            peso=peso,
            estrato=estrato,
            upm=upm,
        )
        densidad = 0.5 / (superior - inferior) if superior > inferior else None
        error = sqrt(varianza_acumulada) / densidad if densidad else 0
        filas.append(
            {
                "gestion": gestion,
                **dict(zip(dimensiones, claves)),
                "observaciones": len(grupo),
                "valor": mediana,
                "cv": error / abs(mediana) if mediana else pd.NA,
            }
        )
    return pd.DataFrame(filas)


def estimar_respuestas_multiples(
    datos: pd.DataFrame,
    *,
    categorias: dict[str, Iterable[str]],
    categoria: str,
    dimensiones: Iterable[str],
    gestion: int,
    valido: Callable[[pd.DataFrame], pd.Series],
) -> pd.DataFrame:
    """Estima el porcentaje que marcó cada categoría de respuesta múltiple."""

    resultados = [
        estimar_porcentaje(
            datos,
            caso=lambda d, variables=list(variables): d[variables].eq(1).any(axis=1),
            valido=valido,
            dimensiones=dimensiones,
            gestion=gestion,
        ).assign(**{categoria: etiqueta})
        for etiqueta, variables in categorias.items()
    ]
    columnas = [
        "gestion",
        *dimensiones,
        categoria,
        "observaciones",
        "numerador",
        "denominador",
        "valor",
        "cv",
    ]
    return pd.concat(resultados, ignore_index=True).loc[:, columnas]
