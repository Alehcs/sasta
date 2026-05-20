"""Pruebas unitarias de escenarios cinematicos normales para SASTA."""

from src.calculo_cinematico_modulo import calcular_proyecciones
from src.ingesta_modulo import Aeronave
from src.motor_alertas_modulo import evaluar_alertas


def test_ut_norm_01_aeronaves_convergentes_generan_alerta_rojo():
    """UT-NORM-01: V01 y V02 convergentes deben generar alerta ROJO."""
    aeronaves = [
        Aeronave("V01", 0.0, 0.0, 30000, 400, 90, 0),
        Aeronave("V02", 10.0, 0.0, 30000, 400, 270, 0),
    ]

    resultados_calculo = calcular_proyecciones(aeronaves)
    resultados_alerta = evaluar_alertas(resultados_calculo)

    assert len(resultados_calculo) == 1
    assert resultados_alerta[0].id_a == "V01"
    assert resultados_alerta[0].id_b == "V02"
    assert resultados_alerta[0].alerta == "ROJO"


def test_ut_norm_02_aeronaves_paralelas_separadas_6_nm_generan_alerta_verde():
    """UT-NORM-02: V05 y V06 paralelas a 6 NM deben generar alerta VERDE."""
    aeronaves = [
        Aeronave("V05", 100.0, 100.0, 35000, 400, 45, 0),
        Aeronave("V06", 100.0, 106.0, 35000, 400, 45, 0),
    ]

    resultados_calculo = calcular_proyecciones(aeronaves)
    resultados_alerta = evaluar_alertas(resultados_calculo)

    assert len(resultados_calculo) == 1
    assert resultados_calculo[0].distancia_horizontal_nm == 6.0
    assert resultados_alerta[0].id_a == "V05"
    assert resultados_alerta[0].id_b == "V06"
    assert resultados_alerta[0].alerta == "VERDE"
