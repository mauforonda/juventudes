"""Calcula las razones para no denunciar violencia de pareja."""

from pathlib import Path
import pandas as pd
from comun import escribir_resultados, validar_ficha
from edsa import DIMENSIONES_JOVENES, GESTION, cargar_individuales
from encuestas import estimar_respuestas_multiples

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
LETRAS = "ABCDEFGHIJKLMNX"
GRUPOS = {
    "miedo": list("EFGN"),
    "verguenza": ["B"],
    "desconocimiento": ["A"],
    "desconfianza_justicia": ["J"],
    "dependencia_economica": ["H"],
    "otra_razon": list("CDIKLMX"),
}
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
    datos = (
        cargar_individuales(
            {f"razon_{l}": f"ms11_1130_{l}" for l in LETRAS},
            {f"razon_{l}": f"vs08_0822_{l}" for l in LETRAS},
        )
        .loc[lambda d: d[[f"razon_{l}" for l in LETRAS]].notna().any(axis=1)]
        .assign(
            **{
                nombre: lambda d, letras=letras: d[
                    [f"razon_{letra}" for letra in letras]
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
        valido=lambda d: pd.Series(True, index=d.index),
        dimensiones=DIMENSIONES_JOVENES,
        gestion=GESTION,
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
