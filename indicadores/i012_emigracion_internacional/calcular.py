"""Cuenta personas que emigraron al exterior cuando tenían de 16 a 28 años."""

from pathlib import Path

import pandas as pd

from comun import (
    cargar_configuracion,
    escribir_resultados,
    ruta_fuente,
    validar_codigos_municipales,
    validar_ficha,
)
from cpv import GESTION, formar_codigo_municipio


BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
MAPA_SEXO = {1: "hombre", 2: "mujer"}
DIMENSIONES = [
    "codigo_municipio",
    "sexo",
    "edad_salida",
    "anio_salida",
    "codigo_pais_destino",
]
COLUMNAS_RESULTADO = ["gestion", *DIMENSIONES, "valor"]


def calcular():
    configuracion = cargar_configuracion()
    emigracion_path = ruta_fuente(configuracion, "cpv2024", "emigracion.parquet")
    return (
        pd.read_parquet(
            emigracion_path,
            columns=[
                "idep",
                "iprov",
                "imun",
                "e203_sexo",
                "e204_ansal",
                "e205_edad",
                "pais_destino_cod",
            ],
        )
        .loc[lambda datos: datos["e205_edad"].between(16, 28)]
        .assign(
            gestion=GESTION,
            codigo_municipio=formar_codigo_municipio,
            sexo=lambda datos: datos["e203_sexo"].map(MAPA_SEXO),
            edad_salida=lambda datos: datos["e205_edad"],
            anio_salida=lambda datos: datos["e204_ansal"],
            codigo_pais_destino=lambda datos: pd.to_numeric(datos["pais_destino_cod"])
            .astype("Int64")
            .astype("string")
            .str.zfill(3),
        )
        .dropna(subset=DIMENSIONES)
        .groupby(["gestion", *DIMENSIONES], as_index=False)
        .size()
        .rename(columns={"size": "valor"})
        .loc[:, COLUMNAS_RESULTADO]
    )


def main() -> None:
    validar_ficha(FICHA_PATH)
    resultados = calcular()
    validar_codigos_municipales(resultados, "codigo_municipio")
    escribir_resultados(
        resultados,
        RESULTADOS_PATH,
        columnas=COLUMNAS_RESULTADO,
        ordenar_por=DIMENSIONES,
    )


if __name__ == "__main__":
    main()
