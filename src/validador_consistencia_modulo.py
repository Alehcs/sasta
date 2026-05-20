"""Valida consistencia numerica entre resultados Python y Java de SASTA."""

import csv
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
RUTA_PYTHON = BASE_DIR / "data" / "resultados_python.csv"
RUTA_JAVA = BASE_DIR / "data" / "resultados_java.csv"
TOLERANCIA = 0.01
CAMPOS_NUMERICOS = (
    "tiempo_min",
    "distancia_horizontal_nm",
    "distancia_vertical_ft",
)


def validar_consistencia(
    ruta_python=RUTA_PYTHON,
    ruta_java=RUTA_JAVA,
    tolerancia=TOLERANCIA,
):
    """Compara resultados Python y Java por par de aeronaves."""
    filas = comparar_resultados(ruta_python, ruta_java, tolerancia)

    print("VALIDACION CRUZADA JAVA/PYTHON - SASTA")
    print("=" * 43)
    print(f"{'Par':<12} {'Diff tiempo':>14} {'Diff H':>12} {'Diff V':>12} {'Estado':>10}")
    print("-" * 64)

    for fila in filas:
        print(_formatear_fila(fila))

    return filas


def comparar_resultados(
    ruta_python=RUTA_PYTHON,
    ruta_java=RUTA_JAVA,
    tolerancia=TOLERANCIA,
):
    """Retorna diferencias numericas entre resultados Python y Java."""
    resultados_python = _leer_resultados(ruta_python)
    resultados_java = _leer_resultados(ruta_java)
    pares = sorted(set(resultados_python) | set(resultados_java))
    filas = []

    for par in pares:
        resultado_python = resultados_python.get(par)
        resultado_java = resultados_java.get(par)

        if resultado_python is None or resultado_java is None:
            fila = {
                "par": par,
                "diferencia_tiempo": None,
                "diferencia_horizontal": None,
                "diferencia_vertical": None,
                "estado": "REVISAR",
            }
        else:
            diferencia_tiempo = abs(resultado_python["tiempo_min"] - resultado_java["tiempo_min"])
            diferencia_horizontal = abs(
                resultado_python["distancia_horizontal_nm"]
                - resultado_java["distancia_horizontal_nm"]
            )
            diferencia_vertical = abs(
                resultado_python["distancia_vertical_ft"]
                - resultado_java["distancia_vertical_ft"]
            )
            estado = "OK"
            if (
                diferencia_tiempo > tolerancia
                or diferencia_horizontal > tolerancia
                or diferencia_vertical > tolerancia
            ):
                estado = "REVISAR"

            fila = {
                "par": par,
                "diferencia_tiempo": diferencia_tiempo,
                "diferencia_horizontal": diferencia_horizontal,
                "diferencia_vertical": diferencia_vertical,
                "estado": estado,
            }

        filas.append(fila)

    return filas


def _leer_resultados(ruta_csv):
    """Lee resultados exportados y los indexa por par id_a-id_b."""
    resultados = {}

    with open(ruta_csv, newline="", encoding="utf-8") as archivo_csv:
        lector = csv.DictReader(archivo_csv)

        for fila in lector:
            par = f"{fila['id_a']}-{fila['id_b']}"
            resultados[par] = {
                campo: float(fila[campo])
                for campo in CAMPOS_NUMERICOS
            }

    return resultados


def _formatear_fila(fila):
    """Prepara una fila de salida para consola."""
    if fila["diferencia_tiempo"] is None:
        return f"{fila['par']:<12} {'N/A':>14} {'N/A':>12} {'N/A':>12} {fila['estado']:>10}"

    return (
        f"{fila['par']:<12} "
        f"{fila['diferencia_tiempo']:>14.4f} "
        f"{fila['diferencia_horizontal']:>12.4f} "
        f"{fila['diferencia_vertical']:>12.4f} "
        f"{fila['estado']:>10}"
    )


def validar_registro_aeronave(registro):
    """Mantiene una validacion simple de existencia de registro."""
    return registro is not None


if __name__ == "__main__":
    validar_consistencia()
