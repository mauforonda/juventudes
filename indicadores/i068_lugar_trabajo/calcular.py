"""Calcula la distribución de jóvenes ocupados por lugar de trabajo."""

from pathlib import Path
from comun import escribir_resultados, validar_ficha
from ece import DIMENSIONES_JOVENES
from empleo_ece import calcular_distribucion_ocupados

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
VARIABLE = "s2_25"
CATEGORIA = "lugar_trabajo"
MAPA_LUGAR = {
    1: "vivienda_particular",
    2: "local_o_terreno_propio",
    3: "local_de_empresa_o_cliente",
    4: "predio_agropecuario_o_natural",
    5: "puesto_movil",
    6: "quiosco_o_puesto_fijo",
    7: "vehiculo",
    8: "domicilio_del_cliente",
    9: "ambulante",
    10: "ambulante_de_preventa",
    11: "otro_lugar",
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
    return calcular_distribucion_ocupados(VARIABLE, CATEGORIA, MAPA_LUGAR)


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
