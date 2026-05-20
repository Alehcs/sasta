"""Modulo de ingesta de datos para la demo SASTA.

Lee aeronaves desde CSV, valida registros basicos y registra descartes.
"""

from dataclasses import dataclass
import csv
from datetime import datetime
from pathlib import Path


CAMPOS_OBLIGATORIOS = ("id", "pos_x", "pos_y", "alt_z", "vel_h", "angulo", "tasa_v")


@dataclass
class Aeronave:
    """Representa una aeronave validada para continuar al calculo."""

    id: str
    pos_x: float
    pos_y: float
    alt_z: int
    vel_h: float
    angulo: float
    tasa_v: float


def registrar_error(ruta_log, mensaje):
    """Registra un mensaje de error o descarte con timestamp."""
    ruta = Path(ruta_log)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().isoformat(timespec="seconds")

    with ruta.open("a", encoding="utf-8") as archivo_log:
        archivo_log.write(f"[{timestamp}] {mensaje}\n")


def cargar_aeronaves_csv(ruta_csv, ruta_log="logs/errores.log"):
    """Carga aeronaves validas desde un CSV y retorna tambien los descartes."""
    aeronaves_validas = []
    registros_descartados = []

    with open(ruta_csv, newline="", encoding="utf-8") as archivo_csv:
        lector = csv.DictReader(archivo_csv)

        for numero_fila, fila in enumerate(lector, start=2):
            motivo = _validar_campos_obligatorios(fila)
            if motivo:
                _descartar(registros_descartados, ruta_log, numero_fila, fila, motivo)
                continue

            try:
                aeronave = Aeronave(
                    id=fila["id"].strip(),
                    pos_x=float(fila["pos_x"]),
                    pos_y=float(fila["pos_y"]),
                    alt_z=int(fila["alt_z"]),
                    vel_h=float(fila["vel_h"]),
                    angulo=float(fila["angulo"]),
                    tasa_v=float(fila["tasa_v"]),
                )
            except ValueError as error:
                motivo = f"valor numerico invalido: {error}"
                _descartar(registros_descartados, ruta_log, numero_fila, fila, motivo)
                continue

            if aeronave.alt_z < 0:
                motivo = "altitud invalida: alt_z no puede ser negativa"
                _descartar(registros_descartados, ruta_log, numero_fila, fila, motivo)
                continue

            if aeronave.alt_z < 100:
                motivo = "RN-05: aeronave excluida por altitud menor a 100 ft"
                _descartar(registros_descartados, ruta_log, numero_fila, fila, motivo)
                continue

            aeronaves_validas.append(aeronave)

    return aeronaves_validas, registros_descartados


def cargar_aeronaves(ruta_archivo):
    """Mantiene compatibilidad con pruebas iniciales de la demo."""
    aeronaves, _descartados = cargar_aeronaves_csv(ruta_archivo)
    return aeronaves


def _validar_campos_obligatorios(fila):
    """Valida que los campos requeridos existan y no esten vacios."""
    for campo in CAMPOS_OBLIGATORIOS:
        if campo not in fila or fila[campo] is None or fila[campo].strip() == "":
            return f"campo obligatorio faltante o vacio: {campo}"

    return None


def _descartar(registros_descartados, ruta_log, numero_fila, fila, motivo):
    """Guarda un registro descartado y registra su motivo en el log."""
    registro = {"fila": numero_fila, "motivo": motivo, "datos": dict(fila)}
    registros_descartados.append(registro)
    identificador = fila.get("id", "SIN_ID") if fila else "SIN_ID"
    registrar_error(ruta_log, f"Fila {numero_fila} ({identificador}) descartada: {motivo}")
