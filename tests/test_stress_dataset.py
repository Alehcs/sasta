"""Prueba de rendimiento y robustez sobre el dataset de estres de SASTA.

Valida que el flujo completo (ingesta -> calculo -> alertas) procese un dataset
sintetico de 200 aeronaves sin errores y dentro de un umbral de tiempo holgado,
apto para entorno local y CI. No valida exactitud aeronautica real.
"""

import sys
import time
from pathlib import Path

from src.calculo_cinematico_modulo import calcular_proyecciones
from src.ingesta_modulo import cargar_aeronaves_csv
from src.motor_alertas_modulo import evaluar_alertas


BASE_DIR = Path(__file__).resolve().parent.parent
RUTA_CSV = BASE_DIR / "data" / "aeronaves_stress_la_serena_200.csv"
UMBRAL_SEGUNDOS = 5.0

sys.path.insert(0, str(BASE_DIR / "scripts"))
from generar_dataset_estres import generar_dataset_estres  # noqa: E402


def test_flujo_estres_200_aeronaves(tmp_path):
    """Procesa 200 aeronaves validas y termina en menos de 5 segundos."""
    if not RUTA_CSV.exists():
        generar_dataset_estres(RUTA_CSV)

    ruta_log = tmp_path / "errores.log"

    inicio = time.perf_counter()

    aeronaves, descartados = cargar_aeronaves_csv(RUTA_CSV, ruta_log)
    resultados_calculo = calcular_proyecciones(aeronaves)
    resultados_alerta = evaluar_alertas(resultados_calculo)

    transcurrido = time.perf_counter() - inicio

    # El dataset de estres es valido por diseno: 200 aeronaves, 0 descartes.
    assert len(aeronaves) == 200
    assert len(descartados) == 0

    # Con 200 aeronaves deben generarse pares (200 * 199 / 2 = 19900).
    assert len(resultados_calculo) > 0
    assert len(resultados_alerta) == len(resultados_calculo)

    # Cada alerta debe pertenecer al conjunto valido (robustez, no exactitud).
    assert all(r.alerta in {"VERDE", "AMARILLO", "ROJO"} for r in resultados_alerta)

    # Umbral holgado para no ser fragil en local/CI.
    assert transcurrido < UMBRAL_SEGUNDOS, f"Flujo demoro {transcurrido:.2f}s"
