"""Calcula la anemia entre mujeres jóvenes."""

from pathlib import Path
from comun import escribir_resultados, validar_ficha
from edsa import DIMENSIONES_JOVENES, GESTION, cargar_antropometria
from encuestas import estimar_porcentaje

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
ANEMIA = "tip_anemia_m"
PESO = "ponderador_mhm"
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
    datos = (
        cargar_antropometria([ANEMIA, PESO])
        .loc[lambda d: d["sexo"].eq("mujer")]
        .assign(factor=lambda d: d[PESO])
    )
    return estimar_porcentaje(
        datos,
        caso=lambda d: d[ANEMIA].isin([2, 3, 4]),
        valido=lambda d: d[ANEMIA].isin([1, 2, 3, 4]) & d["factor"].notna(),
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
