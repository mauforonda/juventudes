"""Calcula los motivos de discriminación declarados."""

from pathlib import Path
from comun import escribir_resultados, validar_ficha
from eh import DIMENSIONES_JOVENES, GESTION, cargar_discriminacion
from encuestas import estimar_respuestas_multiples

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
CATEGORIAS = {
    "color_piel": ["s09a_01a"],
    "pertenencia_indigena": ["s09a_01b"],
    "procedencia": ["s09a_01c"],
    "orientacion_o_identidad": ["s09a_01d"],
    "edad": ["s09a_01e"],
    "sexo": ["s09a_01f"],
    "idioma": ["s09a_01g"],
    "vestimenta": ["s09a_01h"],
    "discapacidad": ["s09a_01i"],
    "religion": ["s09a_01j"],
    "condicion_economica_social": ["s09a_01k"],
    "otro": ["s09a_01l"],
}
MOTIVOS = [variable for variables in CATEGORIAS.values() for variable in variables]
COLUMNAS_RESULTADO = [
    "gestion",
    *DIMENSIONES_JOVENES,
    "motivo",
    "observaciones",
    "numerador",
    "denominador",
    "valor",
    "cv",
]


def calcular():
    datos = cargar_discriminacion(MOTIVOS)
    return estimar_respuestas_multiples(
        datos,
        categorias=CATEGORIAS,
        categoria="motivo",
        valido=lambda d: d[MOTIVOS].eq(1).any(axis=1),
        dimensiones=DIMENSIONES_JOVENES,
        gestion=GESTION,
    )


def main() -> None:
    validar_ficha(FICHA_PATH)
    escribir_resultados(
        calcular(),
        RESULTADOS_PATH,
        columnas=COLUMNAS_RESULTADO,
        ordenar_por=[*DIMENSIONES_JOVENES, "motivo"],
    )


if __name__ == "__main__":
    main()
