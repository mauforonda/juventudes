"""Calcula el ingreso laboral mediano según el nivel educativo."""

from pathlib import Path
from comun import escribir_resultados, validar_ficha
from ece import DIMENSIONES_JOVENES, GESTION, cargar_personas
from encuestas import estimar_mediana

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
CONDICION_ACTIVIDAD = "condact"
INGRESO = "ylab"
NIVEL_ORIGINAL = "niv_ed"
NIVEL = "nivel_educativo"
MAPA_NIVEL = {
    0: "ninguno",
    1: "primaria_incompleta",
    2: "primaria_completa",
    3: "secundaria_incompleta",
    4: "secundaria_completa",
    5: "superior",
    7: "otros",
}
COLUMNAS_RESULTADO = [
    "gestion",
    *DIMENSIONES_JOVENES,
    NIVEL,
    "observaciones",
    "valor",
    "cv",
]


def calcular():
    datos = (
        cargar_personas([CONDICION_ACTIVIDAD, INGRESO, NIVEL_ORIGINAL])
        .loc[lambda d: d[CONDICION_ACTIVIDAD].eq(1) & d[INGRESO].gt(0)]
        .assign(nivel_educativo=lambda d: d[NIVEL_ORIGINAL].map(MAPA_NIVEL))
        .dropna(subset=[NIVEL])
    )
    return estimar_mediana(
        datos,
        variable=INGRESO,
        dimensiones=[*DIMENSIONES_JOVENES, NIVEL],
        gestion=GESTION,
    ).loc[:, COLUMNAS_RESULTADO]


def main() -> None:
    validar_ficha(FICHA_PATH)
    escribir_resultados(
        calcular(),
        RESULTADOS_PATH,
        columnas=COLUMNAS_RESULTADO,
        ordenar_por=[*DIMENSIONES_JOVENES, NIVEL],
    )


if __name__ == "__main__":
    main()
