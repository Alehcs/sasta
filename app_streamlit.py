"""Dashboard Streamlit para la demo visual del sistema SASTA."""

from pathlib import Path
import tempfile

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from src.calculo_cinematico_modulo import calcular_proyecciones, descomponer_velocidad
from src.ingesta_modulo import cargar_aeronaves_csv
from src.motor_alertas_modulo import evaluar_alertas
from src.validador_consistencia_modulo import comparar_resultados


BASE_DIR = Path(__file__).resolve().parent
RUTA_CSV_DEMO = BASE_DIR / "data" / "aeronaves_demo.csv"
RUTA_LOG_APP = BASE_DIR / "logs" / "errores_streamlit.log"
RUTA_RESULTADOS_PYTHON = BASE_DIR / "data" / "resultados_python.csv"
RUTA_RESULTADOS_JAVA = BASE_DIR / "data" / "resultados_java.csv"


def main():
    """Ejecuta la interfaz visual del sistema SASTA."""
    st.set_page_config(layout="wide", page_title="SASTA Demo")
    _aplicar_estilos_dark()

    st.markdown("### SASTA - Sistema de Alerta de Separación y Tráfico Aéreo")
    st.caption("Demo visual del núcleo de validación, cálculo cinemático, alertas y validación cruzada.")

    archivo_subido = st.file_uploader("Cargar CSV alternativo", type=["csv"])
    ruta_csv, usando_temporal = _resolver_csv(archivo_subido)

    try:
        aeronaves, descartados = _cargar_datos(ruta_csv)
    finally:
        if usando_temporal:
            Path(ruta_csv).unlink(missing_ok=True)

    resultados_calculo = calcular_proyecciones(aeronaves)
    resultados_alerta = evaluar_alertas(resultados_calculo)
    aeronaves_por_id = {aeronave.id: aeronave for aeronave in aeronaves}

    st.caption(f"Archivo procesado: {ruta_csv if not usando_temporal else archivo_subido.name}")
    _mostrar_metricas(aeronaves, descartados, resultados_alerta)
    _mostrar_modo_demo(ruta_csv, usando_temporal, archivo_subido, aeronaves, descartados, resultados_alerta)
    filtro_alerta = _seleccionar_filtro_alerta()
    resultados_alerta_filtrados = _filtrar_alertas(resultados_alerta, filtro_alerta)

    columna_izquierda, columna_derecha = st.columns([1.05, 0.95], gap="medium")
    with columna_izquierda:
        _mostrar_tabla_alertas(resultados_alerta_filtrados, filtro_alerta)
        par_seleccionado = _seleccionar_par(resultados_alerta_filtrados)

    with columna_derecha:
        _mostrar_radar(aeronaves_por_id, resultados_calculo, resultados_alerta, par_seleccionado)

    _mostrar_descartados(descartados)
    _mostrar_validacion_cruzada()
    _mostrar_evidencia_calidad()


