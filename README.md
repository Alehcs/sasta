# Sistema de Alerta de Separacion y Trafico Aereo (SASTA)

Implementacion inicial del nucleo critico de SASTA para demostrar construccion, pruebas unitarias y trazabilidad en la asignatura Gestion de Calidad de Software.

## Objetivo de la demo

Evidenciar lectura de datos, validacion, calculo cinematico, motor de alertas, manejo de errores, logs y pruebas unitarias.

## Estructura del proyecto

- `data/`: contiene el CSV de prueba con aeronaves de demostracion.
- `logs/`: almacena registros de errores y descartes generados durante la ingesta.
- `src/`: contiene los modulos principales del sistema.
- `java/`: contiene el calculador Java para validacion cruzada.
- `tests/`: contiene las pruebas unitarias automatizadas.
- `requirements.txt`: lista las dependencias necesarias para ejecutar la demo y sus pruebas.

## Modulos principales

- `ingesta_modulo.py`: lectura CSV, validacion y descarte de registros invalidos.
- `calculo_cinematico_modulo.py`: calculo de proyeccion entre pares de aeronaves.
- `motor_alertas_modulo.py`: clasificacion VERDE, AMARILLO y ROJO.
- `exportar_resultados_python.py`: exporta resultados cinematicos calculados en Python.
- `validador_consistencia_modulo.py`: compara resultados cinematicos Java/Python con tolerancia numerica.
- `main.py`: ejecucion de demo por consola.

## Variables de entrada del CSV

- `id`: identificador de la aeronave.
- `pos_x`: posicion horizontal X en NM.
- `pos_y`: posicion horizontal Y en NM.
- `alt_z`: altitud en pies.
- `vel_h`: velocidad horizontal en nudos.
- `angulo`: rumbo en grados.
- `tasa_v`: tasa vertical en pies por minuto.

## Reglas de negocio y criterios

- RN-05: excluir aeronaves con altitud menor a 100 ft.
- Existe conflicto si la distancia horizontal es menor a 5.00 NM y la distancia vertical es menor a 1000 ft.
- ROJO si el conflicto ocurre en menos de 2 minutos.
- AMARILLO si el conflicto ocurre entre 2 y 5 minutos.
- VERDE si no hay conflicto o si las trayectorias son divergentes.
- Distancia horizontal exactamente 5.00 NM debe ser VERDE, porque el conflicto exige distancia horizontal menor a 5.00 NM.
- Tiempo critico exactamente 2.00 minutos debe ser AMARILLO, porque ROJO aplica solo si `tiempo_min < 2.00`.

## Instalacion

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Si PowerShell bloquea la activacion por politica de ejecucion, usar:

```cmd
.venv\Scripts\activate.bat
```

## Ejecucion de la demo

```powershell
python src/main.py
```

## Interfaz visual Streamlit

```powershell
streamlit run app_streamlit.py
```

## Ejecucion de pruebas

```powershell
python -m pytest -v
```

## Validación cruzada Java/Python

La validacion cruzada es una evidencia adicional de calidad y no reemplaza la demo principal por consola. El calculo cinematico critico se ejecuta en Python y tambien en Java. Python exporta sus resultados a `data/resultados_python.csv`, Java exporta sus resultados a `data/resultados_java.csv`, y el validador compara ambos archivos usando tolerancia `<= 0.01`.

Si las diferencias de tiempo, distancia horizontal y distancia vertical estan dentro de tolerancia, el par queda en estado OK. Si alguna diferencia supera la tolerancia, queda en estado REVISAR.

### Requisito de Java

La validacion cruzada Java/Python requiere **Java 17 o superior**. Antes de ejecutarla, verificar la version con:

```powershell
java -version
```

Si el comando `java` por defecto apunta a otra version (por ejemplo Java 8) o falla, configurar `JAVA_HOME` hacia un JDK 17 y anteponer `%JAVA_HOME%\bin` al `PATH`.

```powershell
python src/exportar_resultados_python.py
javac java/SastaCalculator.java
java -cp java SastaCalculator
python src/validador_consistencia_modulo.py
```

Evidencia actual:

- 6 pares comparados.
- 6 pares en estado OK.
- Diferencias observadas: 0.0000 en tiempo, distancia horizontal y distancia vertical para todos los pares.

## Fase 3 - Automatización QA e Integración Continua

Se agrego un flujo de Integración Continua (CI) mediante **GitHub Actions** definido en `.github/workflows/qa.yml`. Las pruebas y validaciones del proyecto se ejecutan **automáticamente** en cada `push` a `main` y en cada `pull_request` hacia `main`, sin intervención manual.

