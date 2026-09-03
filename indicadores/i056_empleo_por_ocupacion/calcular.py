"""Calcula la distribución del empleo juvenil por grupo ocupacional."""

from pathlib import Path

from comun import escribir_resultados, validar_codigos_municipales, validar_ficha
from cpv import DIMENSIONES_JOVENES
from empleo_cpv import calcular_distribucion_ocupados

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
VARIABLE = "ocu_1d_19"
CATEGORIA = "grupo_ocupacional"
MAPA_OCUPACION = {
    0: "fuerzas_armadas",
    1: "directores_y_gerentes",
    2: "profesionales",
    3: "tecnicos",
    4: "personal_administrativo",
    5: "servicios_y_ventas",
    6: "agricultura_y_pesca",
    7: "construccion_y_manufactura",
    8: "operadores_de_maquinaria",
    9: "ocupaciones_elementales",
}
COLUMNAS_RESULTADO = [
    "gestion",
    *DIMENSIONES_JOVENES,
    CATEGORIA,
    "numerador",
    "denominador",
    "valor",
]


def calcular():
    return calcular_distribucion_ocupados(VARIABLE, CATEGORIA, MAPA_OCUPACION)


def main() -> None:
    validar_ficha(FICHA_PATH)
    resultados = calcular()
    validar_codigos_municipales(resultados, "codigo_municipio")
    escribir_resultados(
        resultados,
        RESULTADOS_PATH,
        columnas=COLUMNAS_RESULTADO,
        ordenar_por=[*DIMENSIONES_JOVENES, CATEGORIA],
    )


if __name__ == "__main__":
    main()
