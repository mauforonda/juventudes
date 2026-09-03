"""Calcula el acceso a internet en los hogares de jóvenes."""

from pathlib import Path
from comun import escribir_resultados, validar_codigos_municipales, validar_ficha
from cpv import DIMENSIONES_JOVENES, calcular_porcentaje, cargar_personas

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
FIJO = "v19e_inetfijo"
MOVIL = "v19f_inetmovil"
COLUMNAS_RESULTADO = [
    "gestion",
    *DIMENSIONES_JOVENES,
    "numerador",
    "denominador",
    "valor",
]


def tiene_internet(datos):
    return datos[FIJO].eq(1) | datos[MOVIL].eq(1)


def respuesta_definida(datos):
    return tiene_internet(datos) | (datos[FIJO].eq(2) & datos[MOVIL].eq(2))


def calcular():
    return calcular_porcentaje(
        cargar_personas(columnas_vivienda=[FIJO, MOVIL]),
        caso=tiene_internet,
        valido=respuesta_definida,
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