El workflow se ejecuta en `ubuntu-latest`, configura Python 3.12 y Java 17, instala las dependencias desde `requirements.txt` y valida de forma automatizada:

- `pytest`: pruebas unitarias y de integración.
- Flujo principal por consola (`python src/main.py`).
- Cálculo cinemático en Python y en Java, con compilación de `java/SastaCalculator.java`.
- Validación cruzada Java/Python con tolerancia `<= 0.01`.
- Compilación del dashboard (`python -m py_compile app_streamlit.py`).

Además se incorporaron **pruebas de integración** que ejercitan el sistema de extremo a extremo:

- `tests/test_integracion_flujo.py`: valida el flujo completo (ingesta, validación, cálculo y alertas) sobre `data/aeronaves_demo.csv`, confirmando 4 aeronaves válidas, 3 registros descartados, 6 pares evaluados, V01-V02 en ROJO y V05-V06 en VERDE.
- `tests/test_validacion_cruzada.py`: compara `data/resultados_python.csv` y `data/resultados_java.csv` y verifica que todos los pares queden en estado OK con diferencias `<= 0.01`.

### Pruebas de sistema y robustez

- **Dataset de estrés sintético inspirado en La Serena.** El script `scripts/generar_dataset_estres.py` genera de forma determinista (semilla fija) el archivo `data/aeronaves_stress_la_serena_200.csv` con **200 aeronaves válidas** en un espacio aéreo regional simplificado (coordenadas locales en NM, rango aproximado -80 a 80), con mezcla realista de altitudes, velocidades, rumbos y tasas verticales. **Es un dataset sintético y académico: no representa tráfico aéreo real ni usa latitud/longitud real.**
- **Prueba de rendimiento básica.** `tests/test_stress_dataset.py` procesa el flujo completo (ingesta, cálculo y alertas) sobre las 200 aeronaves, verifica que no haya errores, que se generen pares y que el flujo termine en **menos de 5 segundos** (umbral holgado para entorno local/CI).
- **Dataset de robustez con errores.** `data/aeronaves_robustez_la_serena.csv` separa el caso válido del caso con errores: incluye registros válidos, una altitud negativa, una `vel_h` corrupta y una aeronave bajo 100 ft (RN-05).
- **Logs categorizados por criticidad.** `registrar_error()` ahora etiqueta cada evento con su nivel: `ERROR` (datos corruptos o altitud negativa), `WARNING` (exclusión por RN-05) e `INFO` (eventos informativos). Formato: `[timestamp] [NIVEL] mensaje`.

**GitHub Actions** ejecuta estas pruebas automatizadas en cada `push`/`pull_request` a `main` (incluida la generación del dataset de estrés antes de `pytest`). Esto responde al enfoque de **pruebas automatizadas y CI/CD** visto en clase: cada cambio queda verificado de forma reproducible antes de integrarse, reduciendo el riesgo de regresiones.

## Fase 4 - Aseguramiento Estático, Cobertura y Seguridad

La Fase 4 agrega controles de calidad estaticos y de seguridad basica sin cambiar las reglas de negocio del sistema SASTA.

- **Linting con Ruff:** `python -m ruff check .` revisa `src/`, `tests/`, `scripts/` y `app_streamlit.py` con reglas base orientadas a errores comunes de Python, sin imponer reglas de estilo excesivamente estrictas.
- **Cobertura con pytest-cov:** `python -m pytest --cov=src --cov=scripts --cov-report=term-missing --cov-report=xml` ejecuta las pruebas y muestra lineas no cubiertas.
- **Reporte para SonarQube:** el reporte `coverage.xml` queda configurado para futuras integraciones mediante `sonar-project.properties`, sin requerir SonarQube instalado localmente.
- **Seguridad basica con Bandit:** `python -m bandit -r src scripts app_streamlit.py` revisa patrones Python riesgosos de forma automatizada.
- **Rendimiento:** `tests/test_stress_dataset.py` confirma que el dataset sintetico de 200 aeronaves se procesa en menos de 5 segundos.
- **Bandit B311 documentado:** `scripts/generar_dataset_estres.py` usa `random.Random` con semilla fija solo para generar datos sinteticos reproducibles de prueba. No se usa para criptografia ni seguridad, por lo que se marca como falso positivo razonable con `# nosec B311`.

Comandos principales de Fase 4:

```powershell
python -m ruff check .
python -m pytest --cov=src --cov=scripts --cov-report=term-missing --cov-report=xml
python -m bandit -r src scripts app_streamlit.py
```

