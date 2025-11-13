"""Funciones para ajustar y reportar el diseño factorial (ANOVA 2x3)."""
from __future__ import annotations

import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols


def anova_2x3(df: pd.DataFrame):
    """Ajusta un modelo ANOVA 2x3 para 'acuerdo_ampliacion'.

    Factores:
        - frecuencia_viaje (Frecuente / No frecuente)
        - grupo_edad (Joven / Adulto / Adulto mayor)

    La función:
        - filtra registros con grupo_edad == "Sin categoría"
        - verifica que haya al menos 2 niveles en cada factor
        - intenta ajustar el modelo:
              acuerdo_ampliacion ~ C(frecuencia_viaje) * C(grupo_edad)
        - imprime la tabla ANOVA si es posible
        - si no se puede ajustar, imprime una explicación en español.
    """
    print("===== ANOVA 2x3 =====")

    # Trabajamos sobre una copia para no tocar el DataFrame original
    df_anova = df.copy()

    # Eliminar filas con grupo_edad "Sin categoría" (edades fuera de rango, etc.)
    if "grupo_edad" not in df_anova.columns or "frecuencia_viaje" not in df_anova.columns:
        print(
            "No se encontraron las columnas 'grupo_edad' y/o 'frecuencia_viaje' en el DataFrame. "
            "No es posible realizar la ANOVA 2x3."
        )
        return None

    df_anova = df_anova[df_anova["grupo_edad"] != "Sin categoría"]

    # Eliminar filas con datos faltantes en las variables clave
    df_anova = df_anova.dropna(
        subset=["acuerdo_ampliacion", "frecuencia_viaje", "grupo_edad"]
    )

    # Revisar cuántos niveles tiene realmente cada factor
    niveles_frec = df_anova["frecuencia_viaje"].unique()
    niveles_edad = df_anova["grupo_edad"].unique()

    print("Niveles en 'frecuencia_viaje':", niveles_frec)
    print("Niveles en 'grupo_edad':", niveles_edad)

    if len(niveles_frec) < 2 or len(niveles_edad) < 2:
        print(
            "\nNo se puede realizar la ANOVA 2x3 porque alguno de los factores "
            "no tiene al menos 2 niveles en los datos filtrados."
        )
        print(
            "Esto suele ocurrir cuando, por ejemplo, casi todos los encuestados "
            "pertenecen a un solo grupo (p. ej., solo 'No frecuente')."
        )
        print(
            "Puedes mencionarlo en el informe como una LIMITACIÓN del diseño: "
            "no se logró cubrir adecuadamente todos los tratamientos del diseño factorial 2x3."
        )
        return None

    # Si hay suficientes niveles, intentamos ajustar el modelo
    try:
        modelo = ols(
            "acuerdo_ampliacion ~ C(frecuencia_viaje) * C(grupo_edad)",
            data=df_anova,
        ).fit()

        tabla_anova = sm.stats.anova_lm(modelo, typ=2)
        print("\nTabla ANOVA (tipo II):")
        print(tabla_anova)

        print(
            "\nInterpretación general sugerida:\n"
            "- La fila 'C(frecuencia_viaje)' indica si, en promedio, los viajeros frecuentes\n"
            "  y no frecuentes difieren en su grado de acuerdo con la ampliación.\n"
            "- La fila 'C(grupo_edad)' indica si los distintos grupos etarios difieren en su media.\n"
            "- La fila 'C(frecuencia_viaje):C(grupo_edad)' indica si hay interacción entre ambos factores.\n"
        )

        return tabla_anova
    except Exception as e:
        print(
            "No fue posible ajustar el modelo ANOVA 2x3 por un problema numérico o de diseño."
        )
        print("Detalle técnico del error:", repr(e))
        print(
            "Puedes mencionar en el informe que, aunque se intentó ajustar una ANOVA 2x3, "
            "la estructura real de los datos (tratamientos vacíos o casi vacíos) "
            "impidió realizar el análisis factorial completo."
        )
        return None
