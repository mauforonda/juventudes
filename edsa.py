"""Lectura y armonización común para la EDSA 2023."""

from collections.abc import Iterable
import pandas as pd
from comun import cargar_configuracion, ruta_fuente

GESTION = 2023
MAPA_AREA = {1: "urbana", 2: "rural"}
MAPA_SEXO = {1: "hombre", 2: "mujer"}
DIMENSIONES_JOVENES = ["codigo_departamento", "area", "edad", "sexo"]


def cargar_hogar(columnas: Iterable[str] = ()) -> pd.DataFrame:
    """Lee jóvenes del cuestionario de hogar y armoniza sus dimensiones."""

    configuracion = cargar_configuracion()
    ruta = ruta_fuente(configuracion, "edsa2023", "EDSA2023_Hogar.parquet")
    columnas_base = [
        "departamento",
        "area",
        "hs01_0003",
        "hs01_0004a",
        "factorexph",
        "estrato",
        "upm",
    ]
    return (
        pd.read_parquet(ruta, columns=list(dict.fromkeys([*columnas_base, *columnas])))
        .loc[lambda d: d["hs01_0004a"].between(16, 28)]
        .assign(
            codigo_departamento=lambda d: d["departamento"]
            .astype("int64")
            .astype("string"),
            area=lambda d: d["area"].map(MAPA_AREA),
            edad=lambda d: d["hs01_0004a"],
            sexo=lambda d: d["hs01_0003"].map(MAPA_SEXO),
            factor=lambda d: d["factorexph"],
            estrato=lambda d: d["estrato"].astype("string"),
            upm=lambda d: d["upm"].astype("string"),
        )
    )


def _cargar_individual(
    archivo: str,
    *,
    edad_original: str,
    peso_original: str,
    sexo: str,
    columnas: dict[str, str],
) -> pd.DataFrame:
    """Lee un cuestionario individual y armoniza nombres y dimensiones."""

    configuracion = cargar_configuracion()
    ruta = ruta_fuente(configuracion, "edsa2023", archivo)
    originales = list(columnas.values())
    return (
        pd.read_parquet(
            ruta,
            columns=list(
                dict.fromkeys(
                    [
                        "departamento",
                        "area",
                        edad_original,
                        peso_original,
                        "estrato",
                        "upm",
                        *originales,
                    ]
                )
            ),
        )
        .rename(columns={origen: destino for destino, origen in columnas.items()})
        .loc[lambda d: d[edad_original].between(16, 28)]
        .assign(
            codigo_departamento=lambda d: d["departamento"]
            .astype("int64")
            .astype("string"),
            area=lambda d: d["area"].map(MAPA_AREA),
            edad=lambda d: d[edad_original].astype("int64"),
            sexo=sexo,
            factor=lambda d: d[peso_original],
            estrato=lambda d: d["estrato"].astype("string"),
            upm=lambda d: d["upm"].astype("string"),
        )
    )


def cargar_individuales(
    columnas_mujer: dict[str, str], columnas_hombre: dict[str, str]
) -> pd.DataFrame:
    """Une cuestionarios de mujeres y hombres con variables armonizadas."""

    mujeres = _cargar_individual(
        "EDSA2023_Mujer.parquet",
        edad_original="ms01_0101a",
        peso_original="ponderadorm",
        sexo="mujer",
        columnas=columnas_mujer,
    )
    hombres = _cargar_individual(
        "EDSA2023_Hombre.parquet",
        edad_original="vs01_0101a",
        peso_original="ponderadorh",
        sexo="hombre",
        columnas=columnas_hombre,
    )
    comunes = [
        "codigo_departamento",
        "area",
        "edad",
        "sexo",
        "factor",
        "estrato",
        "upm",
        *columnas_mujer,
    ]
    return pd.concat([mujeres[comunes], hombres[comunes]], ignore_index=True)


def cargar_mujeres(columnas: dict[str, str]) -> pd.DataFrame:
    """Lee el cuestionario individual de mujeres jóvenes."""

    return _cargar_individual(
        "EDSA2023_Mujer.parquet",
        edad_original="ms01_0101a",
        peso_original="ponderadorm",
        sexo="mujer",
        columnas=columnas,
    )


def cargar_hombres(columnas: dict[str, str]) -> pd.DataFrame:
    """Lee el cuestionario individual de hombres jóvenes."""

    return _cargar_individual(
        "EDSA2023_Hombre.parquet",
        edad_original="vs01_0101a",
        peso_original="ponderadorh",
        sexo="hombre",
        columnas=columnas,
    )


def cargar_antropometria(columnas: Iterable[str] = ()) -> pd.DataFrame:
    """Une mediciones de peso, talla y hemoglobina con datos personales."""

    configuracion = cargar_configuracion()
    mediciones = pd.read_parquet(
        ruta_fuente(configuracion, "edsa2023", "EDSA2023_Peso_talla_hemo.parquet"),
        columns=list(dict.fromkeys(["folio", "nro", "estrato", "upm", *columnas])),
    )
    personas = pd.read_parquet(
        ruta_fuente(configuracion, "edsa2023", "EDSA2023_Hogar.parquet"),
        columns=["folio", "nro", "departamento", "area", "hs01_0003", "hs01_0004a"],
    )
    return (
        mediciones.merge(
            personas, on=["folio", "nro"], how="inner", validate="one_to_one"
        )
        .loc[lambda d: d["hs01_0004a"].between(16, 28)]
        .assign(
            codigo_departamento=lambda d: d["departamento"]
            .astype("int64")
            .astype("string"),
            area=lambda d: d["area"].map(MAPA_AREA),
            edad=lambda d: d["hs01_0004a"].astype("int64"),
            sexo=lambda d: d["hs01_0003"].map(MAPA_SEXO),
            estrato=lambda d: d["estrato"].astype("string"),
            upm=lambda d: d["upm"].astype("string"),
        )
    )
