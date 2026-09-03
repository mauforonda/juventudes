"""Calcula la sensación de seguridad al caminar de noche."""

from pathlib import Path
from comun import escribir_resultados, validar_ficha
from eh import DIMENSIONES_JOVENES, GESTION, cargar_discriminacion
from encuestas import estimar_distribucion

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
NIVEL = "nivel_seguridad"
ETIQUETAS = {1: "muy_inseguro", 2: "inseguro", 3: "seguro", 4: "muy_seguro"}
COLUMNAS_RESULTADO = [
    "gestion",
    *DIMENSIONES_JOVENES,
    NIVEL,
    "observaciones",
    "numerador",
    "denominador",
    "valor",
    "cv",
]


def calcular():
    datos = cargar_discriminacion(["s09b_01"]).assign(
        nivel_seguridad=lambda d: d["s09b_01"].map(ETIQUETAS)
    )
    return estimar_distribucion(
        datos, categoria=NIVEL, dimensiones=DIMENSIONES_JOVENES, gestion=GESTION
    )


def main() -> None:
    validar_ficha(FICHA_PATH)
    escribir_resultados(
        calcular(),
        RESULTADOS_PATH,
        columnas=COLUMNAS_RESULTADO,
        ordenar_por=[*DIMENSIONES_JOVENES, NIVEL],
    )


if __name__ == "__main__":
    main()
