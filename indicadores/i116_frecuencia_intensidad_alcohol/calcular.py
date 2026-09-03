"""Calcula la frecuencia e intensidad del consumo de alcohol."""

from pathlib import Path
from comun import escribir_resultados, validar_ficha
from edsa import DIMENSIONES_JOVENES, GESTION, cargar_individuales
from encuestas import estimar_distribucion, estimar_media

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
CONSUMO = "consumo"
FRECUENCIA_ORIGINAL = "frecuencia_original"
VASOS = "vasos"
FRECUENCIA = "frecuencia"
MAPA_FRECUENCIA = {1: "diariamente", 2: "un_dia_por_semana", 3: "a_veces"}
COLUMNAS_RESULTADO = [
    "gestion",
    *DIMENSIONES_JOVENES,
    FRECUENCIA,
    "observaciones",
    "numerador",
    "denominador",
    "valor",
    "cv",
    "vasos_promedio",
    "cv_vasos",
]


def calcular():
    datos = (
        cargar_individuales(
            {
                CONSUMO: "ms10_1026",
                FRECUENCIA_ORIGINAL: "ms10_1027_01",
                VASOS: "ms10_1027_02",
            },
            {
                CONSUMO: "vs01_0137",
                FRECUENCIA_ORIGINAL: "vs01_0138",
                VASOS: "vs01_0138_01",
            },
        )
        .loc[lambda d: d[CONSUMO].eq(1) & d[FRECUENCIA_ORIGINAL].isin(MAPA_FRECUENCIA)]
        .assign(frecuencia=lambda d: d[FRECUENCIA_ORIGINAL].map(MAPA_FRECUENCIA))
    )
    distribucion = estimar_distribucion(
        datos, categoria=FRECUENCIA, dimensiones=DIMENSIONES_JOVENES, gestion=GESTION
    )
    intensidad = estimar_media(
        datos.loc[lambda d: d[VASOS].gt(0)],
        variable=VASOS,
        dimensiones=[*DIMENSIONES_JOVENES, FRECUENCIA],
        gestion=GESTION,
    ).rename(columns={"valor": "vasos_promedio", "cv": "cv_vasos"})
    return distribucion.merge(
        intensidad.drop(columns="observaciones"),
        on=["gestion", *DIMENSIONES_JOVENES, FRECUENCIA],
        how="left",
        validate="one_to_one",
    ).loc[:, COLUMNAS_RESULTADO]


def main() -> None:
    validar_ficha(FICHA_PATH)
    escribir_resultados(
        calcular(),
        RESULTADOS_PATH,
        columnas=COLUMNAS_RESULTADO,
        ordenar_por=[*DIMENSIONES_JOVENES, FRECUENCIA],
    )


if __name__ == "__main__":
    main()
