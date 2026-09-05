"""Calcula el ingreso laboral medio y mediano según el nivel educativo."""

from pathlib import Path
from comun import escribir_resultados, validar_ficha
from ece import DIMENSIONES_JOVENES, GESTION, cargar_personas
from encuestas import estimar_media, estimar_mediana

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
    "poblacion_estimada",
    "media",
    "cv_media",
    "mediana",
    "cv_mediana",
]


def calcular():
    datos = (
        cargar_personas([CONDICION_ACTIVIDAD, INGRESO, NIVEL_ORIGINAL])
        .loc[lambda d: d[CONDICION_ACTIVIDAD].eq(1) & d[INGRESO].gt(0)]
        .assign(nivel_educativo=lambda d: d[NIVEL_ORIGINAL].map(MAPA_NIVEL))
        .dropna(subset=[NIVEL])
    )
    dimensiones = [*DIMENSIONES_JOVENES, NIVEL]
    return (
        estimar_media(
            datos,
            variable=INGRESO,
            dimensiones=dimensiones,
            gestion=GESTION,
        )
        .rename(columns={"valor": "media", "cv": "cv_media"})
        .merge(
            estimar_mediana(
                datos,
                variable=INGRESO,
                dimensiones=dimensiones,
                gestion=GESTION,
            ).rename(
                columns={
                    "observaciones": "observaciones_mediana",
                    "valor": "mediana",
                    "cv": "cv_mediana",
                }
            ),
            on=["gestion", *dimensiones],
            validate="one_to_one",
        )
        .merge(
            datos.groupby(dimensiones, as_index=False, dropna=False).agg(
                poblacion_estimada=("factor", "sum")
            ),
            on=dimensiones,
            validate="one_to_one",
        )
        .drop(columns="observaciones_mediana")
        .loc[:, COLUMNAS_RESULTADO]
    )


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
