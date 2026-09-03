"""Calcula la tenencia de vivienda en hogares encabezados por jóvenes."""

from pathlib import Path
from comun import escribir_resultados, validar_codigos_municipales, validar_ficha
from cpv import DIMENSIONES_JOVENES, calcular_distribucion, cargar_personas

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
PARENTESCO = "p24_parentes"
TENENCIA_ORIGINAL = "v17_tenencia"
CATEGORIA = "tenencia_vivienda"
MAPA_TENENCIA = {
    1: "propia_pagada",
    2: "propia_en_pago",
    3: "prestada",
    4: "alquilada",
    5: "anticretica",
    6: "mixta",
    7: "cedida_por_servicios",
    8: "otra",
}
COLUMNAS_RESULTADO = [
    "gestion",
    *DIMENSIONES_JOVENES,
    CATEGORIA,
    "numerador",
    "denominador",
    "valor",
]


def calcular():
    datos = (
        cargar_personas([PARENTESCO], columnas_vivienda=[TENENCIA_ORIGINAL])
        .loc[lambda d: d[PARENTESCO].eq(1)]
        .assign(tenencia_vivienda=lambda d: d[TENENCIA_ORIGINAL].map(MAPA_TENENCIA))
    )
    return calcular_distribucion(
        datos, categoria=CATEGORIA, dimensiones=DIMENSIONES_JOVENES
    )


def main() -> None:
    validar_ficha(FICHA_PATH)
    resultados = calcular()
    validar_codigos_municipales(resultados, "codigo_municipio")
    escribir_resultados(
        resultados,
        RESULTADOS_PATH,
        columnas=COLUMNAS_RESULTADO,
        ordenar_por=[*DIMENSIONES_JOVENES, CATEGORIA],
    )


if __name__ == "__main__":
    main()
