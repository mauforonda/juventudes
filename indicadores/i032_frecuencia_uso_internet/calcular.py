"""Calcula la frecuencia de uso de internet entre jóvenes usuarios."""

from pathlib import Path
from comun import escribir_resultados, validar_ficha
from eh import DIMENSIONES_JOVENES, GESTION, cargar_personas
from encuestas import estimar_distribucion

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
USO = "s03c_16a"
FRECUENCIA = "s03c_16b"
MAPA_FRECUENCIA = {
    1: "diariamente",
    2: "algunos_dias_semana",
    3: "algunos_dias_mes",
    4: "algunos_dias_trimestre",
}
CATEGORIA = "frecuencia"
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
        cargar_personas([USO, FRECUENCIA])
        .loc[lambda d: d[USO].eq(1)]
        .assign(frecuencia=lambda d: d[FRECUENCIA].map(MAPA_FRECUENCIA))
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
