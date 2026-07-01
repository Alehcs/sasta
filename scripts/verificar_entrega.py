"""Verificacion final de entrega para SASTA.

Ejecuta el flujo QA principal y valida que existan los artefactos criticos de
cierre. No modifica reglas de negocio ni genera commits.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import shutil
# Ejecuta comandos QA cerrados definidos por el proyecto.
import subprocess  # nosec B404
import sys


BASE_DIR = Path(__file__).resolve().parent.parent
ARCHIVOS_CRITICOS = (
    "README.md",
    "app_streamlit.py",
    "pyproject.toml",
    "sonar-project.properties",
    ".github/workflows/qa.yml",
    "data/aeronaves_demo.csv",
    "data/aeronaves_stress_la_serena_200.csv",
    "src/main.py",
    "src/exportar_resultados_python.py",
    "src/validador_consistencia_modulo.py",
    "java/SastaCalculator.java",
    "docs/UAT_CHECKLIST.md",
    "docs/CODE_FREEZE.md",
    "docs/INFORME_FINAL_CALIDAD.md",
)


def main() -> int:
    """Ejecuta la verificacion final de entrega."""
    faltantes = _validar_archivos_criticos()
    if faltantes:
        print("Archivos criticos faltantes:")
        for ruta in faltantes:
            print(f"- {ruta}")
        return 1

    comandos = _crear_comandos()
    resultados = [_ejecutar(nombre, comando) for nombre, comando in comandos]

    fallidos = [nombre for nombre, codigo in resultados if codigo != 0]
    if fallidos:
        print("\nVerificacion final con fallos:")
        for nombre in fallidos:
            print(f"- {nombre}")
        return 1

    print("\nVerificacion final completada correctamente.")
    return 0


def _validar_archivos_criticos() -> list[str]:
    """Retorna rutas criticas que no existen."""
    return [
        ruta
        for ruta in ARCHIVOS_CRITICOS
        if not (BASE_DIR / ruta).exists()
    ]


def _crear_comandos() -> list[tuple[str, list[str]]]:
    """Construye el flujo de comandos final segun herramientas disponibles."""
    comandos = []

    if _modulo_disponible("ruff"):
        comandos.append(("Ruff", [sys.executable, "-m", "ruff", "check", "."]))
    else:
        print("Ruff no disponible; instalar requirements.txt para habilitar linting.")

    if _modulo_disponible("pytest_cov"):
        comandos.append(
            (
                "Pytest con cobertura",
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "--cov=src",
                    "--cov=scripts",
                    "--cov-report=term-missing",
                    "--cov-report=xml",
                ],
            )
        )
    else:
        print("pytest-cov no disponible; instalar requirements.txt para habilitar cobertura.")

    if _modulo_disponible("bandit"):
        comandos.append(
            (
                "Bandit",
                [sys.executable, "-m", "bandit", "-r", "src", "scripts", "app_streamlit.py"],
            )
        )

    javac = _resolver_herramienta_java("javac")
    java = _resolver_herramienta_java("java")

    comandos.extend(
        [
            ("Demo consola", [sys.executable, "src/main.py"]),
            ("Exportar resultados Python", [sys.executable, "src/exportar_resultados_python.py"]),
            ("Compilar Java", [javac, "java/SastaCalculator.java"]),
            ("Ejecutar Java", [java, "-cp", "java", "SastaCalculator"]),
            ("Validacion cruzada", [sys.executable, "src/validador_consistencia_modulo.py"]),
            ("Compilar Streamlit", [sys.executable, "-m", "py_compile", "app_streamlit.py"]),
        ]
    )

    return comandos


def _modulo_disponible(nombre: str) -> bool:
    """Indica si un modulo Python esta instalado."""
    return importlib.util.find_spec(nombre) is not None


def _resolver_herramienta_java(nombre: str) -> str:
    """Busca javac/java priorizando JAVA_HOME para evitar runtimes antiguos en PATH."""
    ejecutable = f"{nombre}.exe" if os.name == "nt" else nombre
    java_home = os.environ.get("JAVA_HOME")
    candidatos = []

    if java_home:
        candidatos.append(Path(java_home) / "bin" / ejecutable)

    herramienta_path = shutil.which(nombre)
    if herramienta_path:
        candidatos.append(Path(herramienta_path))

    for candidato in candidatos:
        if candidato.exists():
            return str(candidato)

    return nombre


def _ejecutar(nombre: str, comando: list[str]) -> tuple[str, int]:
    """Ejecuta un comando y retorna su codigo de salida."""
    print(f"\n== {nombre} ==")
    print(" ".join(comando))
    proceso = subprocess.run(comando, cwd=BASE_DIR, check=False)  # nosec B603
    return nombre, proceso.returncode


if __name__ == "__main__":
    raise SystemExit(main())