def _aplicar_estilos_dark():
    """Aplica una paleta oscura compacta para la demo visual."""
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] {
            background: #0b1120;
            color: #e5e7eb;
        }
        .block-container {
            padding-top: 4.25rem;
            padding-bottom: 1rem;
        }
        div[data-testid="stVerticalBlock"] {
            gap: 0.6rem;
        }
        h3 {
            margin-top: 0.35rem;
            margin-bottom: 0.25rem;
            color: #f9fafb;
        }
        p, label, span {
            color: #e5e7eb;
        }
        div[data-testid="stMetric"] {
            background: linear-gradient(180deg, #1f2937 0%, #111827 100%);
            border: 1px solid #374151;
            border-radius: 6px;
            padding: 0.45rem 0.6rem;
            box-shadow: 0 6px 18px rgba(0, 0, 0, 0.22);
        }
        div[data-testid="stMetricLabel"] p {
            color: #cbd5e1;
            font-size: 0.82rem;
        }
        div[data-testid="stMetricValue"] {
            color: #f9fafb;
            font-size: 1.35rem;
        }
        [data-testid="stExpander"] {
            background: #111827;
            border: 1px solid #374151;
            border-radius: 6px;
        }
        [data-testid="stExpander"] summary {
            color: #f9fafb;
        }
        [data-testid="stFileUploader"] section {
            background: #111827;
            border: 1px dashed #4b5563;
        }
        [data-testid="stSelectbox"] div {
            color: #e5e7eb;
        }
        .sasta-summary {
            background: #111827;
            border: 1px solid #374151;
            border-radius: 6px;
            padding: 0.55rem 0.7rem;
            color: #e5e7eb;
            font-size: 0.9rem;
            line-height: 1.45;
            box-shadow: 0 6px 18px rgba(0, 0, 0, 0.18);
        }
        .sasta-summary b {
            color: #f9fafb;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _resolver_csv(archivo_subido):
    """Devuelve la ruta del CSV demo o una copia temporal del archivo subido."""
    if archivo_subido is None:
        return RUTA_CSV_DEMO, False

    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temporal:
        temporal.write(archivo_subido.getvalue())
        return Path(temporal.name), True


def _cargar_datos(ruta_csv):
    """Carga aeronaves usando el modulo de ingesta existente."""
    RUTA_LOG_APP.parent.mkdir(parents=True, exist_ok=True)
    RUTA_LOG_APP.unlink(missing_ok=True)
    return cargar_aeronaves_csv(ruta_csv, RUTA_LOG_APP)


def _mostrar_metricas(aeronaves, descartados, resultados_alerta):
    """Muestra indicadores principales de la demo en dos filas."""
    conteos_alertas = {"ROJO": 0, "AMARILLO": 0, "VERDE": 0}
    for resultado in resultados_alerta:
        conteos_alertas[resultado.alerta] += 1

    fila_1 = st.columns(3)
    fila_1[0].metric("Aeronaves válidas", len(aeronaves))
    fila_1[1].metric("Registros descartados", len(descartados))
    fila_1[2].metric("Pares evaluados", len(resultados_alerta))

    fila_2 = st.columns(3)
    fila_2[0].metric("Alertas ROJAS", conteos_alertas["ROJO"])
    fila_2[1].metric("Alertas AMARILLAS", conteos_alertas["AMARILLO"])
    fila_2[2].metric("Alertas VERDES", conteos_alertas["VERDE"])


def _mostrar_modo_demo(
    ruta_csv,
    usando_temporal,
    archivo_subido,
    aeronaves,
    descartados,
    resultados_alerta,
):
    """Muestra una guia compacta para ejecutar la demo ante revisores."""
    dataset = archivo_subido.name if usando_temporal else Path(ruta_csv).name
    caso_rojo = _describir_caso_principal(resultados_alerta, "V01", "V02")
    caso_verde = _describir_caso_principal(resultados_alerta, "V05", "V06")

    with st.expander("Modo demo", expanded=True):
        st.markdown(
            f"""
            <div class="sasta-summary">
            <b>Dataset:</b> {dataset}<br>
            <b>Aeronaves validas:</b> {len(aeronaves)} &nbsp;|&nbsp;
            <b>Registros descartados:</b> {len(descartados)} &nbsp;|&nbsp;
            <b>Pares evaluados:</b> {len(resultados_alerta)}<br>
            <b>Caso ROJO principal:</b> {caso_rojo} &nbsp;|&nbsp;
            <b>Caso VERDE principal:</b> {caso_verde}
            </div>
            """,
            unsafe_allow_html=True,
        )


def _describir_caso_principal(resultados_alerta, id_a, id_b):
    """Devuelve la alerta observada para un par esperado de la demo."""
    for resultado in resultados_alerta:
        if {resultado.id_a, resultado.id_b} == {id_a, id_b}:
            return f"{id_a}-{id_b}: {resultado.alerta}"

    return f"{id_a}-{id_b}: no disponible"


def _seleccionar_filtro_alerta():
    """Permite filtrar visualmente la tabla y selector por nivel de alerta."""
    return st.radio(
        "Filtro de alertas",
        ["TODAS", "ROJO", "AMARILLO", "VERDE"],
        horizontal=True,
    )


def _filtrar_alertas(resultados_alerta, filtro_alerta):
    """Retorna los resultados visibles segun el filtro seleccionado."""
    if filtro_alerta == "TODAS":
        return resultados_alerta

    return [
        resultado
        for resultado in resultados_alerta
        if resultado.alerta == filtro_alerta
    ]


def _mostrar_tabla_alertas(resultados_alerta, filtro_alerta):
    """Muestra una tabla coloreada con las alertas calculadas."""
    st.subheader(f"Alertas ({filtro_alerta})")
    filas = []

    for resultado in resultados_alerta:
        filas.append(
            {
                "Par": f"{resultado.id_a}-{resultado.id_b}",
                "Tiempo(min)": round(resultado.tiempo_min, 2),
                "Dist.H(NM)": round(_normalizar_cero(resultado.distancia_horizontal_nm), 2),
                "Dist.V(ft)": round(resultado.distancia_vertical_ft, 2),
                "Alerta": resultado.alerta,
            }
        )

    if not filas:
        st.info("No hay pares evaluados para el filtro seleccionado.")
        return

    dataframe = pd.DataFrame(filas)
    st.dataframe(
        _estilizar_tabla_oscura(dataframe).apply(_colorear_alerta, axis=1),
        width="stretch",
        hide_index=True,
        height=245,
    )


def _seleccionar_par(resultados_alerta):
    """Permite elegir el par que se mostrara en el radar."""
    if not resultados_alerta:
        return None

    opciones = [f"{resultado.id_a}-{resultado.id_b}" for resultado in resultados_alerta]
    return st.selectbox("Par para visualización 2D", opciones)


def _mostrar_radar(aeronaves_por_id, resultados_calculo, resultados_alerta, par_seleccionado):
    """Dibuja una vista 2D tipo radar para el par seleccionado."""
    st.subheader("Visualización 2D tipo radar")

    if not resultados_alerta or par_seleccionado is None:
        st.info("No hay pares disponibles para visualizar.")
        return

    alertas_por_par = {
        f"{resultado.id_a}-{resultado.id_b}": resultado
        for resultado in resultados_alerta
    }
    calculos_por_par = {
        f"{resultado.id_a}-{resultado.id_b}": resultado
        for resultado in resultados_calculo
    }
    alerta = alertas_por_par[par_seleccionado]
    calculo = calculos_por_par[par_seleccionado]
    aeronave_a = aeronaves_por_id[calculo.id_a]
    aeronave_b = aeronaves_por_id[calculo.id_b]

    _mostrar_resumen_par(alerta)
    figura, eje = plt.subplots(figsize=(5, 4), dpi=100)
    figura.patch.set_facecolor("#0b1120")
    eje.set_facecolor("#111827")
    _dibujar_aeronave(eje, aeronave_a, calculo.tiempo_min, "Aeronave A")
    _dibujar_aeronave(eje, aeronave_b, calculo.tiempo_min, "Aeronave B")
    eje.set_title("Proyección 2D del par seleccionado", fontsize=10, color="#f9fafb")
    eje.set_xlabel("Posición X (NM)", fontsize=9, color="#e5e7eb")
    eje.set_ylabel("Posición Y (NM)", fontsize=9, color="#e5e7eb")
    eje.tick_params(labelsize=8, colors="#cbd5e1")
    eje.grid(True, alpha=0.24, color="#475569")
    for spine in eje.spines.values():
        spine.set_color("#475569")
    leyenda = eje.legend(fontsize=7, loc="best", facecolor="#111827", edgecolor="#374151")
    for texto in leyenda.get_texts():
        texto.set_color("#e5e7eb")
    figura.tight_layout()
    st.pyplot(figura, width="content")
    plt.close(figura)


def _mostrar_resumen_par(resultado):
    """Muestra resumen compacto del par seleccionado."""
    st.markdown(
        f"""
        <div class="sasta-summary">
        <b>Par:</b> {resultado.id_a}-{resultado.id_b}<br>
        <b>Tiempo crítico:</b> {resultado.tiempo_min:.2f} min<br>
        <b>Distancia horizontal:</b> {_normalizar_cero(resultado.distancia_horizontal_nm):.2f} NM<br>
        <b>Distancia vertical:</b> {resultado.distancia_vertical_ft:.2f} ft<br>
        <b>Alerta:</b> {resultado.alerta}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _mostrar_descartados(descartados):
    """Muestra registros descartados por validacion de entrada."""
    with st.expander("Ver registros descartados", expanded=False):
        if not descartados:
            st.success("No hubo registros descartados.")
            return

        filas = [
            {
                "Fila": descarte["fila"],
                "ID": descarte["datos"].get("id", "SIN_ID"),
                "Motivo": descarte["motivo"],
            }
            for descarte in descartados
        ]
        dataframe = pd.DataFrame(filas)
        st.dataframe(
            _estilizar_tabla_oscura(dataframe),
            width="stretch",
            hide_index=True,
            height=180,
        )


def _mostrar_validacion_cruzada():
    """Muestra la evidencia de consistencia Java/Python si existe."""
    with st.expander("Validación cruzada Java/Python", expanded=False):
        if not RUTA_RESULTADOS_PYTHON.exists() or not RUTA_RESULTADOS_JAVA.exists():
            st.info(
                "Para generar la evidencia de validación cruzada, ejecutar:\n\n"
                "```powershell\n"
                "python src/exportar_resultados_python.py\n"
                "javac java/SastaCalculator.java\n"
                "java -cp java SastaCalculator\n"
                "python src/validador_consistencia_modulo.py\n"
                "```"
            )
            return

        resultados = comparar_resultados(RUTA_RESULTADOS_PYTHON, RUTA_RESULTADOS_JAVA)
        pares_ok = sum(1 for resultado in resultados if resultado["estado"] == "OK")
        pares_revisar = sum(1 for resultado in resultados if resultado["estado"] == "REVISAR")

        columnas = st.columns(3)
        columnas[0].metric("Pares comparados", len(resultados))
        columnas[1].metric("Pares OK", pares_ok)
        columnas[2].metric("Pares REVISAR", pares_revisar)

        filas = [
            {
                "Par": resultado["par"],
                "Diff tiempo": _formatear_diferencia(resultado["diferencia_tiempo"]),
                "Diff H": _formatear_diferencia(resultado["diferencia_horizontal"]),
                "Diff V": _formatear_diferencia(resultado["diferencia_vertical"]),
                "Estado": resultado["estado"],
            }
            for resultado in resultados
        ]
        dataframe = pd.DataFrame(filas)
        st.dataframe(
            _estilizar_tabla_oscura(dataframe).apply(_colorear_estado, axis=1),
            width="stretch",
            hide_index=True,
            height=245,
        )


def _mostrar_evidencia_calidad():
    """Resume evidencias de calidad del proyecto."""
    with st.expander("Evidencia de calidad", expanded=False):
        st.markdown(
            """
            - Modularidad entre ingesta, cálculo, alertas y presentación.
            - Validación temprana de entradas.
            - Manejo de errores y logs.
            - Pruebas unitarias con `pytest`.
            - Trazabilidad requisito-diseño-código-prueba.
            - Validación cruzada RT-02 Java/Python.
            """
        )


def _dibujar_aeronave(eje, aeronave, tiempo_min, etiqueta):
    """Dibuja posicion inicial, trayectoria y punto futuro de una aeronave."""
    vx, vy = descomponer_velocidad(aeronave)
    x_futuro = aeronave.pos_x + vx * tiempo_min
    y_futuro = aeronave.pos_y + vy * tiempo_min

    eje.scatter(aeronave.pos_x, aeronave.pos_y, s=45, label=f"{etiqueta} inicial")
    eje.plot([aeronave.pos_x, x_futuro], [aeronave.pos_y, y_futuro], linestyle="--", linewidth=1.2)
    eje.scatter(x_futuro, y_futuro, marker="x", s=55, label=f"{etiqueta} futuro")
    eje.annotate(
        aeronave.id,
        (aeronave.pos_x, aeronave.pos_y),
        textcoords="offset points",
        xytext=(4, 4),
        fontsize=8,
        color="#f9fafb",
    )


def _estilizar_tabla_oscura(dataframe):
    """Aplica estilo base oscuro a tablas de la app."""
    return (
        dataframe.style.set_properties(
            **{
                "background-color": "#111827",
                "color": "#e5e7eb",
                "border-color": "#374151",
            }
        )
        .set_table_styles(
            [
                {
                    "selector": "th",
                    "props": [
                        ("background-color", "#1f2937"),
                        ("color", "#f9fafb"),
                        ("border-color", "#374151"),
                    ],
                },
                {
                    "selector": "td",
                    "props": [
                        ("border-color", "#374151"),
                    ],
                },
            ]
        )
    )


def _colorear_alerta(fila):
    """Aplica fondo oscuro contrastado a la fila segun la alerta."""
    colores = {
        "ROJO": "background-color: #7f1d1d; color: #fecaca",
        "AMARILLO": "background-color: #854d0e; color: #fef3c7",
        "VERDE": "background-color: #14532d; color: #dcfce7",
    }
    return [colores.get(fila["Alerta"], "")] * len(fila)


def _colorear_estado(fila):
    """Aplica color de estado a filas de validacion cruzada."""
    colores = {
        "OK": "background-color: #166534; color: #dcfce7",
        "REVISAR": "background-color: #92400e; color: #ffedd5",
    }
    return [colores.get(fila["Estado"], "")] * len(fila)


def _normalizar_cero(valor):
    """Evita ruido numerico en distancias muy cercanas a cero."""
    if abs(valor) < 0.000001:
        return 0.0

    return valor


def _formatear_diferencia(valor):
    """Formatea diferencias numericas de validacion cruzada."""
    if valor is None:
        return "N/A"

    return f"{valor:.4f}"


if __name__ == "__main__":
    main()
