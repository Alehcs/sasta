"""Exporta resultados cinematicos calculados en Python para validacion cruzada."""

import csv
from pathlib import Path

from calculo_cinematico_modulo import calcular_proyecciones
from ingesta_modulo import cargar_aeronaves_csv


BASE_DIR = Path(__file__).resolve().parent.parent
RUTA_CSV = BASE_DIR / "data" / "aeronaves_demo.csv"
RUTA_LOG = BASE_DIR / "logs" / "errores.log"
RUTA_SALIDA = BASE_DIR / "data" / "resultados_python.csv"
CAMPOS_SALIDA = (
    "id_a",
    "id_b",
    "tiempo_min",
    "distancia_horizontal_nm",
    "distancia_vertical_ft",
)


def exportar_resultados_python():
    """Genera el CSV de resultados cinematicos calculados en Python."""
    aeronaves, _descartados = cargar_aeronaves_csv(RUTA_CSV, RUTA_LOG)
    resultados = calcular_proyecciones(aeronaves)

    with RUTA_SALIDA.open("w", newline="", encoding="utf-8") as archivo_csv:
        escritor = csv.DictWriter(archivo_csv, fieldnames=CAMPOS_SALIDA)
        escritor.writeheader()

        for resultado in resultados:
            escritor.writerow(
                {
                    "id_a": resultado.id_a,
                    "id_b": resultado.id_b,
                    "tiempo_min": resultado.tiempo_min,
                    "distancia_horizontal_nm": resultado.distancia_horizontal_nm,
                    "distancia_vertical_ft": resultado.distancia_vertical_ft,
                }
            )

    print(f"Resultados Python exportados en: {RUTA_SALIDA}")


if __name__ == "__main__":
    exportar_resultados_python()
