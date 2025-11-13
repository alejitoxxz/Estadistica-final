"""Modelos y análisis para el diseño factorial 2x3."""
from __future__ import annotations

import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols


SIGNIFICANCIA_POR_DEFECTO: float = 0.05


def anova_2x3(
    df: pd.DataFrame, alpha: float = SIGNIFICANCIA_POR_DEFECTO
) -> pd.DataFrame:
    """Ajusta un modelo ANOVA 2x3 y muestra la tabla de análisis de varianza."""
    columnas_necesarias = {"acuerdo_ampliacion", "frecuencia_viaje", "grupo_edad"}
    faltantes = columnas_necesarias - set(df.columns)
    if faltantes:
        faltantes_str = ", ".join(sorted(faltantes))
        raise KeyError(
            f"Faltan columnas necesarias para el ANOVA: {faltantes_str}. "
            "Verifica el proceso de preparación de datos."
        )

    df_modelo = df.dropna(subset=["acuerdo_ampliacion", "frecuencia_viaje", "grupo_edad"])
    if df_modelo.empty:
        raise ValueError("No hay datos suficientes para ajustar el modelo ANOVA.")

    modelo = ols(
        "acuerdo_ampliacion ~ C(frecuencia_viaje) * C(grupo_edad)", data=df_modelo
    ).fit()
    tabla_anova = sm.stats.anova_lm(modelo, typ=2)

    print("Tabla ANOVA (Tipo II):")
    print(tabla_anova)
    print()

    for factor in ["C(frecuencia_viaje)", "C(grupo_edad)", "C(frecuencia_viaje):C(grupo_edad)"]:
        if factor in tabla_anova.index:
            p_valor = tabla_anova.loc[factor, "PR(>F)"]
            conclusion = "significativo" if p_valor < alpha else "no significativo"
            print(
                f"El efecto de {factor} es {conclusion} (p = {p_valor:.4f})"
                f" con α = {alpha}."
            )
    print()

    return tabla_anova
