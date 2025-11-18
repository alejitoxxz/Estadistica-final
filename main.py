"""Script principal para ejecutar el análisis estadístico completo."""
from __future__ import annotations

from pathlib import Path

from src.cargar_datos import cargar_excel
from src.config import DATA_PATH
from src.descriptivos import resumen_general, resumen_por_grupo
from src.diagnosticos import prueba_normalidad_acuerdo, prueba_normalidad_residuos
from src.diseno_factorial import anova_2x3
from src.graficos import (
    guardar_barras_por_tratamiento,
    guardar_boxplots_por_factores,
    guardar_histograma_acuerdo,
    guardar_mapa_correlacion,
)
from src.intervalos_confianza import intervalo_confianza_media, intervalo_confianza_proporcion
from src.limpiar_preparar import preparar_datos
from src.prueba_hipotesis import prueba_media_mayor_que_5
from src.reporte_markdown import generar_reporte_markdown


DATA_DIR = Path("data")
FIGURAS_DIR = Path("figuras")
REPORTE_PATH = Path("reporte_estadistico.md")


def verificar_estructura() -> bool:
    """Comprueba que existan la carpeta de datos y el archivo Excel."""
    if not DATA_DIR.exists():
        print("Error: la carpeta 'data/' no existe. Crea la carpeta y coloca el Excel allí.")
        return False

    if not DATA_PATH.exists():
        print(
            "Error: no se encontró el archivo 'data/Respuestas_final.xlsx'. "
            "Verifica el nombre y su ubicación."
        )
        return False

    return True


def imprimir_intervalo(resultado: dict[str, float], descripcion: str) -> None:
    """Imprime de forma formateada un intervalo de confianza."""
    print(descripcion)
    print(
        f"n = {resultado['n']:.0f}\n"
        f"Media/Proporción = {resultado.get('media', resultado.get('p_hat', float('nan'))):.3f}\n"
        f"Límite inferior = {resultado['limite_inferior']:.3f}\n"
        f"Límite superior = {resultado['limite_superior']:.3f}\n"
        f"Nivel de confianza = {100 * (1 - resultado['alpha']):.1f}%"
    )
    print()


def main() -> None:
    """Ejecuta todo el flujo de análisis estadístico."""
    if not verificar_estructura():
        return

    FIGURAS_DIR.mkdir(exist_ok=True)
    for archivo in FIGURAS_DIR.glob("*.png"):
        archivo.unlink()

    print("===== CARGA DE DATOS =====")
    df = cargar_excel()
    print()

    print("===== PREPARACIÓN DE DATOS =====")
    df_preparado = preparar_datos(df)
    print("Columnas disponibles tras la preparación:")
    print(list(df_preparado.columns))
    print()

    print("===== ANÁLISIS DESCRIPTIVO =====")
    descriptivos = resumen_general(df_preparado)
    resumen_grupos = resumen_por_grupo(
        df_preparado, ["frecuencia_viaje", "grupo_edad", "tratamiento"]
    )

    print("===== INTERVALO DE CONFIANZA PARA LA MEDIA =====")
    ic_media = intervalo_confianza_media(df_preparado["acuerdo_ampliacion"])
    imprimir_intervalo(ic_media, "Intervalo de confianza para la media de acuerdo con la ampliación:")

    print("===== INTERVALO DE CONFIANZA PARA LA PROPORCIÓN A FAVOR =====")
    ic_prop = intervalo_confianza_proporcion(df_preparado["a_favor"])
    imprimir_intervalo(ic_prop, "Intervalo de confianza para la proporción de personas a favor:")

    print("===== PRUEBA DE HIPÓTESIS μ > 5 =====")
    resultado_prueba = prueba_media_mayor_que_5(df_preparado["acuerdo_ampliacion"])
    print()

    print("===== ANOVA 2x3 =====")
    resultado_anova = anova_2x3(df_preparado)

    print("===== PRUEBAS DE NORMALIDAD =====")
    resultado_normalidad: dict[str, dict[str, float | str]] = {}
    resultado_normalidad["acuerdo"] = prueba_normalidad_acuerdo(df_preparado)
    if resultado_anova.get("modelo") is not None:
        resultado_normalidad["residuos_anova"] = prueba_normalidad_residuos(
            resultado_anova.get("modelo")
        )

    columnas_opinion = ["acuerdo_ampliacion", "p2_economia", "p3_necesidad"]
    df_correlaciones = df_preparado[columnas_opinion].corr()

    print("===== GRÁFICAS =====")
    rutas_figuras: dict[str, Path] = {}
    rutas_figuras["hist_acuerdo"] = guardar_histograma_acuerdo(df_preparado, FIGURAS_DIR)
    rutas_box = guardar_boxplots_por_factores(df_preparado, FIGURAS_DIR)
    rutas_figuras.update(rutas_box)
    rutas_figuras["barras_tratamientos"] = guardar_barras_por_tratamiento(
        df_preparado, FIGURAS_DIR
    )
    rutas_figuras["correlaciones"] = guardar_mapa_correlacion(df_preparado, FIGURAS_DIR)

    resultados = {
        "n_muestra": int(len(df_preparado)),
        "descriptivos": descriptivos,
        "resumen_por_grupo": resumen_grupos,
        "intervalos": {
            "media": ic_media,
            "proporcion": ic_prop,
        },
        "prueba_hipotesis": resultado_prueba,
        "anova": resultado_anova,
        "normalidad": resultado_normalidad,
        "correlaciones": df_correlaciones,
    }

    generar_reporte_markdown(resultados, rutas_figuras, REPORTE_PATH)

    print(
        "Análisis completado. Las gráficas se guardaron en la carpeta 'figuras/' y se "
        "generó el archivo 'reporte_estadistico.md'."
    )


if __name__ == "__main__":
    main()
