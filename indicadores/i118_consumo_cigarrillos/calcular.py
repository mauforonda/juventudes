"""Calcula la frecuencia e intensidad del consumo de cigarrillos."""

from pathlib import Path
from comun import escribir_resultados, validar_ficha
from edsa import DIMENSIONES_JOVENES, GESTION, cargar_individuales
from encuestas import estimar_distribucion, estimar_media

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
CONSUMO = "consumo"
FRECUENCIA_ORIGINAL = "frecuencia_original"
CANTIDAD = "cigarrillos"
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
    "cigarrillos_promedio",
    "cv_cigarrillos",
]


def calcular():
    datos = (
        cargar_individuales(
            {
                CONSUMO: "ms10_1030",
                FRECUENCIA_ORIGINAL: "ms10_1031_01",
                CANTIDAD: "ms10_1031_02",
            },
            {
                CONSUMO: "vs01_0141",
                FRECUENCIA_ORIGINAL: "vs01_0142_01",
                CANTIDAD: "vs01_0142_02",
            },
        )
        .loc[lambda d: d[CONSUMO].isin([1, 2])]
        .assign(
            frecuencia=lambda d: d[FRECUENCIA_ORIGINAL]
            .map(MAPA_FRECUENCIA)
            .where(d[CONSUMO].eq(1), "no_fuma")
            .fillna("frecuencia_no_declarada"),
            cigarrillos=lambda d: d[CANTIDAD].where(d[CONSUMO].eq(1), 0),
        )
    )
    distribucion = estimar_distribucion(
        datos, categoria=FRECUENCIA, dimensiones=DIMENSIONES_JOVENES, gestion=GESTION
    )
    intensidad = estimar_media(
        datos.dropna(subset=[CANTIDAD]),
        variable=CANTIDAD,
        dimensiones=[*DIMENSIONES_JOVENES, FRECUENCIA],
        gestion=GESTION,
    ).rename(columns={"valor": "cigarrillos_promedio", "cv": "cv_cigarrillos"})
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
