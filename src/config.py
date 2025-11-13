"""Configuración general del proyecto de estadística inferencial."""
from __future__ import annotations

from pathlib import Path

# Ruta relativa al archivo con las respuestas de la encuesta.
DATA_PATH: Path = Path("data") / "Respuestas_final.xlsx"

# Mapa de columnas para adaptar los nombres reales del archivo Excel a nombres
# estándar dentro del proyecto. Ajusta los valores del diccionario una vez
# conozcas los encabezados reales del archivo (puedes obtenerlos ejecutando el
# script principal, que imprimirá la lista de columnas disponibles).
COLUMN_MAP: dict[str, str] = {
    "edad": "Edad",
    "viajes_anio": "Viajes_al_año",
    "p1_acuerdo": "Pregunta1",
    "p2_economia": "Pregunta2",
    "p3_necesidad": "Pregunta3",
}

# Puedes modificar libremente las claves del diccionario si quieres usar otros
# nombres estándar dentro del código. Lo importante es que los valores
# correspondan exactamente a los encabezados existentes en el Excel.
