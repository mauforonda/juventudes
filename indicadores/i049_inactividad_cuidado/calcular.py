"""Calcula la inactividad juvenil asociada al hogar y los cuidados."""

from pathlib import Path

from comun import escribir_resultados, validar_codigos_municipales, validar_ficha
from cpv import DIMENSIONES_JOVENES, calcular_porcentaje, cargar_personas

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
CONDICION_ACTIVIDAD = "condact_19"
ACTIVIDAD_NO_OCUPADA = "p48_nocu"
COLUMNAS_RESULTADO = [
    "gestion",
    *DIMENSIONES_JOVENES,
    "numerador",
    "denominador",
    "valor",
]


def calcular():
    datos = cargar_personas([CONDICION_ACTIVIDAD, ACTIVIDAD_NO_OCUPADA])
    return calcular_porcentaje(
        datos,
        caso=lambda d: d[ACTIVIDAD_NO_OCUPADA].eq(6),
        valido=lambda d: d[CONDICION_ACTIVIDAD].eq(4),
        dimensiones=DIMENSIONES_JOVENES,
    )


def main() -> None:
    validar_ficha(FICHA_PATH)
    resultados = calcular()
    validar_codigos_municipales(resultados, "codigo_municipio")
    escribir_resultados(
        resultados,
        RESULTADOS_PATH,
        columnas=COLUMNAS_RESULTADO,
        ordenar_por=DIMENSIONES_JOVENES,
    )


if __name__ == "__main__":
    main()
