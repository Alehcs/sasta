"""Prueba de integracion del flujo completo de SASTA.

Cubre: ingesta -> validacion -> calculo cinematico -> motor de alertas,
usando el dataset real data/aeronaves_demo.csv.
"""

from pathlib import Path

from src.calculo_cinematico_modulo import calcular_proyecciones
from src.ingesta_modulo import cargar_aeronaves_csv
from src.motor_alertas_modulo import evaluar_alertas


BASE_DIR = Path(__file__).resolve().parent.parent
RUTA_CSV = BASE_DIR / "data" / "aeronaves_demo.csv"


def _buscar_alerta(resultados_alerta, id_a, id_b):
    """Devuelve la alerta de un par, sin importar el orden de los ids."""
    for resultado in resultados_alerta:
        par = {resultado.id_a, resultado.id_b}
        if par == {id_a, id_b}:
            return resultado.alerta

    return None


def test_flujo_completo_demo(tmp_path):
    """Valida el flujo extremo a extremo con el dataset de demostracion."""
    ruta_log = tmp_path / "errores.log"

    aeronaves, descartados = cargar_aeronaves_csv(RUTA_CSV, ruta_log)

    assert len(aeronaves) == 4
    assert len(descartados) == 3

    resultados_calculo = calcular_proyecciones(aeronaves)
    resultados_alerta = evaluar_alertas(resultados_calculo)

    assert len(resultados_alerta) == 6

    assert _buscar_alerta(resultados_alerta, "V01", "V02") == "ROJO"
    assert _buscar_alerta(resultados_alerta, "V05", "V06") == "VERDE"
