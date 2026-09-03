"""Calcula la violencia física de pareja en los últimos 12 meses."""

from pathlib import Path
from comun import escribir_resultados, validar_ficha
from edsa import DIMENSIONES_JOVENES, GESTION, cargar_individuales
from encuestas import estimar_porcentaje

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
ACTOS = [f"acto_{letra}" for letra in "ABCDEF"]
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
    datos = cargar_individuales(
        {f"acto_{letra}": f"ms11_1108_{letra}" for letra in "ABCDEF"},
        {f"acto_{letra}": f"vs08_0808_{letra}" for letra in "ABCDEF"},
    )
    return estimar_porcentaje(
        datos,
        caso=lambda d: d[ACTOS].isin([1, 2, 3]).any(axis=1),
        valido=lambda d: d[ACTOS].isin([1, 2, 3, 4]).all(axis=1),
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