## Fase 5 - Validación de Usuario y Cierre Final

La Fase 5 estabiliza el proyecto para entrega final y concentra la evidencia de aceptacion de usuario, cierre de alcance y verificacion final.

- **Filtros del dashboard:** `app_streamlit.py` permite filtrar visualmente las alertas por `TODAS`, `ROJO`, `AMARILLO` y `VERDE`, manteniendo la tabla y la visualizacion 2D tipo radar sobre los resultados ya calculados.
- **Modo demo:** el dashboard incluye una seccion compacta con dataset usado, aeronaves validas, registros descartados, pares evaluados, caso ROJO principal (`V01-V02`) y caso VERDE principal (`V05-V06`).
- **Checklist UAT:** `docs/UAT_CHECKLIST.md` guia la aceptacion manual del revisor: consola, dashboard, casos ROJO/VERDE, descartes, validacion cruzada, pruebas automatizadas y GitHub Actions.
- **Code freeze:** `docs/CODE_FREEZE.md` define fecha de congelamiento, alcance congelado, comandos finales, reglas de no modificacion y excepciones permitidas.
- **Informe final de calidad:** `docs/INFORME_FINAL_CALIDAD.md` resume el estado por fases, pruebas, datasets, validacion cruzada, logs, CI/CD, linting, cobertura y seguridad.
- **Script de verificacion final:** `scripts/verificar_entrega.py` ejecuta el flujo final de QA y prioriza `JAVA_HOME` para evitar runtimes Java antiguos en PATH.
- **Bandit en el script de entrega:** el uso de `subprocess` queda marcado con `# nosec` porque ejecuta comandos cerrados de QA definidos por el proyecto, no entrada libre de usuario.

Flujo de entrega recomendado:

```powershell
python scripts/verificar_entrega.py
streamlit run app_streamlit.py
```

## Flujo recomendado de verificación QA

Secuencia completa para verificar el proyecto de punta a punta en un entorno local (la misma lógica que ejecuta GitHub Actions). Requiere Python 3.12+ y Java 17 (ver "Requisito de Java"):

```powershell
pip install -r requirements.txt
python scripts/generar_dataset_estres.py
python -m ruff check .
python -m pytest -v --cov=src --cov=scripts --cov-report=term-missing --cov-report=xml
python -m bandit -r src scripts app_streamlit.py
python src/main.py
python src/exportar_resultados_python.py
javac java/SastaCalculator.java
java -cp java SastaCalculator
python src/validador_consistencia_modulo.py
python -m py_compile app_streamlit.py
python -m py_compile scripts/verificar_entrega.py
python scripts/verificar_entrega.py
streamlit run app_streamlit.py
```

Resultado esperado:

- Dataset de estrés `data/aeronaves_stress_la_serena_200.csv` generado (200 aeronaves válidas).
- `ruff`: analisis estatico sin hallazgos.
- `pytest` con cobertura: 10 pruebas aprobadas (unitarias, integración y estrés) y `coverage.xml` generado.
- `bandit`: analisis basico de seguridad sin hallazgos relevantes; B311 queda documentado como falso positivo razonable para el generador sintetico.
- Demo por consola: 4 aeronaves válidas, 3 registros descartados, 6 pares evaluados, V01-V02 en ROJO y V05-V06 en VERDE.
- Validación cruzada Java/Python: todos los pares en estado OK con diferencias `<= 0.01`.
- `py_compile` del dashboard sin errores y Streamlit levantando correctamente.
- `scripts/verificar_entrega.py`: flujo final de verificacion ejecutado correctamente.

## Casos de prueba implementados

- UT-NORM-01: convergencia frontal inminente => ROJO.
- UT-NORM-02: vuelo paralelo seguro => VERDE.
- UT-BORD-01: distancia horizontal exactamente 5.00 NM => VERDE, porque el conflicto exige distancia horizontal menor a 5.00 NM.
- UT-BORD-02: tiempo critico exactamente 2.00 min => AMARILLO, porque ROJO aplica solo si `tiempo_min < 2.00`.
- UT-ERR-01: altitud negativa => registro descartado.
- UT-ERR-02: velocidad corrupta => registro descartado.
- UT-RN-01: altitud menor a 100 ft => exclusion por RN-05.

## Matriz resumida de trazabilidad

