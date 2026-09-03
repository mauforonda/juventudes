"""Calcula el sobrepeso u obesidad entre jóvenes."""

from pathlib import Path
import numpy as np
from comun import escribir_resultados, validar_ficha
from edsa import DIMENSIONES_JOVENES, GESTION, cargar_antropometria
from encuestas import estimar_porcentaje

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
CATEGORIA_MUJER = "categaimc_m"
CATEGORIA_HOMBRE = "categaimc_h"
PESO_MUJER = "ponderador_mpt"
PESO_HOMBRE = "ponderador_vpt"
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
    datos = cargar_antropometria(
        [CATEGORIA_MUJER, CATEGORIA_HOMBRE, PESO_MUJER, PESO_HOMBRE]
    ).assign(
        categoria_imc=lambda d: np.where(
            d["sexo"].eq("mujer"), d[CATEGORIA_MUJER], d[CATEGORIA_HOMBRE]
        ),
        factor=lambda d: np.where(d["sexo"].eq("mujer"), d[PESO_MUJER], d[PESO_HOMBRE]),
    )
    return estimar_porcentaje(
        datos,
        caso=lambda d: d["categoria_imc"].eq(2),
        valido=lambda d: d["categoria_imc"].isin([1, 2, 3]) & d["factor"].notna(),
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
