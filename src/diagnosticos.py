"""Pruebas de diagnóstico y supuestos para el análisis estadístico."""
from __future__ import annotations

from typing import Dict, Optional

import pandas as pd
from scipy import stats

ALPHA_DEFAULT = 0.05


def _interpretar_p_valor(p_valor: Optional[float], alpha: float = ALPHA_DEFAULT) -> str:
    """Devuelve un texto breve para interpretar una prueba de normalidad."""

    if p_valor is None or pd.isna(p_valor):
        return "No fue posible evaluar la normalidad con los datos disponibles."
    if p_valor < alpha:
        return "Se rechaza la normalidad (p < {:.3f}).".format(alpha)
    return "No se rechaza la normalidad (p ≥ {:.3f}).".format(alpha)


def prueba_normalidad_acuerdo(df: pd.DataFrame, alpha: float = ALPHA_DEFAULT) -> Dict[str, float | str]:
    """Aplica la prueba Shapiro-Wilk a la variable ``acuerdo_ampliacion``."""

    serie = df.get("acuerdo_ampliacion")
    if serie is None:
        return {
            "n": 0,
            "estadistico": float("nan"),
            "p_valor": float("nan"),
            "decision_texto": "No se encontró la columna 'acuerdo_ampliacion'.",
        }

    datos = serie.dropna()
    if len(datos) < 3:
        return {
            "n": len(datos),
            "estadistico": float("nan"),
            "p_valor": float("nan"),
            "decision_texto": "No hay suficientes datos para aplicar Shapiro-Wilk (mínimo 3 observaciones).",
        }

    estadistico, p_valor = stats.shapiro(datos)
    return {
        "n": len(datos),
        "estadistico": float(estadistico),
        "p_valor": float(p_valor),
        "decision_texto": _interpretar_p_valor(p_valor, alpha),
    }


def prueba_normalidad_residuos(modelo, alpha: float = ALPHA_DEFAULT) -> Dict[str, float | str]:
    """Ejecuta Shapiro-Wilk sobre los residuos de un modelo de statsmodels."""

    if modelo is None:
        return {
            "n": 0,
            "estadistico": float("nan"),
            "p_valor": float("nan"),
            "decision_texto": "No se recibió un modelo ANOVA válido para evaluar los residuos.",
        }

    residuos = getattr(modelo, "resid", None)
    if residuos is None:
        return {
            "n": 0,
            "estadistico": float("nan"),
            "p_valor": float("nan"),
            "decision_texto": "El objeto del modelo no expone residuos para aplicar la prueba.",
        }

    residuos = pd.Series(residuos).dropna()
    if len(residuos) < 3:
        return {
            "n": len(residuos),
            "estadistico": float("nan"),
            "p_valor": float("nan"),
            "decision_texto": "Se requieren al menos 3 residuos no nulos para aplicar Shapiro-Wilk.",
        }

    estadistico, p_valor = stats.shapiro(residuos)
    return {
        "n": len(residuos),
        "estadistico": float(estadistico),
        "p_valor": float(p_valor),
        "decision_texto": _interpretar_p_valor(p_valor, alpha),
    }
