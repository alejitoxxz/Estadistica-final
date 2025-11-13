"""Pruebas de hipótesis asociadas al proyecto."""
from __future__ import annotations

from typing import Dict

import pandas as pd
from scipy import stats


def prueba_media_mayor_que_5(
    serie: pd.Series, mu0: float = 5.0, alpha: float = 0.05
) -> Dict[str, float]:
    """Realiza una prueba t de una muestra para H1: media > mu0."""
    datos = serie.dropna().astype(float)
    if datos.empty:
        raise ValueError("La serie proporcionada no contiene datos válidos para la prueba.")

    media_muestral = datos.mean()
    resultado_t = stats.ttest_1samp(datos, popmean=mu0, alternative="two-sided")
    estadistico_t = float(resultado_t.statistic)
    p_valor_bilateral = float(resultado_t.pvalue)

    if media_muestral > mu0:
        p_valor_unilateral = p_valor_bilateral / 2
    else:
        p_valor_unilateral = 1 - (p_valor_bilateral / 2)

    decision = "Rechazar H0" if p_valor_unilateral < alpha else "No rechazar H0"

    print("Resultado de la prueba t de una muestra (cola derecha):")
    print(f"Media muestral = {media_muestral:.3f}")
    print(f"Estadístico t = {estadistico_t:.3f}")
    print(f"p-valor unilateral = {p_valor_unilateral:.4f}")
    if decision == "Rechazar H0":
        print(
            "Conclusión: existe evidencia estadísticamente significativa para afirmar "
            "que la media poblacional es mayor que", mu0,
            "con un nivel de significancia de", alpha,
        )
    else:
        print(
            "Conclusión: no se encontró evidencia suficiente para afirmar que la media "
            "poblacional supere", mu0,
            "con un nivel de significancia de", alpha,
        )

    return {
        "media_muestral": float(media_muestral),
        "estadistico_t": estadistico_t,
        "p_valor_unilateral": float(p_valor_unilateral),
        "decision": decision,
        "alpha": float(alpha),
        "mu0": float(mu0),
    }
