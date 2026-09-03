"""Calcula los lugares de agresiones fuera de la pareja."""

from pathlib import Path
import pandas as pd
from comun import escribir_resultados, validar_ficha
from edsa import DIMENSIONES_JOVENES, GESTION, cargar_individuales
from encuestas import estimar_respuestas_multiples

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
LETRAS = "ABCDEFGX"
LUGARES = {
    "espacio_publico": ["A"],
    "trabajo": ["B"],
    "escuela": ["C"],
    "universidad": ["D"],
    "evento_publico": ["E"],
    "institucion_policial_militar": ["F"],
    "organizacion_social_politica": ["G"],
    "otro": ["X"],
}
COLUMNAS_RESULTADO = [
    "gestion",
    *DIMENSIONES_JOVENES,
    "lugar",
    "observaciones",
    "numerador",
    "denominador",
    "valor",
    "cv",
]


def calcular():
    mujeres = {f"agresion_{l}": f"ms11_1134_{l}" for l in LETRAS} | {
        f"sexual_{l}": f"ms11_1137_{l}" for l in LETRAS
    }
    hombres = {f"agresion_{l}": f"vs08_0826_{l}" for l in LETRAS} | {
        f"sexual_{l}": f"vs08_0829_{l}" for l in LETRAS
    }
    datos = cargar_individuales(mujeres, hombres).assign(
        **{
            nombre: lambda d, letras=letras: d[
                [
                    f"{tipo}_{letra}"
                    for tipo in ["agresion", "sexual"]
                    for letra in letras
                ]
            ]
            .eq(1)
            .any(axis=1)
            for nombre, letras in LUGARES.items()
        }
    )
    return estimar_respuestas_multiples(
        datos,
        categorias={nombre: [nombre] for nombre in LUGARES},
        categoria="lugar",
        valido=lambda d: pd.concat([d[nombre] for nombre in LUGARES], axis=1).any(
            axis=1
        ),
        dimensiones=DIMENSIONES_JOVENES,
        gestion=GESTION,
    )


def main() -> None:
    validar_ficha(FICHA_PATH)
    escribir_resultados(
        calcular(),
        RESULTADOS_PATH,
        columnas=COLUMNAS_RESULTADO,
        ordenar_por=[*DIMENSIONES_JOVENES, "lugar"],
    )


if __name__ == "__main__":
    main()
