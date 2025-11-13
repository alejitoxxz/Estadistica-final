"""Funciones para generar visualizaciones del proyecto."""
from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set(style="whitegrid")


def histograma_acuerdo(df: pd.DataFrame) -> None:
    """Muestra un histograma de la variable de acuerdo con la ampliación."""
    plt.figure(figsize=(8, 5))
    sns.histplot(df["acuerdo_ampliacion"].dropna(), bins=10, kde=True, color="#1f77b4")
    plt.title("Distribución del acuerdo con la ampliación")
    plt.xlabel("Calificación (1-10)")
    plt.ylabel("Frecuencia")
    plt.tight_layout()
    plt.show()


def boxplots_por_factores(df: pd.DataFrame) -> None:
    """Genera boxplots por frecuencia de viaje y por grupo de edad."""
    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    sns.boxplot(data=df, x="frecuencia_viaje", y="acuerdo_ampliacion", palette="Set2")
    plt.title("Acuerdo según frecuencia de viaje")
    plt.xlabel("Frecuencia de viaje")
    plt.ylabel("Calificación")

    plt.subplot(1, 2, 2)
    sns.boxplot(data=df, x="grupo_edad", y="acuerdo_ampliacion", palette="Set3")
    plt.title("Acuerdo según grupo de edad")
    plt.xlabel("Grupo de edad")
    plt.ylabel("Calificación")

    plt.tight_layout()
    plt.show()


def barras_por_tratamiento(df: pd.DataFrame) -> None:
    """Grafica la media y el error estándar por tratamiento."""
    resumen = (
        df.dropna(subset=["acuerdo_ampliacion", "tratamiento"])
        .groupby("tratamiento")
        ["acuerdo_ampliacion"]
        .agg(["mean", "count", "std"])
        .rename(columns={"mean": "media", "count": "n", "std": "desviacion"})
    )

    resumen["error_estandar"] = resumen["desviacion"] / resumen["n"].pow(0.5)
    resumen = resumen.sort_values("media", ascending=False)

    plt.figure(figsize=(10, 6))
    posiciones = range(len(resumen))
    plt.bar(posiciones, resumen["media"], yerr=resumen["error_estandar"], color="#4c72b0", capsize=5)
    plt.xticks(posiciones, resumen.index, rotation=45, ha="right")
    plt.title("Promedio de acuerdo por tratamiento")
    plt.xlabel("Tratamiento")
    plt.ylabel("Media de la calificación")
    plt.tight_layout()
    plt.show()
