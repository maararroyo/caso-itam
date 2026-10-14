"""¿Qué tan visible es el delito en la CDMX? — punto de entrada.

Ejecutar con:  streamlit run app.py
"""
import streamlit as st

from datos import GEOGRAFIAS, PERIODOS, VARIANTES_C

st.set_page_config(
    page_title="¿Qué tan visible es el delito?",
    page_icon="🔎",
    layout="wide",
)

# ---- Panel de supuestos (compartido por todas las vistas) ------------------
# Los widgets viven aquí, no en cada página, para que el valor se conserve
# al cambiar de vista. Las páginas lo leen de st.session_state.
def _al_cambiar_periodo():
    """La geografía de residencia solo existe para el promedio 2020–2024."""
    if st.session_state.periodo != "2020_2024":
        st.session_state.geografia = "ocurrencia"


with st.sidebar:
    st.markdown("### Supuestos")
    st.selectbox(
        "Periodo",
        options=list(PERIODOS),
        format_func=PERIODOS.get,
        key="periodo",
        on_change=_al_cambiar_periodo,
        help="El promedio de cinco años es la estimación más precisa. "
             "Con un solo año, varias estimaciones por tipo de delito son poco precisas.",
    )
    st.selectbox(
        "Qué carpetas se cuentan",
        options=list(VARIANTES_C),
        format_func=VARIANTES_C.get,
        key="variante_c",
        help="Cambia la tasa oficial de carpetas y el ranking de alcaldías. "
             "No cambia el porcentaje de denuncia ni el de carpetas iniciadas.",
    )
    st.radio(
        "Alcaldía asignada según",
        options=list(GEOGRAFIAS),
        format_func=GEOGRAFIAS.get,
        key="geografia",
        disabled=st.session_state.get("periodo", "2020_2024") != "2020_2024",
        help="Por residencia solo hay estimaciones para el promedio 2020–2024. "
             "Cambia la ficha de alcaldía y los paneles de alcaldías.",
    )

pagina = st.navigation(
    [
        st.Page("vistas/embudo.py", title="El embudo de la visibilidad", icon="🔻", default=True),
        st.Page("vistas/donde_o_que.py", title="¿Dónde o qué?", icon="⚖️"),
        st.Page("vistas/ficha.py", title="Ficha de alcaldía", icon="📍"),
    ]
)
pagina.run()
