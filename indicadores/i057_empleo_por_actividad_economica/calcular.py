"""Calcula la distribución del empleo juvenil por actividad económica."""

from pathlib import Path

from comun import escribir_resultados, validar_codigos_municipales, validar_ficha
from cpv import DIMENSIONES_JOVENES
from empleo_cpv import calcular_distribucion_ocupados

BASE_INDICADOR = Path(__file__).resolve().parent
FICHA_PATH = BASE_INDICADOR / "ficha.json"
RESULTADOS_PATH = BASE_INDICADOR / "resultados.csv"
VARIABLE = "act_eco_2d_19"
CATEGORIA = "actividad_economica"
MAPA_ACTIVIDAD = {
    1: "agricultura_ganaderia_y_pesca",
    2: "mineria",
    3: "industria_manufacturera",
    4: "electricidad_y_gas",
    5: "agua_y_residuos",
    6: "construccion",
    7: "comercio",
    8: "transporte_y_almacenamiento",
    9: "alojamiento_y_comidas",
    10: "informacion_y_comunicaciones",
    11: "finanzas_y_seguros",
    12: "actividades_inmobiliarias",
    13: "servicios_profesionales_y_tecnicos",
    14: "servicios_administrativos",
    15: "administracion_publica",
    16: "educacion",
    17: "salud_y_asistencia_social",
    18: "arte_y_recreacion",
    19: "otros_servicios",
    20: "hogares_como_empleadores",
    21: "organismos_extraterritoriales",
}
COLUMNAS_RESULTADO = [
    "gestion",
    *DIMENSIONES_JOVENES,
    CATEGORIA,
    "numerador",
    "denominador",
    "valor",
]


def calcular():
    return calcular_distribucion_ocupados(VARIABLE, CATEGORIA, MAPA_ACTIVIDAD)


def main() -> None:
    validar_ficha(FICHA_PATH)
    resultados = calcular()
    validar_codigos_municipales(resultados, "codigo_municipio")
    escribir_resultados(
        resultados,
        RESULTADOS_PATH,
        columnas=COLUMNAS_RESULTADO,
        ordenar_por=[*DIMENSIONES_JOVENES, CATEGORIA],
    )


if __name__ == "__main__":
    main()
