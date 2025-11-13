"""Cálculo de intervalos de confianza para media y proporción."""
from __future__ import annotations

from typing import Dict

import numpy as np
import pandas as pd
from scipy import stats


def intervalo_confianza_media(serie: pd.Series, alpha: float = 0.05) -> Dict[str, float]:
    """Calcula el intervalo de confianza para la media poblacional."""
    datos = serie.dropna().astype(float)
    n = datos.size
    if n == 0:
        raise ValueError("La serie no contiene datos válidos para calcular el intervalo de confianza.")

    media = datos.mean()
    desviacion = datos.std(ddof=1)
    error_estandar = desviacion / np.sqrt(n)
    gl = n - 1
    t_critico = stats.t.ppf(1 - alpha / 2, df=gl)
    margen = t_critico * error_estandar

    resultado = {
        "n": float(n),
        "media": float(media),
        "desviacion": float(desviacion),
        "error_estandar": float(error_estandar),
        "t_critico": float(t_critico),
        "limite_inferior": float(media - margen),
        "limite_superior": float(media + margen),
        "alpha": float(alpha),
    }
    return resultado


def intervalo_confianza_proporcion(
    serie_binaria: pd.Series, alpha: float = 0.05
) -> Dict[str, float]:
    """Calcula el intervalo de confianza para una proporción poblacional."""
    datos = serie_binaria.dropna().astype(float)
    n = datos.size
    if n == 0:
        raise ValueError("La serie binaria no contiene datos válidos.")

    p_hat = datos.mean()
    error_estandar = np.sqrt(p_hat * (1 - p_hat) / n)
    z_critico = stats.norm.ppf(1 - alpha / 2)
    margen = z_critico * error_estandar

    resultado = {
        "n": float(n),
        "p_hat": float(p_hat),
        "error_estandar": float(error_estandar),
        "z_critico": float(z_critico),
        "limite_inferior": float(max(0.0, p_hat - margen)),
        "limite_superior": float(min(1.0, p_hat + margen)),
        "alpha": float(alpha),
    }
    return resultado
