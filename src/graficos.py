"""Funciones para generar y guardar visualizaciones del proyecto."""
from __future__ import annotations

from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

sns.set_theme(style="whitegrid")


def _guardar_figura(fig: plt.Figure, ruta: Path, mostrar: bool = False) -> Path:
    """Guarda una figura de Matplotlib en ``ruta`` y la cierra.

    Parameters
    ----------
    fig:
        Objeto :class:`matplotlib.figure.Figure` que se desea guardar.
    ruta:
        Ruta de destino para la imagen.
    mostrar:
        Si es ``True`` se muestra la figura después de guardarla.
    """

    ruta.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(ruta, dpi=300, bbox_inches="tight")
    if mostrar:  # pragma: no cover - uso interactivo opcional
        plt.show()
    plt.close(fig)
    return ruta


def guardar_histograma_acuerdo(df: pd.DataFrame, output_dir: Path, mostrar: bool = False) -> Path:
    """Genera y guarda el histograma del acuerdo con la ampliación."""

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(
        df["acuerdo_ampliacion"].dropna(),
        bins=10,
        kde=True,
        color="#4c72b0",
        ax=ax,
    )
    ax.set_title("Histograma del grado de acuerdo con la ampliación", fontsize=14)
    ax.set_xlabel("Calificación (1–10)", fontsize=12)
    ax.set_ylabel("Número de personas", fontsize=12)

    ruta = output_dir / "hist_acuerdo.png"
    return _guardar_figura(fig, ruta, mostrar)


def guardar_boxplots_por_factores(
    df: pd.DataFrame, output_dir: Path, mostrar: bool = False
) -> Dict[str, Path]:
    """Guarda los boxplots de acuerdo por frecuencia de viaje y grupo etario."""

    rutas: Dict[str, Path] = {}

    fig_frec, ax_frec = plt.subplots(figsize=(10, 6))
    sns.boxplot(
        data=df,
        x="frecuencia_viaje",
        y="acuerdo_ampliacion",
        palette="Set2",
        ax=ax_frec,
    )
    ax_frec.set_title("Acuerdo según frecuencia de viaje", fontsize=14)
    ax_frec.set_xlabel("Frecuencia de viaje", fontsize=12)
    ax_frec.set_ylabel("Calificación (1–10)", fontsize=12)
    ax_frec.tick_params(axis="x", rotation=10)
    rutas["box_frecuencia"] = _guardar_figura(
        fig_frec, output_dir / "box_frecuencia.png", mostrar
    )

    fig_edad, ax_edad = plt.subplots(figsize=(10, 6))
    sns.boxplot(
        data=df,
        x="grupo_edad",
        y="acuerdo_ampliacion",
        palette="Set3",
        ax=ax_edad,
    )
    ax_edad.set_title("Acuerdo según grupo etario", fontsize=14)
    ax_edad.set_xlabel("Grupo de edad", fontsize=12)
    ax_edad.set_ylabel("Calificación (1–10)", fontsize=12)
    ax_edad.tick_params(axis="x", rotation=15)
    rutas["box_edad"] = _guardar_figura(fig_edad, output_dir / "box_edad.png", mostrar)

    return rutas


def guardar_barras_por_tratamiento(
    df: pd.DataFrame, output_dir: Path, mostrar: bool = False
) -> Path:
    """Guarda la gráfica de barras con la media de acuerdo por tratamiento."""

    resumen = (
        df.dropna(subset=["acuerdo_ampliacion", "tratamiento"])
        .groupby("tratamiento")
        ["acuerdo_ampliacion"]
        .agg(["mean", "count", "std"])
        .rename(columns={"mean": "media", "count": "n", "std": "desviacion"})
    )

    resumen["error_estandar"] = resumen["desviacion"] / np.sqrt(resumen["n"])
    resumen = resumen.fillna(0.0)
    resumen_original = resumen.copy()

    orden_tratamientos = [
        "Frecuente - Joven",
        "Frecuente - Adulto",
        "Frecuente - Adulto mayor",
        "No frecuente - Joven",
        "No frecuente - Adulto",
        "No frecuente - Adulto mayor",
    ]
    tratamientos_presentes = [
        tratamiento for tratamiento in orden_tratamientos if tratamiento in resumen.index
    ]
    if tratamientos_presentes:
        resumen = resumen.loc[tratamientos_presentes]
        restantes = [
            tratamiento for tratamiento in resumen_original.index if tratamiento not in tratamientos_presentes
        ]
        if restantes:
            resumen = pd.concat([resumen, resumen_original.loc[restantes]])
    else:
        resumen = resumen_original.sort_index()

    fig, ax = plt.subplots(figsize=(10, 6))
    posiciones = np.arange(len(resumen))
    barras = ax.bar(
        posiciones,
        resumen["media"],
        yerr=resumen["error_estandar"],
        color="#55a868",
        capsize=5,
    )
    ax.set_xticks(posiciones)
    ax.set_xticklabels(resumen.index, rotation=20, ha="right")
    ax.set_title("Media del acuerdo por tratamiento 2×3", fontsize=14)
    ax.set_xlabel("Tratamiento", fontsize=12)
    ax.set_ylabel("Calificación promedio", fontsize=12)

    max_media = resumen["media"].max() if not resumen.empty else 0
    ax.set_ylim(0, max_media + 1)

    for barra, media in zip(barras, resumen["media"], strict=False):
        ax.text(
            barra.get_x() + barra.get_width() / 2,
            media + 0.05,
            f"{media:.2f}",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    ruta = output_dir / "barras_tratamientos.png"
    return _guardar_figura(fig, ruta, mostrar)
