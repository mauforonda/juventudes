"""Calcula la interrupción de clases durante la gestión educativa."""

from pathlib import Path

import pandas as pd

from comun import escribir_resultados, validar_ficha
from eh import DIMENSIONES_JOVENES, GESTION, cargar_personas
from encuestas import estimar_porcentaje

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
MATRICULA = "s03a_04"
ASISTENCIA = "s03b_10"
RAZON = "s03b_11"
RAZONES = {
    1: "vacacion_o_receso",
    2: "culmino_estudios",
    3: "trabajo",
    4: "traslado_familiar",
    5: "otra_razon",
}
CATEGORIA = "razon_inasistencia"
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
    datos = cargar_personas([MATRICULA, ASISTENCIA, RAZON]).loc[
        lambda tabla: tabla[MATRICULA].eq(1)
    ]
    resultados = [
        estimar_porcentaje(
            datos,
            caso=lambda tabla, codigo=codigo: tabla[ASISTENCIA].eq(4)
            & tabla[RAZON].eq(codigo),
            valido=lambda tabla: tabla[ASISTENCIA].between(1, 4),
            dimensiones=DIMENSIONES_JOVENES,
            gestion=GESTION,
        ).assign(**{CATEGORIA: etiqueta})
        for codigo, etiqueta in RAZONES.items()
    ]
    return pd.concat(resultados, ignore_index=True).loc[:, COLUMNAS_RESULTADO]


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
