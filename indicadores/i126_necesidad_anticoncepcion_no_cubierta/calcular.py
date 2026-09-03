"""Calcula la necesidad de anticoncepción no cubierta."""

from pathlib import Path
from comun import escribir_resultados, validar_ficha
from edsa import DIMENSIONES_JOVENES, GESTION, cargar_mujeres
from encuestas import estimar_porcentaje

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
ACTIVA = "sexualmente_activa"
SIN_METODO = "sin_metodo"
DESEO = "deseo_embarazo"
DESEA_POSTERGAR_O_EVITAR = [2, 3, 5]
COLUMNAS_RESULTADO = [
    "gestion",
    *DIMENSIONES_JOVENES,
    "observaciones",
    "numerador",
    "denominador",
    "valor",
    "cv",
]


def calcular():
    datos = cargar_mujeres(
        {ACTIVA: "sexact_m", SIN_METODO: "actmaconcep_nin_m", DESEO: "deseo_m"}
    )
    return estimar_porcentaje(
        datos.loc[lambda d: d[ACTIVA].eq(1)],
        caso=lambda d: d[SIN_METODO].eq(1) & d[DESEO].isin(DESEA_POSTERGAR_O_EVITAR),
        valido=lambda d: d[SIN_METODO].isin([0, 1]) & d[DESEO].isin(range(1, 8)),
        dimensiones=DIMENSIONES_JOVENES,
        gestion=GESTION,
    )


def main() -> None:
    validar_ficha(FICHA_PATH)
    escribir_resultados(
        calcular(),
        RESULTADOS_PATH,
        columnas=COLUMNAS_RESULTADO,
        ordenar_por=DIMENSIONES_JOVENES,
    )


if __name__ == "__main__":
    main()
