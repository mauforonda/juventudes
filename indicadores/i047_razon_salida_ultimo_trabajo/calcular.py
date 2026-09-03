"""Calcula la razón de salida del último trabajo."""

from pathlib import Path

from comun import escribir_resultados, validar_ficha
from ece import DIMENSIONES_JOVENES, GESTION, cargar_personas
from encuestas import estimar_distribucion

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
CONDICION_ACTIVIDAD = "condact"
RAZON_ORIGINAL = "s2_13a_a"
CATEGORIA = "razon_salida"
MAPA_RAZON = {
    1: "despido_o_retiro",
    2: "fin_de_contrato",
    3: "fin_del_trabajo",
    4: "mal_desempeno_del_negocio",
    5: "salud",
    6: "hogar_o_cuidado",
    7: "edad_avanzada",
    8: "pandemia",
    9: "otra_razon",
    10: "estudios",
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
    datos = (
        cargar_personas([CONDICION_ACTIVIDAD, RAZON_ORIGINAL])
        .loc[lambda d: d[CONDICION_ACTIVIDAD].isin([2, 4, 5])]
        .assign(razon_salida=lambda d: d[RAZON_ORIGINAL].map(MAPA_RAZON))
    )
    return estimar_distribucion(
        datos, categoria=CATEGORIA, dimensiones=DIMENSIONES_JOVENES, gestion=GESTION
    )


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
