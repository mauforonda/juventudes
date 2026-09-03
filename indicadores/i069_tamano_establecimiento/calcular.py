"""Calcula la distribución de jóvenes por tamaño del establecimiento."""

from pathlib import Path
from comun import escribir_resultados, validar_ficha
from ece import DIMENSIONES_JOVENES
from empleo_ece import calcular_distribucion_ocupados

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
VARIABLE = "s2_26a"
CATEGORIA = "tamano_establecimiento"
MAPA_TAMANO = {
    1: "1_persona",
    2: "2_a_5",
    3: "6_a_10",
    4: "11_a_20",
    5: "21_a_30",
    6: "31_a_50",
    7: "51_a_100",
    8: "101_o_mas",
}
COLUMNAS_RESULTADO = [
    "gestion",
    *DIMENSIONES_JOVENES,
    CATEGORIA,
    "observaciones",
    "numerador",
    "denominador",
    "valor",
    "cv",
]


def calcular():
    return calcular_distribucion_ocupados(VARIABLE, CATEGORIA, MAPA_TAMANO)


def main() -> None:
    validar_ficha(FICHA_PATH)
    escribir_resultados(
        calcular(),
        RESULTADOS_PATH,
        columnas=COLUMNAS_RESULTADO,
        ordenar_por=[*DIMENSIONES_JOVENES, CATEGORIA],
    )


if __name__ == "__main__":
    main()
