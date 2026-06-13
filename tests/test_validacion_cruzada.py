"""Prueba de integracion de la validacion cruzada Java/Python de SASTA.

Compara los resultados exportados por Python y Java y verifica que todos
los pares queden en estado OK dentro de la tolerancia numerica permitida.
"""

from pathlib import Path

import pytest

from src.validador_consistencia_modulo import comparar_resultados


BASE_DIR = Path(__file__).resolve().parent.parent
RUTA_PYTHON = BASE_DIR / "data" / "resultados_python.csv"
RUTA_JAVA = BASE_DIR / "data" / "resultados_java.csv"
TOLERANCIA = 0.01


def test_validacion_cruzada_todos_los_pares_ok():
    """Todos los pares comparados deben quedar OK con diferencias <= 0.01."""
    if not RUTA_PYTHON.exists() or not RUTA_JAVA.exists():
        pytest.skip(
            "Faltan resultados_python.csv o resultados_java.csv; "
            "ejecutar exportacion Python y Java antes de esta prueba."
        )

    filas = comparar_resultados(RUTA_PYTHON, RUTA_JAVA, TOLERANCIA)

    assert filas, "No se compararon pares; los archivos estan vacios."

    for fila in filas:
        assert fila["estado"] == "OK", f"Par {fila['par']} en estado REVISAR"
        assert fila["diferencia_tiempo"] <= TOLERANCIA
        assert fila["diferencia_horizontal"] <= TOLERANCIA
        assert fila["diferencia_vertical"] <= TOLERANCIA
