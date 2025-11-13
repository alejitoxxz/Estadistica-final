"""Script principal para ejecutar el análisis estadístico completo."""
from __future__ import annotations

from pathlib import Path

from src.cargar_datos import cargar_excel
from src.config import DATA_PATH
from src.descriptivos import resumen_general, resumen_por_grupo
from src.diseno_factorial import anova_2x3
from src.graficos import barras_por_tratamiento, boxplots_por_factores, histograma_acuerdo
from src.intervalos_confianza import intervalo_confianza_media, intervalo_confianza_proporcion
from src.limpiar_preparar import preparar_datos
from src.prueba_hipotesis import prueba_media_mayor_que_5


DATA_DIR = Path("data")
FIGURAS_DIR = Path("figuras")


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

    print("===== CARGA DE DATOS =====")
    df = cargar_excel()
    print()

    print("===== PREPARACIÓN DE DATOS =====")
    df_preparado = preparar_datos(df)
    print("Columnas disponibles tras la preparación:")
    print(list(df_preparado.columns))
    print()

    print("===== ANÁLISIS DESCRIPTIVO =====")
    resumen_general(df_preparado)
    resumen_por_grupo(df_preparado, ["frecuencia_viaje", "grupo_edad", "tratamiento"])

    print("===== INTERVALO DE CONFIANZA PARA LA MEDIA =====")
    ic_media = intervalo_confianza_media(df_preparado["acuerdo_ampliacion"])
    imprimir_intervalo(ic_media, "Intervalo de confianza para la media de acuerdo con la ampliación:")

    print("===== INTERVALO DE CONFIANZA PARA LA PROPORCIÓN A FAVOR =====")
    ic_prop = intervalo_confianza_proporcion(df_preparado["a_favor"])
    imprimir_intervalo(ic_prop, "Intervalo de confianza para la proporción de personas a favor:")

    print("===== PRUEBA DE HIPÓTESIS μ > 5 =====")
    prueba_media_mayor_que_5(df_preparado["acuerdo_ampliacion"])
    print()

    print("===== ANOVA 2x3 =====")
    anova_2x3(df_preparado)

    print("===== GRÁFICAS =====")
    histograma_acuerdo(df_preparado)
    boxplots_por_factores(df_preparado)
    barras_por_tratamiento(df_preparado)

    print("Análisis completado. Las gráficas se mostraron en pantalla. Puedes guardarlas"
          " manualmente desde la ventana de visualización si lo deseas.")


if __name__ == "__main__":
    main()