| Requisito | Modulo | Funcion | Caso de prueba | Resultado esperado |
| --- | --- | --- | --- | --- |
| Leer y validar aeronaves desde CSV | `ingesta_modulo.py` | `cargar_aeronaves_csv()` | UT-ERR-01 | Registro con altitud negativa descartado |
| Detectar datos numericos corruptos | `ingesta_modulo.py` | `cargar_aeronaves_csv()` | UT-ERR-02 | Registro con `vel_h` corrupta descartado |
| Aplicar RN-05 | `ingesta_modulo.py` | `cargar_aeronaves_csv()` | UT-RN-01 | Aeronave bajo 100 ft excluida |
| Calcular maxima aproximacion entre pares | `calculo_cinematico_modulo.py` | `calcular_proyecciones()` | UT-NORM-01 | Par convergente disponible para alerta |
| Mantener separacion horizontal segura | `calculo_cinematico_modulo.py` | `calcular_proyecciones()` | UT-NORM-02 | Par paralelo conserva 6 NM |
| Clasificar conflicto inminente | `motor_alertas_modulo.py` | `evaluar_alerta()` | UT-NORM-01 | Alerta ROJO |
| Clasificar vuelo sin conflicto | `motor_alertas_modulo.py` | `evaluar_alerta()` | UT-NORM-02 | Alerta VERDE |
| Evaluar alertas de todos los pares | `motor_alertas_modulo.py` | `evaluar_alertas()` | UT-NORM-01 / UT-NORM-02 | Lista de alertas generada |
| Validar borde de 5.00 NM | `motor_alertas_modulo.py` | `evaluar_alerta()` | UT-BORD-01 | Alerta VERDE |
| Validar borde de 2.00 minutos | `motor_alertas_modulo.py` | `evaluar_alerta()` | UT-BORD-02 | Alerta AMARILLO |
| RT-02 Validación cruzada Java/Python | `validador_consistencia_modulo.py` / `java/SastaCalculator.java` | `comparar_resultados()` | Auditoría cruzada | Diferencias `<= 0.01` y estado OK |

## Justificacion de calidad

La demo aplica separacion modular entre ingesta, calculo cinematico, reglas de alerta y ejecucion por consola. La validacion temprana de entradas evita que datos corruptos avancen al calculo, mientras que la tolerancia a errores permite continuar la ejecucion aunque existan filas invalidas. Los logs entregan evidencia de auditoria sobre descartes y exclusiones. Las pruebas unitarias automatizadas verifican casos normales, bordes y errores, y la matriz resume la trazabilidad requisito-diseno-codigo-prueba.

## Plan de Demo y Evidencia de Ejecución

La demo se realizara mediante una interfaz de consola estilizada, cargando datos desde un archivo CSV y mostrando alertas VERDE, AMARILLO y ROJO. Esta decision permite evidenciar de forma simple y verificable la ingesta de datos desde CSV, validacion de entradas, aplicacion de la regla RN-05, calculo cinematico, motor de alertas, manejo de errores, generacion de logs, ejecucion de pruebas unitarias y trazabilidad entre requisitos, diseno, codigo y pruebas.

| Paso de demo | Acción | Evidencia esperada |
| --- | --- | --- |
| 1 | Mostrar estructura del repositorio | Carpetas `data/`, `src/`, `tests/`, `logs/` y `README.md` |
| 2 | Mostrar dataset CSV | Archivo `data/aeronaves_demo.csv` con casos normales, error y regla de negocio; los casos borde se evidencian mediante pruebas unitarias |
| 3 | Ejecutar `python src/main.py` | Salida por consola con aeronaves validas, registros descartados y pares evaluados |
| 4 | Observar alertas | `V01-V02` genera ROJO; `V05-V06` genera VERDE |
| 5 | Mostrar logs de errores | `V15` descartada por altitud negativa, `V16` por velocidad corrupta y `V17` por RN-05 |
| 6 | Ejecutar `python -m pytest -v` | 10 pruebas aprobadas (unitarias, integracion y estres) |
| 7 | Mostrar matriz de trazabilidad | Relacion entre requisito, modulo, funcion implementada, caso de prueba y resultado esperado |
| 8 | Justificar decisiones de calidad | Separacion modular, validacion temprana, tolerancia a errores, logs y pruebas automatizadas |

## Evidencia de ejecución actual

- `python src/main.py` ejecutado correctamente.
- Resultado principal: 4 aeronaves validas, 3 registros descartados y 6 pares evaluados.
- `python -m pytest -v` ejecutado correctamente.
- Resultado: 10 pruebas aprobadas (unitarias, integracion y estres).
- Dataset de estres `data/aeronaves_stress_la_serena_200.csv` generado con 200 aeronaves validas.
- Validacion cruzada Java/Python ejecutada correctamente.
- Resultado: todos los pares comparados quedan en estado OK con tolerancia `<= 0.01`.
