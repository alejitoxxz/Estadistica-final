"""Configuración general del proyecto de estadística inferencial."""
from __future__ import annotations

from pathlib import Path

# Ruta relativa al archivo con las respuestas de la encuesta.
DATA_PATH: Path = Path("data") / "Respuestas_final.xlsx"

# Mapa DEFINITIVO de columnas, usando los encabezados EXACTOS del Excel:
COLUMN_MAP: dict[str, str] = {
    "edad": "Cuál es tu edad?",
    "viajes_anio": "Cuántas veces al año visitas el aeropuerto José María Córdova de Rionegro?",
    "p1_acuerdo": "En una escala de 1 a 10, ¿qué tan de acuerdo estás con la ampliación del aeropuerto José María Córdova?",
    "p2_economia": "En una escala de 1 a 10, ¿qué tanto crees que la economía del oriente antioqueño puede mejorar con esta obra?",
    "p3_necesidad": "En una escala de 1 a 10, ¿qué tan necesaria consideras esta obra?",
}

# IMPORTANTE:
# - Los valores (la parte derecha) deben coincidir EXACTAMENTE con los encabezados del Excel.
# - Respeta tildes, signos de interrogación, comas y espacios.
