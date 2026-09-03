"""Calcula las razones declaradas para no usar anticonceptivos."""

from pathlib import Path
import pandas as pd
from comun import escribir_resultados, validar_ficha
from edsa import DIMENSIONES_JOVENES, GESTION, cargar_mujeres
from encuestas import estimar_respuestas_multiples

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
ACTIVA = "sexualmente_activa"
SIN_METODO = "sin_metodo"
DESEO = "deseo_embarazo"
GRUPOS = {
    "oposicion": list("IJKL"),
    "costo": ["T"],
    "distancia": ["S"],
    "desconocimiento": list("MN"),
    "salud_o_efectos": list("OPQR"),
    "otra_razon": list("ABCDEFGHX"),
}
VARIABLES = [
    f"razon_{pregunta}_{letra}"
    for pregunta in ["01", "02"]
    for letra in "ABCDEFGHIJKLMNOPQRSTX"
]
COLUMNAS_RESULTADO = [
    "gestion",
    *DIMENSIONES_JOVENES,
    "razon",
    "observaciones",
    "numerador",
    "denominador",
    "valor",
    "cv",
]


def calcular():
    columnas = {
        ACTIVA: "sexact_m",
        SIN_METODO: "actmaconcep_nin_m",
        DESEO: "deseo_m",
    } | {
        f"razon_{pregunta}_{letra}": f"ms07_0707_{pregunta}_{letra}"
        for pregunta in ["01", "02"]
        for letra in "ABCDEFGHIJKLMNOPQRSTX"
    }
    datos = (
        cargar_mujeres(columnas)
        .loc[lambda d: d[ACTIVA].eq(1) & d[SIN_METODO].eq(1) & d[DESEO].isin([2, 3, 5])]
        .loc[lambda d: d[VARIABLES].notna().any(axis=1)]
        .assign(
            **{
                nombre: lambda d, letras=letras: d[
                    [
                        f"razon_{pregunta}_{letra}"
                        for pregunta in ["01", "02"]
                        for letra in letras
                    ]
                ]
                .eq(1)
                .any(axis=1)
                for nombre, letras in GRUPOS.items()
            }
        )
    )
    return estimar_respuestas_multiples(
        datos,
        categorias={nombre: [nombre] for nombre in GRUPOS},
        categoria="razon",
        dimensiones=DIMENSIONES_JOVENES,
        gestion=GESTION,
        valido=lambda d: pd.Series(True, index=d.index),
    )


def main() -> None:
    validar_ficha(FICHA_PATH)
    escribir_resultados(
        calcular(),
        RESULTADOS_PATH,
        columnas=COLUMNAS_RESULTADO,
        ordenar_por=[*DIMENSIONES_JOVENES, "razon"],
    )


if __name__ == "__main__":
    main()
