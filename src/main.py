"""Punto de entrada por consola para la demo academica SASTA."""

from pathlib import Path

from calculo_cinematico_modulo import calcular_proyecciones
from ingesta_modulo import cargar_aeronaves_csv
from motor_alertas_modulo import evaluar_alertas

try:
    from colorama import Fore, Style, init
except ImportError:
    class _ColorFallback:
        BLACK = ""
        RED = ""
        GREEN = ""
        YELLOW = ""
        BLUE = ""
        MAGENTA = ""
        CYAN = ""
        WHITE = ""
        RESET_ALL = ""

    Fore = _ColorFallback()
    Style = _ColorFallback()

    def init(autoreset=True):
        return None


BASE_DIR = Path(__file__).resolve().parent.parent
RUTA_CSV = BASE_DIR / "data" / "aeronaves_demo.csv"
RUTA_LOG = BASE_DIR / "logs" / "errores.log"


def main():
    """Ejecuta la demo por consola del sistema SASTA."""
    init(autoreset=True)

    aeronaves, descartados = cargar_aeronaves_csv(RUTA_CSV, RUTA_LOG)
    resultados_calculo = calcular_proyecciones(aeronaves)
    resultados_alerta = evaluar_alertas(resultados_calculo)

    print("SISTEMA SASTA - DEMO DE CONSTRUCCIÓN Y PRUEBAS")
    print("=" * 52)
    print(f"Aeronaves validas:      {len(aeronaves)}")
    print(f"Registros descartados:  {len(descartados)}")
    print(f"Pares evaluados:        {len(resultados_alerta)}")
    print()

    print(f"{'Par':<12} {'Tiempo(min)':>12} {'Dist.H(NM)':>12} {'Dist.V(ft)':>12} {'Alerta':>12}")
    print("-" * 64)

    for resultado in resultados_alerta:
        par = f"{resultado.id_a}-{resultado.id_b}"
        distancia_horizontal = _normalizar_cero(resultado.distancia_horizontal_nm)
        alerta = _colorear_alerta(resultado.alerta, f"{resultado.alerta:>12}")

        print(
            f"{par:<12} "
            f"{resultado.tiempo_min:>12.2f} "
            f"{distancia_horizontal:>12.2f} "
            f"{resultado.distancia_vertical_ft:>12.2f} "
            f"{alerta}"
        )

    print()
    print(f"Archivo CSV usado: {RUTA_CSV}")
    print(f"Log de errores:    {RUTA_LOG}")
    print("Las pruebas unitarias se ejecutan con: pytest")


def _normalizar_cero(valor):
    """Evita mostrar ruido numerico cuando el resultado es casi cero."""
    if abs(valor) < 0.000001:
        return 0.0

    return valor


def _colorear_alerta(alerta, texto):
    """Aplica color de consola segun el nivel de alerta."""
    if alerta == "VERDE":
        return f"{Fore.GREEN}{texto}{Style.RESET_ALL}"
    if alerta == "AMARILLO":
        return f"{Fore.YELLOW}{texto}{Style.RESET_ALL}"
    if alerta == "ROJO":
        return f"{Fore.RED}{texto}{Style.RESET_ALL}"

    return texto


if __name__ == "__main__":
    main()
