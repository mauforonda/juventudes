"""Calcula la inseguridad alimentaria en hogares con jóvenes."""

from pathlib import Path
from comun import escribir_resultados, validar_ficha
from eh import DIMENSIONES_JOVENES, GESTION, cargar_personas_con_hogar
from encuestas import estimar_porcentaje

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
EXPERIENCIAS = [f"s07a_{numero:02d}" for numero in range(1, 9)]
COLUMNAS_RESULTADO = [
    "gestion",
    *DIMENSIONES_JOVENES,
    "observaciones",
    "numerador",
    "denominador",
    "valor",
    "cv",
]


def calcular():
    datos = cargar_personas_con_hogar(
        "EH2025_Seguridad_Alimentaria.parquet", columnas_hogar=EXPERIENCIAS
    )
    return estimar_porcentaje(
        datos,
        caso=lambda d: d[EXPERIENCIAS].eq(1).any(axis=1),
        valido=lambda d: d[EXPERIENCIAS].isin([1, 2]).all(axis=1),
        dimensiones=DIMENSIONES_JOVENES,
        gestion=GESTION,
    )


def main() -> None:
    validar_ficha(FICHA_PATH)
    escribir_resultados(
        calcular(),
        RESULTADOS_PATH,
        columnas=COLUMNAS_RESULTADO,
        ordenar_por=DIMENSIONES_JOVENES,
    )


if __name__ == "__main__":
    main()
