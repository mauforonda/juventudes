"""Calcula los lugares de atención de problemas de salud recientes."""

from pathlib import Path
from comun import escribir_resultados, validar_ficha
from edsa import DIMENSIONES_JOVENES, GESTION, cargar_hogar
from encuestas import estimar_respuestas_multiples

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
PROBLEMA = "hs03_0033"
CATEGORIA = "lugar_atencion"
CATEGORIAS = {
    "servicio_publico": [f"hs03_0035_{letra}" for letra in "ABCDEFG"],
    "caja_o_seguro": [f"hs03_0035_{letra}" for letra in "HIJKLMNO"],
    "servicio_privado": ["hs03_0035_P", "hs03_0035_Q"],
    "farmacia": ["hs03_0035_T"],
    "medicina_tradicional": ["hs03_0035_U"],
    "otra_atencion": ["hs03_0035_R", "hs03_0035_S", "hs03_0035_X"],
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
    datos = cargar_hogar([PROBLEMA, *VARIABLES])
    return estimar_respuestas_multiples(
        datos,
        categorias=CATEGORIAS,
        categoria=CATEGORIA,
        dimensiones=DIMENSIONES_JOVENES,
        gestion=GESTION,
        valido=lambda d: d[PROBLEMA].eq(1) & d[VARIABLES].eq(1).any(axis=1),
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
