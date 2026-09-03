"""Calcula la conclusión de educación superior entre jóvenes."""

from pathlib import Path
from comun import escribir_resultados, validar_codigos_municipales, validar_ficha
from cpv import DIMENSIONES_JOVENES, calcular_porcentaje, cargar_personas

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
NIVEL = "p41a_nivel"
CURSO = "p41b_curso"
COLUMNAS_RESULTADO = [
    "gestion",
    *DIMENSIONES_JOVENES,
    "numerador",
    "denominador",
    "valor",
]


def concluyo_superior(datos):
    return (
        (datos[NIVEL].eq(10) & datos[CURSO].ge(3))
        | (datos[NIVEL].eq(11) & datos[CURSO].ge(5))
        | datos[NIVEL].isin([12, 13])
    )


def calcular():
    datos = cargar_personas([NIVEL, CURSO])
    return calcular_porcentaje(
        datos,
        caso=concluyo_superior,
        valido=lambda d: d[NIVEL].between(1, 13) & d[CURSO].ne(9),
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
