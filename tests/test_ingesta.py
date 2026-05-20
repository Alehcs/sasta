"""Pruebas unitarias de ingesta para el sistema SASTA."""

from src.calculo_cinematico_modulo import calcular_proyecciones
from src.ingesta_modulo import cargar_aeronaves_csv


def test_ut_err_01_descarta_altitud_negativa_y_registra_log(tmp_path):
    """UT-ERR-01: descarta un registro con altitud negativa."""
    ruta_csv = tmp_path / "altitud_negativa.csv"
    ruta_log = tmp_path / "errores.log"
    _crear_csv(
        ruta_csv,
        [
            "V15,12.0,15.0,-200,350,120,0",
        ],
    )

    aeronaves, descartados = cargar_aeronaves_csv(ruta_csv, ruta_log)

    assert aeronaves == []
    assert len(descartados) == 1
    assert descartados[0]["datos"]["id"] == "V15"
    assert "altitud invalida" in descartados[0]["motivo"]
    assert "V15" in ruta_log.read_text(encoding="utf-8")
    assert "altitud invalida" in ruta_log.read_text(encoding="utf-8")


def test_ut_err_02_descarta_velocidad_corrupta_y_registra_log(tmp_path):
    """UT-ERR-02: descarta un registro con vel_h corrupta."""
    ruta_csv = tmp_path / "velocidad_corrupta.csv"
    ruta_log = tmp_path / "errores.log"
    _crear_csv(
        ruta_csv,
        [
            "V16,20.0,30.0,12000,CORRUPTO,90,0",
        ],
    )

    aeronaves, descartados = cargar_aeronaves_csv(ruta_csv, ruta_log)

    assert aeronaves == []
    assert len(descartados) == 1
    assert descartados[0]["datos"]["id"] == "V16"
    assert "valor numerico invalido" in descartados[0]["motivo"]
    assert "V16" in ruta_log.read_text(encoding="utf-8")
    assert "valor numerico invalido" in ruta_log.read_text(encoding="utf-8")


def test_ut_rn_01_excluye_altitud_menor_a_100_por_rn05(tmp_path):
    """UT-RN-01: excluye una aeronave con altitud 50 ft por RN-05."""
    ruta_csv = tmp_path / "rn05.csv"
    ruta_log = tmp_path / "errores.log"
    _crear_csv(
        ruta_csv,
        [
            "V17,5.0,5.0,50,100,90,0",
        ],
    )

    aeronaves, descartados = cargar_aeronaves_csv(ruta_csv, ruta_log)
    resultados_calculo = calcular_proyecciones(aeronaves)

    assert aeronaves == []
    assert resultados_calculo == []
    assert len(descartados) == 1
    assert descartados[0]["datos"]["id"] == "V17"
    assert "RN-05" in descartados[0]["motivo"]
    assert "RN-05" in ruta_log.read_text(encoding="utf-8")


def _crear_csv(ruta_csv, filas):
    """Crea un CSV temporal con las columnas esperadas por SASTA."""
    contenido = "id,pos_x,pos_y,alt_z,vel_h,angulo,tasa_v\n"
    contenido += "\n".join(filas)
    contenido += "\n"
    ruta_csv.write_text(contenido, encoding="utf-8")
