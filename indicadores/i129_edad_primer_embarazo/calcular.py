"""Calcula la distribución de la edad al primer embarazo."""

from pathlib import Path
from comun import escribir_resultados, validar_ficha
from edsa import DIMENSIONES_JOVENES, GESTION, cargar_mujeres
from encuestas import estimar_distribucion

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
EDAD_PRIMER_EMBARAZO = "edad_primer_embarazo"
COLUMNAS_RESULTADO = [
    "gestion",
    *DIMENSIONES_JOVENES,
    EDAD_PRIMER_EMBARAZO,
    "observaciones",
    "numerador",
    "denominador",
    "valor",
    "cv",
]


def calcular():
    datos = cargar_mujeres({EDAD_PRIMER_EMBARAZO: "ms02_0238"}).loc[
        lambda d: d[EDAD_PRIMER_EMBARAZO].between(10, d["edad"])
    ]
    return estimar_distribucion(
        datos,
        categoria=EDAD_PRIMER_EMBARAZO,
        dimensiones=DIMENSIONES_JOVENES,
        gestion=GESTION,
    )


def main() -> None:
    validar_ficha(FICHA_PATH)
    escribir_resultados(
        calcular(),
        RESULTADOS_PATH,
        columnas=COLUMNAS_RESULTADO,
        ordenar_por=[*DIMENSIONES_JOVENES, EDAD_PRIMER_EMBARAZO],
    )


if __name__ == "__main__":
    main()
