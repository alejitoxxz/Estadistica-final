"""Funciones para ajustar y reportar el diseño factorial (ANOVA 2x3)."""
from __future__ import annotations

from typing import Dict

import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols


def _generar_conclusion(tabla_anova: pd.DataFrame) -> str:
    """Crea una interpretación breve a partir de la tabla ANOVA."""

    if "PR(>F)" not in tabla_anova.columns:
        return (
            "La tabla ANOVA no contiene valores p. Revisa los resultados manualmente "
            "para interpretar los efectos principales y la interacción."
        )

    etiquetas = {
        "C(frecuencia_viaje)": "el efecto principal de la frecuencia de viaje",
        "C(grupo_edad)": "el efecto principal del grupo etario",
        "C(frecuencia_viaje):C(grupo_edad)": "la interacción entre frecuencia de viaje y grupo etario",
    }

    conclusiones = []
    for fila, descripcion in etiquetas.items():
        if fila in tabla_anova.index:
            p_valor = tabla_anova.loc[fila, "PR(>F)"]
            if p_valor < 0.05:
                conclusiones.append(
                    f"Se encontró evidencia de que {descripcion} es significativa (p = {p_valor:.3f})."
                )
            else:
                conclusiones.append(
                    f"No se encontró evidencia significativa para {descripcion} (p = {p_valor:.3f})."
                )

    if not conclusiones:
        return (
            "La tabla ANOVA no contiene las filas esperadas para evaluar los efectos del diseño factorial."
        )

    return " ".join(conclusiones)


def anova_2x3(df: pd.DataFrame) -> Dict[str, object]:
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
    # Trabajamos sobre una copia para no tocar el DataFrame original
    df_anova = df.copy()

    # Eliminar filas con grupo_edad "Sin categoría" (edades fuera de rango, etc.)
    if "grupo_edad" not in df_anova.columns or "frecuencia_viaje" not in df_anova.columns:
        print(
            "No se encontraron las columnas 'grupo_edad' y/o 'frecuencia_viaje' en el DataFrame. "
            "No es posible realizar la ANOVA 2x3."
        )
        return {
            "exito": False,
            "mensaje": "Faltan columnas necesarias para ejecutar la ANOVA 2x3.",
            "tabla": None,
            "tabla_texto": "",
            "conclusion": "No fue posible estimar el modelo por ausencia de factores clave.",
        }

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
        return {
            "exito": False,
            "mensaje": "Los datos no contienen niveles suficientes para ambos factores.",
            "tabla": None,
            "tabla_texto": "",
            "conclusion": (
                "No se pudo ajustar el modelo ANOVA porque algún factor quedó representado con "
                "un único nivel tras el filtrado de datos."
            ),
        }

    # Si hay suficientes niveles, intentamos ajustar el modelo
    try:
        modelo = ols(
            "acuerdo_ampliacion ~ C(frecuencia_viaje) * C(grupo_edad)",
            data=df_anova,
        ).fit()

        tabla_anova = sm.stats.anova_lm(modelo, typ=2)
        print("\nTabla ANOVA (tipo II):")
        print(tabla_anova)

        conclusion = _generar_conclusion(tabla_anova)
        print("\n" + conclusion)

        return {
            "exito": True,
            "mensaje": "Modelo ANOVA ajustado correctamente.",
            "tabla": tabla_anova,
            "tabla_texto": tabla_anova.to_string(),
            "conclusion": conclusion,
        }
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
        return {
            "exito": False,
            "mensaje": "Error numérico al ajustar el modelo ANOVA 2x3.",
            "tabla": None,
            "tabla_texto": "",
            "conclusion": (
                "Aunque se intentó ajustar el modelo ANOVA 2×3, surgieron problemas numéricos "
                "que impidieron obtener resultados válidos."
            ),
        }
