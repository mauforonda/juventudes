"""Calcula la recepción de remesas y su medio principal."""

from pathlib import Path
from comun import escribir_resultados, validar_ficha
from eh import DIMENSIONES_JOVENES, GESTION, cargar_personas
from encuestas import estimar_distribucion

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
RECEPCION = "s05c_07"
MEDIO_ORIGINAL = "s05c_09aa"
CATEGORIA = "medio_recepcion"
MAPA_MEDIO = {
    1: "banco",
    2: "empresa_de_remesas",
    3: "encomendero",
    4: "transporte_o_correo",
    5: "criptoactivos",
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
        cargar_personas([RECEPCION, MEDIO_ORIGINAL])
        .loc[lambda d: d[RECEPCION].isin([1, 2])]
        .assign(
            medio_recepcion=lambda d: d[MEDIO_ORIGINAL]
            .map(MAPA_MEDIO)
            .where(d[RECEPCION].eq(1), "no_recibio")
            .fillna("medio_no_declarado")
        )
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
