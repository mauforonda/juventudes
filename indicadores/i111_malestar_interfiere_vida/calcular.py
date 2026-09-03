"""Calcula el malestar emocional que interfiere con la vida diaria."""

from pathlib import Path
from comun import escribir_resultados, validar_ficha
from edsa import DIMENSIONES_JOVENES, GESTION, cargar_individuales
from encuestas import estimar_porcentaje

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
RESPUESTAS = [f"interferencia_{letra.lower()}" for letra in "ABCD"]
MAPA_MUJER = dict(zip(RESPUESTAS, [f"ms10_1022_{letra}" for letra in "ABCD"]))
MAPA_HOMBRE = dict(zip(RESPUESTAS, [f"vs01_0133_{letra}" for letra in "ABCD"]))
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
    datos = cargar_individuales(MAPA_MUJER, MAPA_HOMBRE)
    return estimar_porcentaje(
        datos,
        caso=lambda d: d[RESPUESTAS].eq(1).any(axis=1),
        valido=lambda d: d[RESPUESTAS].isin([1, 2]).any(axis=1),
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
