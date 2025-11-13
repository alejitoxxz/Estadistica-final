"""Generación automática del reporte estadístico en formato Markdown."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pandas as pd


def _formatear_numero(valor: Any, decimales: int = 2) -> str:
    """Devuelve ``valor`` formateado con ``decimales`` decimales."""
    if isinstance(valor, (int, float)) and not pd.isna(valor):
        formato = f"{{:.{decimales}f}}"
        return formato.format(valor)
    return "N/A"


def _formatear_moda(moda: Any) -> str:
    """Formatea la moda (o lista de modas) para mostrarla en el reporte."""
    if moda is None:
        return "N/A"
    # Si viene como escalar
    if isinstance(moda, (int, float)):
        return _formatear_numero(moda)
    # Si viene como lista / serie
    try:
        lista = list(moda)
    except TypeError:
        return str(moda)
    if len(lista) == 0:
        return "N/A"
    return ", ".join(_formatear_numero(valor) for valor in lista)


def _ruta_a_posix(ruta: Path | None) -> str:
    """Convierte una ruta a formato POSIX para usar en Markdown."""
    if ruta is None:
        return ""
    return ruta.as_posix()


def generar_reporte_markdown(
    resultados: Dict[str, Any], rutas_figuras: Dict[str, Path], output_path: Path
) -> None:
    """Escribe un reporte Markdown con los resultados del análisis estadístico."""

    output_path.parent.mkdir(parents=True, exist_ok=True)

    descriptivos = resultados.get("descriptivos", {})
    acuerdo = descriptivos.get("acuerdo_ampliacion", {})
    economia = descriptivos.get("p2_economia", {})
    necesidad = descriptivos.get("p3_necesidad", {})

    ic_media = resultados.get("intervalos", {}).get("media", {})
    ic_prop = resultados.get("intervalos", {}).get("proporcion", {})

    prueba = resultados.get("prueba_hipotesis", {})
    anova = resultados.get("anova", {})

    n_muestra = resultados.get("n_muestra", 0)

    # Interpretaciones de intervalos
    interpretacion_media = (
        "Con un {nivel:.0f} % de confianza, el verdadero promedio poblacional de acuerdo con "
        "la ampliación del aeropuerto se encuentra entre {li} y {ls}."
    ).format(
        nivel=(1 - ic_media.get("alpha", 0)) * 100,
        li=_formatear_numero(ic_media.get("limite_inferior")),
        ls=_formatear_numero(ic_media.get("limite_superior")),
    )

    interpretacion_prop = (
        "Con un {nivel:.0f} % de confianza, la proporción real de personas a favor de la ampliación "
        "se ubica entre {li} y {ls}."
    ).format(
        nivel=(1 - ic_prop.get("alpha", 0)) * 100,
        li=_formatear_numero(ic_prop.get("limite_inferior")),
        ls=_formatear_numero(ic_prop.get("limite_superior")),
    )

    # Conclusión prueba de hipótesis
    if prueba.get("decision") == "Rechazar H0":
        conclusion_prueba = (
            "Se rechaza la hipótesis nula y se concluye que la media poblacional supera a "
            f"{_formatear_numero(prueba.get('mu0'), 2)}."
        )
    else:
        conclusion_prueba = (
            "No se rechaza la hipótesis nula; los datos no aportan evidencia suficiente para afirmar "
            f"que la media exceda a {_formatear_numero(prueba.get('mu0'), 2)}."
        )

    tabla_anova_texto = anova.get("tabla_texto", "")
    conclusion_anova = anova.get("conclusion", "No se obtuvo un resultado interpretable del ANOVA.")
    mensaje_anova = anova.get("mensaje", "")

    # Rutas de figuras
    ruta_hist = _ruta_a_posix(rutas_figuras.get("hist_acuerdo"))
    ruta_box_frec = _ruta_a_posix(rutas_figuras.get("box_frecuencia"))
    ruta_box_edad = _ruta_a_posix(rutas_figuras.get("box_edad"))
    ruta_barras = _ruta_a_posix(rutas_figuras.get("barras_tratamientos"))

    # Conclusiones generales
    conclusiones_generales = [
        (
            "El grado de acuerdo con la ampliación presenta una media de "
            f"{_formatear_numero(acuerdo.get('media'))}, lo que sugiere una valoración favorable."
        ),
        (
            "Las percepciones sobre el impacto económico ({media_economia}) y la necesidad de la obra ({media_necesidad}) "
            "también muestran niveles altos en la escala de 1 a 10."
        ).format(
            media_economia=_formatear_numero(economia.get("media")),
            media_necesidad=_formatear_numero(necesidad.get("media")),
        ),
        (
            "La prueba t con hipótesis H0: μ ≤ {mu0} arroja p = {p_valor}, {decision}."
        ).format(
            mu0=_formatear_numero(prueba.get("mu0")),
            p_valor=_formatear_numero(prueba.get("p_valor_unilateral"), 4),
            decision=(
                "lo que respalda la afirmación de que la media supera el umbral."
                if prueba.get("decision") == "Rechazar H0"
                else "por lo que no se evidencia una media superior al umbral."
            ),
        ),
        conclusion_anova,
    ]

    # =========================
    # Construcción del Markdown
    # =========================
    contenido = f"""# Informe de resultados - Proyecto de Estadística

