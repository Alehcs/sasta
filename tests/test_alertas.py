"""Pruebas unitarias de reglas borde del motor de alertas SASTA."""

from src.calculo_cinematico_modulo import ResultadoCalculo
from src.motor_alertas_modulo import evaluar_alerta


def test_ut_bord_01_distancia_horizontal_exactamente_5_nm_es_verde():
    """UT-BORD-01: distancia horizontal 5.00 debe generar alerta VERDE."""
    resultado_calculo = ResultadoCalculo(
        id_a="B01",
        id_b="B02",
        tiempo_min=1.0,
        distancia_horizontal_nm=5.00,
        distancia_vertical_ft=500.0,
    )

    resultado_alerta = evaluar_alerta(resultado_calculo)

    assert resultado_alerta.alerta == "VERDE"


def test_ut_bord_02_tiempo_exactamente_2_min_es_amarillo():
    """UT-BORD-02: tiempo 2.00 con conflicto debe generar alerta AMARILLO."""
    resultado_calculo = ResultadoCalculo(
        id_a="B03",
        id_b="B04",
        tiempo_min=2.00,
        distancia_horizontal_nm=4.99,
        distancia_vertical_ft=500.0,
    )

    resultado_alerta = evaluar_alerta(resultado_calculo)

    assert resultado_alerta.alerta == "AMARILLO"
