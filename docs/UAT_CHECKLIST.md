# UAT Checklist - SASTA

Checklist de aceptacion para usuario, revisor o docente.

## Preparacion

- [ ] Activar entorno Python del proyecto.
- [ ] Instalar dependencias con `pip install -r requirements.txt`.
- [ ] Confirmar Java 17 o superior con `java -version`.
- [ ] Generar dataset de estres con `python scripts/generar_dataset_estres.py`.

## Demo funcional

- [ ] Ejecutar demo por consola con `python src/main.py`.
- [ ] Confirmar 4 aeronaves validas en `data/aeronaves_demo.csv`.
- [ ] Confirmar 3 registros descartados.
- [ ] Confirmar 6 pares evaluados.
- [ ] Verificar que `V01-V02` aparece como ROJO.
- [ ] Verificar que `V05-V06` aparece como VERDE.

## Dashboard Streamlit

- [ ] Abrir dashboard con `streamlit run app_streamlit.py`.
- [ ] Revisar seccion "Modo demo".
- [ ] Probar filtro TODAS.
- [ ] Probar filtro ROJO y confirmar `V01-V02`.
- [ ] Probar filtro VERDE y confirmar `V05-V06`.
- [ ] Confirmar que la visualizacion 2D tipo radar sigue disponible.
- [ ] Revisar registros descartados.
- [ ] Revisar validacion cruzada Java/Python cuando existan los CSV generados.

## Calidad y cierre

- [ ] Ejecutar `python -m ruff check .`.
- [ ] Ejecutar `python -m pytest --cov=src --cov=scripts --cov-report=term-missing --cov-report=xml`.
- [ ] Ejecutar `python -m bandit -r src scripts app_streamlit.py`.
- [ ] Ejecutar `python scripts/verificar_entrega.py`.
- [ ] Confirmar que GitHub Actions esta en verde en el repositorio remoto.

## Criterio de aceptacion

- [ ] No se observan errores bloqueantes.
- [ ] No se modifican reglas de negocio durante la validacion.
- [ ] La evidencia de consola, dashboard, pruebas y CI/CD es consistente.