## 1. Descripción general de la muestra

- Tamaño de la muestra: {n_muestra} encuestados.
- Variables de interés:
  - Grado de acuerdo con la ampliación (1–10)
  - Percepción de impacto en la economía (1–10)
  - Percepción de necesidad de la obra (1–10)
  - Factores: frecuencia de viaje y grupo etario.

## 2. Análisis descriptivo

### 2.1. Grado de acuerdo con la ampliación

- n = {acuerdo.get('n', 'N/A')}
- Media = {_formatear_numero(acuerdo.get('media'))}
- Mediana = {_formatear_numero(acuerdo.get('mediana'))}
- Moda = {_formatear_moda(acuerdo.get('moda'))}
- Desviación estándar = {_formatear_numero(acuerdo.get('desviacion'))}
- Cuartiles: Q1 = {_formatear_numero(acuerdo.get('q1'))}, Q2 = {_formatear_numero(acuerdo.get('q2'))}, Q3 = {_formatear_numero(acuerdo.get('q3'))}

### 2.2. Impacto en la economía

- n = {economia.get('n', 'N/A')}
- Media = {_formatear_numero(economia.get('media'))}
- Mediana = {_formatear_numero(economia.get('mediana'))}
- Moda = {_formatear_moda(economia.get('moda'))}
- Desviación estándar = {_formatear_numero(economia.get('desviacion'))}
- Cuartiles: Q1 = {_formatear_numero(economia.get('q1'))}, Q2 = {_formatear_numero(economia.get('q2'))}, Q3 = {_formatear_numero(economia.get('q3'))}

### 2.3. Percepción de necesidad

- n = {necesidad.get('n', 'N/A')}
- Media = {_formatear_numero(necesidad.get('media'))}
- Mediana = {_formatear_numero(necesidad.get('mediana'))}
- Moda = {_formatear_moda(necesidad.get('moda'))}
- Desviación estándar = {_formatear_numero(necesidad.get('desviacion'))}
- Cuartiles: Q1 = {_formatear_numero(necesidad.get('q1'))}, Q2 = {_formatear_numero(necesidad.get('q2'))}, Q3 = {_formatear_numero(necesidad.get('q3'))}

## 3. Intervalos de confianza

### 3.1. Media del grado de acuerdo con la ampliación

- n = {_formatear_numero(ic_media.get('n'), 0)}
- Media = {_formatear_numero(ic_media.get('media'))}
- IC 95%: [{_formatear_numero(ic_media.get('limite_inferior'))}, {_formatear_numero(ic_media.get('limite_superior'))}]

{interpretacion_media}

### 3.2. Proporción de personas a favor de la ampliación

- Definición de "a favor": calificación ≥ 6.
- n = {_formatear_numero(ic_prop.get('n'), 0)}
- Proporción muestral = {_formatear_numero(ic_prop.get('p_hat'))}
- IC 95%: [{_formatear_numero(ic_prop.get('limite_inferior'))}, {_formatear_numero(ic_prop.get('limite_superior'))}]

{interpretacion_prop}

## 4. Prueba de hipótesis principal

- Hipótesis:
  - H0: μ ≤ {_formatear_numero(prueba.get('mu0'))}
  - H1: μ > {_formatear_numero(prueba.get('mu0'))}
- Estadístico t = {_formatear_numero(prueba.get('estadistico_t'))}
- p-valor (cola derecha) = {_formatear_numero(prueba.get('p_valor_unilateral'), 4)}
- Conclusión: {conclusion_prueba}

## 5. ANOVA factorial 2×3 (Frecuencia de viaje × Grupo etario)

"""

    # Tabla ANOVA como bloque de código Markdown
    if tabla_anova_texto:
        contenido += "```\n"
        contenido += tabla_anova_texto
        contenido += "\n```\n\n"

    if mensaje_anova:
        contenido += f"{mensaje_anova}\n\n"

    contenido += f"Interpretación: {conclusion_anova}\n\n"

    # Gráficas
    contenido += "## 6. Gráficas\n\n"
    if ruta_hist:
        contenido += f"![Histograma del acuerdo]({ruta_hist})\n\n"
    if ruta_box_frec:
        contenido += f"![Boxplot por frecuencia]({ruta_box_frec})\n\n"
    if ruta_box_edad:
        contenido += f"![Boxplot por grupo etario]({ruta_box_edad})\n\n"
    if ruta_barras:
        contenido += f"![Medias por tratamiento]({ruta_barras})\n\n"

    # Conclusiones finales
    contenido += "## 7. Conclusiones generales\n\n"
    for conclusion in conclusiones_generales:
        contenido += f"- {conclusion}\n"

    contenido += "\n"

    # Escribir archivo
    output_path.write_text(contenido, encoding="utf-8")
