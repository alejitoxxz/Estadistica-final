"""Resumenes descriptivos del conjunto de datos."""
from __future__ import annotations

from typing import Dict, Iterable

import pandas as pd


def _calcular_estadisticos_basicos(serie: pd.Series) -> Dict[str, object]:
    """Calcula medidas descriptivas básicas para una serie numérica."""

    serie_limpia = serie.dropna()
    if serie_limpia.empty:
        return {
            "n": 0,
            "media": float("nan"),
            "mediana": float("nan"),
            "moda": [],
            "desviacion": float("nan"),
            "q1": float("nan"),
            "q2": float("nan"),
            "q3": float("nan"),
        }

    moda = serie_limpia.mode().tolist()

    return {
        "n": int(len(serie_limpia)),
        "media": float(serie_limpia.mean()),
        "mediana": float(serie_limpia.median()),
        "moda": moda,
        "desviacion": float(serie_limpia.std(ddof=1)),
        "q1": float(serie_limpia.quantile(0.25)),
        "q2": float(serie_limpia.quantile(0.5)),
        "q3": float(serie_limpia.quantile(0.75)),
    }


def _imprimir_estadisticos_basicos(estadisticos: Dict[str, object], nombre: str) -> None:
    """Imprime en consola un resumen descriptivo."""

    if estadisticos["n"] == 0:
        print(f"No hay datos disponibles para calcular estadísticos de {nombre}.")
        print()
        return

    moda = estadisticos.get("moda", [])
    moda_str = ", ".join(f"{valor:.2f}" for valor in moda) if moda else "N/A"

    print(f"--- {nombre} ---")
    print(f"n = {estadisticos['n']}")
    print(f"Media = {estadisticos['media']:.2f}")
    print(f"Mediana = {estadisticos['mediana']:.2f}")
    print(f"Moda = {moda_str}")
    print(f"Desviación estándar = {estadisticos['desviacion']:.2f}")
    print(
        "Cuartiles (Q1, Q2, Q3) = "
        f"({estadisticos['q1']:.2f}, {estadisticos['q2']:.2f}, {estadisticos['q3']:.2f})"
    )
    print()


def resumen_general(df: pd.DataFrame) -> Dict[str, Dict[str, object]]:
    """Devuelve y muestra estadísticos descriptivos generales."""

    columnas = {
        "acuerdo_ampliacion": "Acuerdo con la ampliación",
        "p2_economia": "Impacto en la economía",
        "p3_necesidad": "Percepción de necesidad",
    }

    resultados: Dict[str, Dict[str, object]] = {}
    for columna, nombre in columnas.items():
        if columna in df.columns:
            estadisticos = _calcular_estadisticos_basicos(df[columna])
            estadisticos["nombre"] = nombre
            resultados[columna] = estadisticos
            _imprimir_estadisticos_basicos(estadisticos, nombre)
        else:
            print(f"La columna '{columna}' no se encuentra en el DataFrame.")
            print()

    return resultados


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
