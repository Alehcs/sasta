"""Modulo de calculo cinematico para la demo SASTA.

Calcula proyecciones simples de maxima aproximacion entre pares de aeronaves.
"""

from dataclasses import dataclass
from itertools import combinations
import math


@dataclass
class ResultadoCalculo:
    """Resultado de proyeccion entre dos aeronaves."""

    id_a: str
    id_b: str
    tiempo_min: float
    distancia_horizontal_nm: float
    distancia_vertical_ft: float


def descomponer_velocidad(aeronave):
    """Descompone la velocidad horizontal en componentes X e Y en NM/min."""
    vel_h_nm_min = aeronave.vel_h / 60
    angulo_rad = math.radians(aeronave.angulo)
    vx = vel_h_nm_min * math.sin(angulo_rad)
    vy = vel_h_nm_min * math.cos(angulo_rad)

    return vx, vy


def calcular_proyecciones(aeronaves):
    """Evalua todos los pares de aeronaves y calcula su maxima aproximacion."""
    resultados = []

    for aeronave_a, aeronave_b in combinations(aeronaves, 2):
        vx1, vy1 = descomponer_velocidad(aeronave_a)
        vx2, vy2 = descomponer_velocidad(aeronave_b)

        dx = aeronave_b.pos_x - aeronave_a.pos_x
        dy = aeronave_b.pos_y - aeronave_a.pos_y
        dvx = vx2 - vx1
        dvy = vy2 - vy1

        velocidad_relativa_cuadrada = (dvx**2) + (dvy**2)
        if velocidad_relativa_cuadrada == 0:
            tiempo_critico = 0
        else:
            tiempo_critico = -((dx * dvx) + (dy * dvy)) / velocidad_relativa_cuadrada

        x1_futuro = aeronave_a.pos_x + vx1 * tiempo_critico
        y1_futuro = aeronave_a.pos_y + vy1 * tiempo_critico
        x2_futuro = aeronave_b.pos_x + vx2 * tiempo_critico
        y2_futuro = aeronave_b.pos_y + vy2 * tiempo_critico

        distancia_horizontal_nm = math.sqrt(
            ((x2_futuro - x1_futuro) ** 2) + ((y2_futuro - y1_futuro) ** 2)
        )

        alt1_futura = aeronave_a.alt_z + aeronave_a.tasa_v * tiempo_critico
        alt2_futura = aeronave_b.alt_z + aeronave_b.tasa_v * tiempo_critico
        distancia_vertical_ft = abs(alt2_futura - alt1_futura)

        resultados.append(
            ResultadoCalculo(
                id_a=aeronave_a.id,
                id_b=aeronave_b.id,
                tiempo_min=tiempo_critico,
                distancia_horizontal_nm=distancia_horizontal_nm,
                distancia_vertical_ft=distancia_vertical_ft,
            )
        )

    return resultados


def calcular_distancia_aproximada(aeronave_a, aeronave_b):
    """Mantiene compatibilidad con pruebas iniciales de la demo."""
    return 0.0
