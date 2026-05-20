"""Modulo de motor de alertas para la demo SASTA.

Aplica reglas de negocio sobre resultados cinematicos ya calculados.
"""

from dataclasses import dataclass


@dataclass
class ResultadoAlerta:
    """Resultado de alerta para un par de aeronaves."""

    id_a: str
    id_b: str
    tiempo_min: float
    distancia_horizontal_nm: float
    distancia_vertical_ft: float
    alerta: str


def evaluar_alerta(resultado_calculo):
    """Evalua una alerta segun tiempo y separacion proyectada."""
    if resultado_calculo.tiempo_min < 0:
        alerta = "VERDE"
    else:
        hay_conflicto = (
            resultado_calculo.distancia_horizontal_nm < 5.00
            and resultado_calculo.distancia_vertical_ft < 1000
        )

        if not hay_conflicto:
            alerta = "VERDE"
        elif resultado_calculo.tiempo_min < 2.00:
            alerta = "ROJO"
        elif resultado_calculo.tiempo_min <= 5.00:
            alerta = "AMARILLO"
        else:
            alerta = "VERDE"

    return ResultadoAlerta(
        id_a=resultado_calculo.id_a,
        id_b=resultado_calculo.id_b,
        tiempo_min=resultado_calculo.tiempo_min,
        distancia_horizontal_nm=resultado_calculo.distancia_horizontal_nm,
        distancia_vertical_ft=resultado_calculo.distancia_vertical_ft,
        alerta=alerta,
    )


def evaluar_alertas(resultados_calculo):
    """Evalua alertas para una lista de resultados cinematicos."""
    return [evaluar_alerta(resultado) for resultado in resultados_calculo]


def generar_alerta(distancia_km, umbral_km=10):
    """Mantiene compatibilidad con pruebas iniciales de la demo."""
    return distancia_km < umbral_km
