"""Produce la población de 16 a 28 años por municipio, área, edad y sexo."""

from pathlib import Path

import pandas as pd

from comun import (
    cargar_configuracion,
    escribir_resultados,
    ruta_fuente,
    validar_codigos_municipales,
    validar_ficha,
)


# Definiciones del indicador
EDAD_MINIMA = 16
EDAD_MAXIMA = 28
GESTION = 2024

MAPA_AREA = {1: "urbana", 2: "rural"}
MAPA_SEXO = {1: "mujer", 2: "hombre"}

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"

COLUMNAS_RESULTADO = [
    "gestion",
    "codigo_municipio",
    "area",
    "edad",
    "sexo",
    "valor",
]


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


def calcular() -> pd.DataFrame:
    """Lee el censo y devuelve la tabla final del indicador."""

    configuracion = cargar_configuracion()
    personas_path = ruta_fuente(configuracion, "cpv2024", "persona.parquet")
    viviendas_path = ruta_fuente(configuracion, "cpv2024", "vivienda.parquet")

    # 1. Define los municipios y áreas presentes en la tabla de viviendas.
    viviendas = pd.read_parquet(
        viviendas_path,
        columns=["i00", "idep", "iprov", "imun", "urbrur"],
    )

    territorios = (
        viviendas.loc[
            lambda datos: datos["urbrur"].isin(MAPA_AREA),
            ["idep", "iprov", "imun", "urbrur"],
        ]
        .assign(
            codigo_municipio=formar_codigo_municipio,
            area=lambda datos: datos["urbrur"].map(MAPA_AREA),
        )
        .loc[:, ["codigo_municipio", "area"]]
        .drop_duplicates()
    )

    # 2. Selecciona a jóvenes, incorpora su área y armoniza las variables.
    jovenes = (
        pd.read_parquet(
            personas_path,
            columns=["i00", "idep", "iprov", "imun", "p26_edad", "p25_sexo"],
        )
        .loc[lambda datos: datos["p26_edad"].between(EDAD_MINIMA, EDAD_MAXIMA)]
        .assign(i00=lambda datos: pd.to_numeric(datos["i00"]).astype("int64"))
        .merge(
            viviendas[["i00", "urbrur"]],
            on="i00",
            how="inner",
            validate="many_to_one",
        )
        .assign(
            codigo_municipio=formar_codigo_municipio,
            area=lambda datos: datos["urbrur"].map(MAPA_AREA),
            sexo=lambda datos: datos["p25_sexo"].map(MAPA_SEXO),
        )
        .rename(columns={"p26_edad": "edad"})
    )

    # 3. Cuenta una persona por fila para cada combinación de dimensiones.
    dimensiones = ["codigo_municipio", "area", "edad", "sexo"]
    conteos = (
        jovenes.groupby(dimensiones, as_index=False)
        .size()
        .rename(columns={"size": "valor"})
    )

    # 4. Completa el universo de combinaciones y asigna cero donde no hay casos.
    resultados = (
        territorios.merge(
            pd.DataFrame({"edad": range(EDAD_MINIMA, EDAD_MAXIMA + 1)}),
            how="cross",
        )
        .merge(pd.DataFrame({"sexo": list(MAPA_SEXO.values())}), how="cross")
        .merge(conteos, on=dimensiones, how="left")
        .assign(
            gestion=GESTION,
            valor=lambda datos: datos["valor"].fillna(0).astype("int64"),
        )
        .loc[:, COLUMNAS_RESULTADO]
    )

    # 5. Valida los códigos y conserva las columnas acordadas.
    validar_codigos_municipales(resultados, "codigo_municipio")
    return resultados


def main() -> None:
    validar_ficha(FICHA_PATH)
    resultados = calcular()

    escribir_resultados(
        resultados,
        RESULTADOS_PATH,
        columnas=COLUMNAS_RESULTADO,
        ordenar_por=["codigo_municipio", "area", "edad", "sexo"],
    )
    print(f"I001: {len(resultados):,} filas escritas en {RESULTADOS_PATH}")


if __name__ == "__main__":
    main()
