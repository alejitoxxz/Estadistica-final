"""Funciones para cargar los datos de la encuesta desde el archivo Excel."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd

from .config import DATA_PATH


def cargar_excel(path: Optional[Path] = None) -> pd.DataFrame:
    """Carga el archivo de respuestas y muestra las columnas disponibles.

    Parameters
    ----------
    path:
        Ruta alternativa al archivo de Excel. Si es ``None`` se usa el valor
        definido en :data:`src.config.DATA_PATH`.

    Returns
    -------
    pandas.DataFrame
        DataFrame con la información tal como aparece en el Excel. Si ocurre un
        error durante la carga, se propaga la excepción después de mostrar un
        mensaje informativo.
    """

    ruta_excel = path or DATA_PATH

    try:
        df = pd.read_excel(ruta_excel)
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"No se encontró el archivo '{ruta_excel}'. Verifica la carpeta 'data/'."
        ) from exc
    except Exception as exc:  # pragma: no cover - comunicación con el usuario
        raise RuntimeError(
            f"Ocurrió un error inesperado al leer el archivo '{ruta_excel}': {exc}"
        ) from exc

    print("Columnas encontradas en el Excel:")
    print(list(df.columns))

    return df
