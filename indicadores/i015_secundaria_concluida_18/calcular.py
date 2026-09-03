"""Calcula la conclusión de secundaria a los 18 años."""

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


def concluyo_secundaria(datos):
    return (
        (datos[NIVEL].eq(6) & datos[CURSO].ge(4))
        | (datos[NIVEL].eq(8) & datos[CURSO].ge(6))
        | datos[NIVEL].between(9, 13)
    )


def calcular():
    datos = cargar_personas([NIVEL, CURSO]).loc[lambda d: d["edad"].eq(18)]
    return calcular_porcentaje(
        datos,
        caso=concluyo_secundaria,
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
