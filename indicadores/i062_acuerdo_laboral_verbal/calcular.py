"""Calcula el acuerdo laboral verbal entre jóvenes asalariados."""

from pathlib import Path
from comun import escribir_resultados, validar_ficha
from ece import DIMENSIONES_JOVENES
from empleo_ece import calcular_porcentaje_asalariados

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
CONTRATO = "s2_21"
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
    return calcular_porcentaje_asalariados(
        CONTRATO,
        caso=lambda d: d[CONTRATO].eq(3),
        valido=lambda d: d[CONTRATO].isin(range(1, 6)),
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
