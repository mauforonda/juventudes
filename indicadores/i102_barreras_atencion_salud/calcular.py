"""Calcula las barreras de atención declaradas por jóvenes sin atención."""

from pathlib import Path
from comun import escribir_resultados, validar_ficha
from edsa import DIMENSIONES_JOVENES, GESTION, cargar_hogar
from encuestas import estimar_respuestas_multiples

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
NO_ATENCION = "hs03_0035_V"
CATEGORIA = "barrera"
CATEGORIAS = {
    "tiempo_de_espera": ["hs03_0039_A", "hs03_0039_B"],
    "calidad_o_falta_de_personal": [
        "hs03_0039_C",
        "hs03_0039_D",
        "hs03_0039_E",
        "hs03_0039_F",
        "hs03_0039_M",
    ],
    "distancia": ["hs03_0039_G"],
    "horarios": ["hs03_0039_H", "hs03_0039_I"],
    "falta_de_dinero": ["hs03_0039_J"],
    "desconocimiento": ["hs03_0039_K"],
    "idioma": ["hs03_0039_L"],
    "otra_razon": ["hs03_0039_X"],
}
VARIABLES = [variable for grupo in CATEGORIAS.values() for variable in grupo]
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
    datos = cargar_hogar([NO_ATENCION, *VARIABLES])
    return estimar_respuestas_multiples(
        datos,
        categorias=CATEGORIAS,
        categoria=CATEGORIA,
        dimensiones=DIMENSIONES_JOVENES,
        gestion=GESTION,
        valido=lambda d: d[NO_ATENCION].eq(1) & d[VARIABLES].eq(1).any(axis=1),
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
