"""Calcula el porcentaje de jóvenes que sólo trabaja."""

from pathlib import Path
from comun import escribir_resultados, validar_codigos_municipales, validar_ficha
from cpv import DIMENSIONES_JOVENES
from transicion_cpv import ASISTENCIA, CONDICION_ACTIVIDAD, calcular

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
COLUMNAS_RESULTADO = [
    "gestion",
    *DIMENSIONES_JOVENES,
    "numerador",
    "denominador",
    "valor",
]


def producir():
    return calcular(lambda d: d[ASISTENCIA].eq(2) & d[CONDICION_ACTIVIDAD].eq(1))


def main() -> None:
    validar_ficha(FICHA_PATH)
    resultados = producir()
    validar_codigos_municipales(resultados, "codigo_municipio")
    escribir_resultados(
        resultados,
        RESULTADOS_PATH,
        columnas=COLUMNAS_RESULTADO,
        ordenar_por=DIMENSIONES_JOVENES,
    )


if __name__ == "__main__":
    main()
