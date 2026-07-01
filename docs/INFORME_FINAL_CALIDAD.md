# Informe Final de Calidad - SASTA

## Dictamen final

SASTA queda listo para demo academica. El proyecto cuenta con evidencia de pruebas automatizadas, validacion cruzada, dashboard visual, dataset de estres, CI/CD y controles estaticos basicos.

## Estado por fases

| Fase | Estado | Evidencia |
| --- | --- | --- |
| Fase 1 - Demo por consola y nucleo | Completada | `src/main.py`, modulos `src/`, dataset demo |
| Fase 2 - Dashboard y validacion cruzada | Completada | `app_streamlit.py`, `java/SastaCalculator.java`, validador Python |
| Fase 3 - Automatizacion QA e integracion continua | Completada | `tests/`, dataset de estres, `.github/workflows/qa.yml` |
| Fase 4 - Aseguramiento estatico, cobertura y seguridad | Completada | `pyproject.toml`, `sonar-project.properties`, Ruff, pytest-cov, Bandit |
| Fase 5 - UAT y cierre final | Completada | checklist UAT, code freeze, script final de verificacion |

## Pruebas automatizadas actuales

- Pruebas unitarias de calculo y motor de alertas.
- Pruebas de ingesta para errores numericos, altitud negativa y RN-05.
- Prueba de integracion del flujo completo.
- Prueba de validacion cruzada Java/Python.
- Prueba de estres sobre 200 aeronaves con umbral menor a 5 segundos.

## Dataset demo

`data/aeronaves_demo.csv` mantiene los casos principales de aceptacion:

- 4 aeronaves validas.
- 3 registros descartados.
- 6 pares evaluados.
- `V01-V02` como caso ROJO principal.
- `V05-V06` como caso VERDE principal.

## Dataset de estres

`data/aeronaves_stress_la_serena_200.csv` contiene 200 aeronaves sinteticas validas. Es determinista, academico y no representa trafico aereo real. Su objetivo es validar rendimiento y robustez del flujo completo.

## Validacion cruzada Java/Python

La validacion cruzada compara resultados cinematicos generados por Python y Java con tolerancia `<= 0.01`. La evidencia esperada es que todos los pares comparados queden en estado OK.

## Logs categorizados

La ingesta registra descartes con nivel de criticidad:

- `ERROR`: datos corruptos o altitud negativa.
- `WARNING`: exclusion RN-05.
- `INFO`: eventos informativos si aplica.

## CI/CD

GitHub Actions ejecuta el flujo QA en `push` y `pull_request` hacia `main`:

- Instalacion de dependencias.
- Configuracion de Python 3.12 y Java 17.
- Generacion de dataset de estres.
- Ruff.
- Pytest con cobertura.
- Bandit.
- Demo por consola.
- Exportacion y validacion cruzada Java/Python.
- Compilacion del dashboard Streamlit.
- Compilacion del script final de verificacion.

## Aseguramiento estatico, cobertura y seguridad

- Ruff revisa errores comunes y complejidad basica.
- pytest-cov genera `coverage.xml` para integracion futura con SonarQube.
- Bandit ejecuta seguridad basica sobre `src`, `scripts` y `app_streamlit.py`.
- `sonar-project.properties` deja preparada la lectura de fuentes, tests y cobertura.

## Cierre

El sistema cumple el alcance academico definido: reglas de negocio trazables, pruebas automatizadas, evidencia de rendimiento, validacion cruzada, dashboard de demo y documentacion de aceptacion. Dictamen final: listo para demo academica.
