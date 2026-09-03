"""Calcula el malestar emocional frecuente entre jóvenes."""

from pathlib import Path
from comun import escribir_resultados, validar_ficha
from edsa import DIMENSIONES_JOVENES, GESTION, cargar_individuales
from encuestas import estimar_porcentaje

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
CONTEXTOS = [f"contexto_{letra.lower()}" for letra in "ABCD"]
MAPA_MUJER = dict(zip(CONTEXTOS, [f"ms10_1021_{letra}" for letra in "ABCD"]))
MAPA_HOMBRE = dict(zip(CONTEXTOS, [f"vs01_0132_{letra}" for letra in "ABCD"]))
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
        caso=lambda d: d[CONTEXTOS].eq(1).any(axis=1),
        valido=lambda d: d[CONTEXTOS].isin([1, 2]).all(axis=1),
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
