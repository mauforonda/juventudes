"""Calcula la confianza declarada en la Policía Boliviana."""

from pathlib import Path
from comun import escribir_resultados, validar_ficha
from eh import DIMENSIONES_JOVENES, GESTION, cargar_discriminacion
from encuestas import estimar_distribucion

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
NIVEL = "nivel_confianza"
ETIQUETAS = {
    1: "mucha_confianza",
    2: "algo_confianza",
    3: "algo_desconfianza",
    4: "mucha_desconfianza",
}
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
    datos = cargar_discriminacion(["s09b_04"]).assign(
        nivel_confianza=lambda d: d["s09b_04"].map(ETIQUETAS)
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
