# Code Freeze - SASTA

## Fecha de congelamiento

2026-07-01

## Alcance congelado

Quedan congelados para entrega final academica:

- Reglas de negocio de alertas VERDE, AMARILLO y ROJO.
- Regla RN-05 de exclusion por altitud menor a 100 ft.
- Flujo de ingesta, validacion, calculo cinematico y motor de alertas.
- Demo por consola.
- Dashboard Streamlit.
- Validacion cruzada Java/Python.
- Pruebas automatizadas, dataset de estres, linting, cobertura y seguridad basica.
- Documentacion final de entrega.

## Comandos finales de verificacion

```powershell
python scripts/generar_dataset_estres.py
python -m ruff check .
python -m pytest --cov=src --cov=scripts --cov-report=term-missing --cov-report=xml
python -m bandit -r src scripts app_streamlit.py
python src/main.py
python src/exportar_resultados_python.py
javac java/SastaCalculator.java
java -cp java SastaCalculator
python src/validador_consistencia_modulo.py
python -m py_compile app_streamlit.py
python scripts/verificar_entrega.py
```

## Reglas de no modificacion

- No cambiar reglas de negocio.
- No alterar datasets de evidencia salvo regeneracion determinista documentada.
- No eliminar pruebas automatizadas.
- No relajar controles QA para ocultar fallos.
- No modificar el workflow de CI/CD sin ejecutar verificacion local.
- No integrar cambios sin revisar el checklist UAT.

## Excepciones permitidas

Solo se permiten cambios despues del congelamiento para:

- Correccion de bugs criticos que bloqueen la demo.
- Ajustes menores de documentacion.
- Correcciones de compatibilidad de entorno sin impacto funcional.

Toda excepcion debe quedar documentada con motivo, archivo afectado y evidencia de nueva verificacion.
