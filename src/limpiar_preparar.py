"""Funciones para limpiar y preparar los datos para el análisis."""
from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd

from .config import COLUMN_MAP


EDAD_MINIMA: int = 16
EDAD_LIMITE_JOVEN: int = 24
EDAD_LIMITE_ADULTO: int = 44


def _validar_columnas(df: pd.DataFrame, columnas_requeridas: Iterable[str]) -> None:
    """Verifica que todas las columnas requeridas estén presentes."""
    columnas_disponibles = set(df.columns)
    faltantes = [col for col in columnas_requeridas if col not in columnas_disponibles]
    if faltantes:
        disponibles = ", ".join(sorted(columnas_disponibles))
        faltantes_str = ", ".join(faltantes)
        raise KeyError(
            "No se encontraron las siguientes columnas requeridas en el DataFrame: "
            f"{faltantes_str}. Columnas disponibles: {disponibles}."
        )


def preparar_datos(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia y prepara el DataFrame para los análisis estadísticos.

    El procedimiento renombra columnas de acuerdo con :data:`src.config.COLUMN_MAP`,
    crea variables categóricas para frecuencia de viaje y grupos de edad,
    calcula el tratamiento factorial y genera indicadores adicionales.
    """

    df_trabajo = df.copy()

    # Renombrar columnas según el mapa definido en config
    columnas_originales = list(COLUMN_MAP.values())
    _validar_columnas(df_trabajo, columnas_originales)

    mapa_renombrar = {valor: clave for clave, valor in COLUMN_MAP.items()}
    df_trabajo = df_trabajo.rename(columns=mapa_renombrar)

    # Guardar una copia del valor original de viajes antes de convertir a número
    if "viajes_anio" in df_trabajo.columns:
        df_trabajo["viajes_original"] = df_trabajo["viajes_anio"]
    else:
        df_trabajo["viajes_original"] = np.nan

    # Conversión a valores numéricos donde aplique
    for columna in ("edad", "viajes_anio", "p1_acuerdo", "p2_economia", "p3_necesidad"):
        if columna in df_trabajo.columns:
            df_trabajo[columna] = pd.to_numeric(df_trabajo[columna], errors="coerce")

    # Crear frecuencia de viaje (robusto: soporta texto o números)
    # Regla:
    # - Frecuente si:
    #   * viajes_anio >= 6 (numérico), o
    #   * el texto original contiene "Más de 6" o "mas de 6"
    cond_frecuente_numerico = df_trabajo["viajes_anio"] >= 6

    viajes_texto = df_trabajo["viajes_original"].astype(str).str.lower()
    cond_frecuente_texto = viajes_texto.str.contains("más de 6") | viajes_texto.str.contains(
        "mas de 6"
    )

    cond_frecuente = cond_frecuente_numerico | cond_frecuente_texto

    df_trabajo["frecuencia_viaje"] = np.where(cond_frecuente, "Frecuente", "No frecuente")

    # Clasificación por grupos de edad
    condiciones = [
        (df_trabajo["edad"] >= EDAD_MINIMA) & (df_trabajo["edad"] <= EDAD_LIMITE_JOVEN),
        (df_trabajo["edad"] >= EDAD_LIMITE_JOVEN + 1) & (df_trabajo["edad"] <= EDAD_LIMITE_ADULTO),
        df_trabajo["edad"] >= EDAD_LIMITE_ADULTO + 1,
    ]
    elecciones = ["Joven", "Adulto", "Adulto mayor"]

    # Usamos un string como valor por defecto para evitar conflictos de tipo con NumPy
    df_trabajo["grupo_edad"] = np.select(
        condiciones,
        elecciones,
        default="Sin categoría",
    )

    # Contar registros fuera del rango esperado (edad < 16 o datos raros)
    registros_fuera_rango = (df_trabajo["grupo_edad"] == "Sin categoría").sum()
    if registros_fuera_rango > 0:
        print(
            "Advertencia: se encontraron",
            registros_fuera_rango,
            "registros con edades fuera del rango definido (16 años en adelante).",
        )

    # Normalizar nombre de la pregunta principal
    df_trabajo = df_trabajo.rename(columns={"p1_acuerdo": "acuerdo_ampliacion"})

    # Crear identificador de tratamiento
    df_trabajo["tratamiento"] = (
        df_trabajo["frecuencia_viaje"].astype(str)
        + " - "
        + df_trabajo["grupo_edad"].astype(str)
    )

    # Variable binaria para quienes están a favor (>= 6)
    df_trabajo["a_favor"] = np.where(df_trabajo["acuerdo_ampliacion"] >= 6, 1, 0)

    return df_trabajo
