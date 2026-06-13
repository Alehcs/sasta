"""Generador de dataset de estres sintetico para SASTA.

DATASET SINTETICO Y ACADEMICO: las aeronaves, posiciones y trayectorias son
generadas artificialmente con fines de prueba de rendimiento y robustez.
NO representan trafico aereo real. El espacio aereo esta inspirado de forma
aproximada en la zona regional de La Serena / La Florida (Chile), usando un
sistema local simplificado en millas nauticas (NM), no latitud/longitud real.

Columnas generadas: id,pos_x,pos_y,alt_z,vel_h,angulo,tasa_v
- pos_x: posicion este/oeste en NM (rango aproximado -80 a 80).
- pos_y: posicion norte/sur en NM (rango aproximado -80 a 80).
- alt_z: altitud en pies (>= 100).
- vel_h: velocidad horizontal en nudos.
- angulo: rumbo en grados (0 a 360).
- tasa_v: tasa vertical en pies por minuto.

El dataset es determinista (semilla fija) y solo contiene registros validos.
"""

import csv
import random
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
RUTA_SALIDA = BASE_DIR / "data" / "aeronaves_stress_la_serena_200.csv"
CAMPOS = ("id", "pos_x", "pos_y", "alt_z", "vel_h", "angulo", "tasa_v")
SEMILLA = 20260520

# Centros de agrupamiento aproximados (en NM) para crear escenarios interesantes:
# aeropuerto, ruta de aproximacion, ruta de salida y un punto de sobrevuelo.
CENTROS_CLUSTER = [
    (0.0, 0.0),
    (-18.0, 12.0),
    (22.0, -8.0),
    (-40.0, -35.0),
    (35.0, 45.0),
]


def _perfil_bajo(rng):
    """Aproximacion/salida baja o aviacion general cercana al aeropuerto."""
    alt = rng.randint(100, 3000)
    vel = rng.randint(90, 160)
    tasa = rng.choice([rng.randint(-1500, -200), rng.randint(200, 1500), 0])
    return alt, vel, tasa


def _perfil_regional(rng):
    """Ascenso/descenso regional comercial."""
    alt = rng.randint(3000, 12000)
    vel = rng.randint(180, 280)
    tasa = rng.choice([rng.randint(-2200, -400), rng.randint(400, 2200)])
    return alt, vel, tasa


def _perfil_ruta(rng):
    """Trafico en ruta o sobrevuelo de gran altitud (crucero)."""
    alt = rng.randint(12000, 35000)
    vel = rng.randint(350, 480)
    tasa = rng.choice([0, rng.randint(-200, 200)])
    return alt, vel, tasa


def _posicion(rng):
    """Genera una posicion; parte del trafico se agrupa cerca de un centro."""
    if rng.random() < 0.45:
        cx, cy = rng.choice(CENTROS_CLUSTER)
        pos_x = cx + rng.uniform(-6.0, 6.0)
        pos_y = cy + rng.uniform(-6.0, 6.0)
    else:
        pos_x = rng.uniform(-80.0, 80.0)
        pos_y = rng.uniform(-80.0, 80.0)

    pos_x = max(-80.0, min(80.0, pos_x))
    pos_y = max(-80.0, min(80.0, pos_y))
    return round(pos_x, 2), round(pos_y, 2)


def generar_dataset_estres(ruta_salida=RUTA_SALIDA, cantidad=200, semilla=SEMILLA):
    """Genera un CSV determinista con aeronaves validas de estres."""
    rng = random.Random(semilla)
    perfiles = (_perfil_bajo, _perfil_regional, _perfil_ruta)
    pesos = (0.30, 0.40, 0.30)

    ruta_salida = Path(ruta_salida)
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)

    with ruta_salida.open("w", newline="", encoding="utf-8") as archivo_csv:
        escritor = csv.writer(archivo_csv)
        escritor.writerow(CAMPOS)

        for indice in range(1, cantidad + 1):
            perfil = rng.choices(perfiles, weights=pesos, k=1)[0]
            alt_z, vel_h, tasa_v = perfil(rng)
            pos_x, pos_y = _posicion(rng)
            angulo = rng.randint(0, 360)

            escritor.writerow(
                [
                    f"LSC{indice:03d}",
                    pos_x,
                    pos_y,
                    alt_z,
                    vel_h,
                    angulo,
                    tasa_v,
                ]
            )

    return ruta_salida


if __name__ == "__main__":
    ruta = generar_dataset_estres()
    print(f"Dataset de estres (sintetico/academico) generado en: {ruta}")
