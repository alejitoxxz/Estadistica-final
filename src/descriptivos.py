"""Resumenes descriptivos del conjunto de datos."""
from __future__ import annotations

from typing import Iterable

import pandas as pd


def _imprimir_estadisticos_basicos(serie: pd.Series, nombre: str) -> None:
    """Imprime medidas descriptivas básicas para una serie numérica."""
    serie_limpia = serie.dropna()
    if serie_limpia.empty:
        print(f"No hay datos disponibles para calcular estadísticos de {nombre}.")
        return

    moda = serie_limpia.mode()
    moda_str = ", ".join(f"{valor:.2f}" for valor in moda) if not moda.empty else "N/A"

    print(f"--- {nombre} ---")
    print(f"n = {len(serie_limpia)}")
    print(f"Media = {serie_limpia.mean():.2f}")
    print(f"Mediana = {serie_limpia.median():.2f}")
    print(f"Moda = {moda_str}")
    print(f"Desviación estándar = {serie_limpia.std(ddof=1):.2f}")
    print("Cuartiles (Q1, Q2, Q3) = "
          f"({serie_limpia.quantile(0.25):.2f}, {serie_limpia.quantile(0.5):.2f}, {serie_limpia.quantile(0.75):.2f})")
    print()


def resumen_general(df: pd.DataFrame) -> None:
    """Muestra estadísticos descriptivos generales de las preguntas principales."""
    columnas = {
        "acuerdo_ampliacion": "Acuerdo con la ampliación",
        "p2_economia": "Impacto en la economía",
        "p3_necesidad": "Percepción de necesidad",
    }
    for columna, nombre in columnas.items():
        if columna in df.columns:
            _imprimir_estadisticos_basicos(df[columna], nombre)
        else:
            print(f"La columna '{columna}' no se encuentra en el DataFrame.")


def resumen_por_grupo(df: pd.DataFrame, by_cols: Iterable[str]) -> pd.DataFrame:
    """Calcula medias y desviaciones estándar agrupadas por factores."""
    columnas_existentes = [col for col in by_cols if col in df.columns]
    if not columnas_existentes:
        raise ValueError("Ninguna de las columnas especificadas existe en el DataFrame.")

    resumen = (
        df.dropna(subset=["acuerdo_ampliacion"])
        .groupby(list(columnas_existentes))
        ["acuerdo_ampliacion"]
        .agg(["count", "mean", "std"])
        .rename(columns={"count": "n", "mean": "media", "std": "desviacion"})
        .reset_index()
    )

    print("Resumen por grupos:")
    print(resumen)
    print()

    return resumen
