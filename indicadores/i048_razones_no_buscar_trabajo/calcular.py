"""Calcula las razones por las que jóvenes no buscaron trabajo."""

from pathlib import Path

from comun import escribir_resultados, validar_ficha
from ece import DIMENSIONES_JOVENES, GESTION, cargar_personas
from encuestas import estimar_distribucion

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
BUSCO_TRABAJO = "s2_05"
RAZON_ORIGINAL = "s2_06"
CATEGORIA = "razon_no_busqueda"
MAPA_RAZON = {
    1: "trabajo_asegurado",
    2: "espera_respuesta",
    3: "cree_que_no_encontrara",
    4: "cansancio_de_buscar",
    5: "espera_mayor_actividad",
    6: "estudios_o_vacaciones",
    7: "jubilacion_o_edad_avanzada",
    8: "edad_temprana",
    9: "salud_o_discapacidad",
    10: "no_necesita_trabajar",
    11: "hogar_cuidado_o_embarazo",
    12: "otra_razon",
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
        cargar_personas([BUSCO_TRABAJO, RAZON_ORIGINAL])
        .loc[lambda d: d[BUSCO_TRABAJO].eq(2)]
        .assign(razon_no_busqueda=lambda d: d[RAZON_ORIGINAL].map(MAPA_RAZON))
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
