"""Funciones compartidas por los indicadores del observatorio."""

from __future__ import annotations

import json
import os
import tempfile
import tomllib
from collections.abc import Iterable
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
CONFIG_PREDETERMINADA = BASE_DIR / "config.local.toml"
DICCIONARIOS_DIR = BASE_DIR / "diccionarios"

CAMPOS_FICHA = frozenset(
    {
        "codigo",
        "nombre",
        "objetivo",
        "definicion_conceptual",
        "poblacion_objetivo",
        "descripcion_operativa",
        "unidad_medida",
        "fuente",
        "desagregaciones",
        "metodo",
    }
)


def cargar_configuracion(ruta: Path | None = None) -> dict:
    """Lee las rutas locales sin incorporarlas al código de los indicadores."""

    ruta_config = ruta or Path(
        os.environ.get("OBSERVATORIO_CONFIG", CONFIG_PREDETERMINADA)
    )
    if not ruta_config.exists():
        raise FileNotFoundError(
            f"No existe {ruta_config}. Copie config.example.toml como "
            "config.local.toml y complete las rutas."
        )

    with ruta_config.open("rb") as archivo:
        configuracion = tomllib.load(archivo)

    if "fuentes" not in configuracion:
        raise ValueError("La configuración debe contener la sección [fuentes].")
    return configuracion


def ruta_fuente(configuracion: dict, fuente: str, *partes: str) -> Path:
    """Resuelve un archivo a partir de una fuente declarada en la configuración."""

    try:
        raiz = Path(configuracion["fuentes"][fuente]).expanduser().resolve()
    except KeyError as error:
        raise KeyError(f"La fuente {fuente!r} no está configurada.") from error

    ruta = raiz.joinpath(*partes)
    if not ruta.exists():
        raise FileNotFoundError(f"No existe el insumo esperado: {ruta}")
    return ruta


def cargar_municipios() -> pd.DataFrame:
    """Lee el diccionario territorial común y conserva los códigos como texto."""

    # Los códigos se leen como texto para preservar todos sus dígitos y poder
    # compararlos directamente con los códigos de las tablas de resultados.
    return pd.read_csv(
        DICCIONARIOS_DIR / "municipios.csv",
        dtype={
            "codigo_municipio": "string",
            "codigo_departamento": "string",
        },
    )


def validar_codigos_municipales(datos: pd.DataFrame, columna: str) -> None:
    """Comprueba que todos los códigos producidos estén en el catálogo de 2024."""

    # Se comparan los códigos distintos de la tabla con los del diccionario.
    # Los valores vacíos no se tratan como códigos desconocidos.
    codigos_validos = set(cargar_municipios()["codigo_municipio"].dropna())
    codigos_observados = set(datos[columna].dropna().astype("string"))
    desconocidos = sorted(codigos_observados - codigos_validos)
    if desconocidos:
        muestra = ", ".join(desconocidos[:10])
        raise ValueError(f"Hay códigos municipales desconocidos: {muestra}")


def validar_ficha(ruta: Path) -> None:
    """Comprueba que una ficha contenga las definiciones mínimas acordadas."""

    with ruta.open(encoding="utf-8") as archivo:
        ficha = json.load(archivo)

    faltantes = sorted(CAMPOS_FICHA - ficha.keys())
    if faltantes:
        raise ValueError(f"La ficha no contiene: {', '.join(faltantes)}")


def escribir_resultados(
    datos: pd.DataFrame,
    ruta: Path,
    *,
    columnas: Iterable[str],
    ordenar_por: Iterable[str],
) -> None:
    """Valida el esquema y reemplaza un CSV sólo cuando terminó de escribirse."""

    # Convertimos las listas recibidas una sola vez para preservar su orden.
    columnas = list(columnas)
    ordenar_por = list(ordenar_por)

    # La tabla debe contener exactamente las columnas declaradas por el
    # indicador: ninguna puede faltar y ninguna columna auxiliar puede quedar.
    faltantes = [columna for columna in columnas if columna not in datos.columns]
    sobrantes = [columna for columna in datos.columns if columna not in columnas]
    if faltantes or sobrantes:
        raise ValueError(
            f"Columnas faltantes: {faltantes}. Columnas no esperadas: {sobrantes}."
        )

    # Una columna sin ningún dato no aporta al resultado y suele señalar una
    # transformación incompleta.
    completamente_vacias = [
        columna
        for columna in columnas
        if not datos.empty and datos[columna].isna().all()
    ]
    if completamente_vacias:
        raise ValueError(
            "La tabla contiene columnas completamente vacías: "
            + ", ".join(completamente_vacias)
        )

    # Seleccionamos las columnas en el orden legible acordado y ordenamos las
    # filas para que ejecuciones equivalentes produzcan el mismo CSV.
    salida = datos.loc[:, columnas].sort_values(ordenar_por)
    ruta.parent.mkdir(parents=True, exist_ok=True)

    # Primero escribimos un archivo temporal. Sólo después de terminarlo
    # reemplazamos el resultado anterior, evitando dejar un CSV incompleto.
    descriptor, temporal = tempfile.mkstemp(
        prefix=f".{ruta.name}.", suffix=".tmp", dir=ruta.parent
    )
    os.close(descriptor)
    temporal_path = Path(temporal)
    try:
        salida.to_csv(temporal_path, index=False)
        os.replace(temporal_path, ruta)
    except BaseException:
        temporal_path.unlink(missing_ok=True)
        raise
