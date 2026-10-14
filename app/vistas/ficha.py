"""Vista 3 — Ficha de alcaldía.

Para quien asigna recursos: qué dice el mapa oficial de una alcaldía y si su
visibilidad (d, k, R) es distinta a la del resto de la ciudad.
"""
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from datos import (COLOR, GEOGRAFIAS, PERIODOS, VARIANTES_C, estimaciones_alcaldia, ic_logit,
                   mapa_corregido, nivel_ciudad, plano_dk, razones_tiempo, residencia)

ETAPAS = {
    "d": "Se denuncia",
    "k": "La denuncia llega a carpeta",
    "R": "Queda registrado",
}
# Comparaciones por azar esperadas: 16 alcaldías × 3 indicadores × 5%
FALSAS_ESPERADAS = 16 * 3 * 0.05


# ---------------------------------------------------------------------------
def visibilidad(alc: str, periodo: str, geografia: str) -> dict:
    """d, k y R de la alcaldía con su intervalo, y de dónde salen."""
    if periodo == "2020_2024":
        if geografia == "residencia":
            f = residencia().set_index("alc").loc[alc]
            est = {p: f[f"{p}_res"] for p in ETAPAS}
            ee = {p: f[f"ee_{p}_res"] for p in ETAPAS}
        else:
            f = plano_dk().set_index("alc").loc[alc]
            est = {p: f[p] for p in ETAPAS}
            ee = {p: np.sqrt(f[f"var_{p}"]) for p in ETAPAS}
        fuente = "estimación directa de la encuesta, cinco años agrupados"
        salida = {}
        for p in ETAPAS:
            lo, hi = ic_logit(est[p], ee[p])
            salida[p] = {"est": est[p], "inf": float(lo), "sup": float(hi)}
        return salida, fuente

    e = estimaciones_alcaldia()
    e = e[(e["alc"] == alc) & (e["anio_ref"] == int(periodo))].set_index("param")
    salida = {p: {"est": e.loc[p, "p_bench_consistente"], "inf": e.loc[p, "ic95_inf_bench"],
                  "sup": e.loc[p, "ic95_sup_bench"]} for p in ETAPAS}
    return salida, "modelo de áreas pequeñas ajustado al total de la ciudad"


def rangos_comunes(alcs, periodo: str, geografia: str) -> dict:
    """Eje de cada indicador fijo para las 16 alcaldías: al cambiar de alcaldía la
    escala no se mueve y los intervalos se pueden comparar a simple vista."""
    todos = [visibilidad(a, periodo, geografia)[0] for a in alcs]
    rangos = {}
    for p in ETAPAS:
        lo = min(t[p]["inf"] for t in todos) * 100
        hi = max(t[p]["sup"] for t in todos) * 100
        margen = (hi - lo) * 0.05
        rangos[p] = [max(0, lo - margen), min(100, hi + margen)]
    return rangos


def figura_visibilidad(v: dict, ciudad: dict, nombre: str, rangos: dict):
    fig = make_subplots(rows=3, cols=1, subplot_titles=list(ETAPAS.values()),
                        vertical_spacing=0.2)
    for fila, p in enumerate(ETAPAS, start=1):
        filas = [(nombre, v[p], COLOR["carpeta"], "circle")]
        if ciudad.get(p) is not None:
            filas.append(("Toda la ciudad", ciudad[p], COLOR["tenue"], "diamond"))
        for etiqueta, x, color, simbolo in filas:
            fig.add_trace(go.Scatter(
                x=[x["est"] * 100], y=[etiqueta], mode="markers",
                marker=dict(size=11, color=color, symbol=simbolo),
                error_x=dict(type="data", symmetric=False,
                             array=[(x["sup"] - x["est"]) * 100],
                             arrayminus=[(x["est"] - x["inf"]) * 100],
                             color=color, thickness=2, width=6),
                hovertemplate=f"{etiqueta}: %{{x:.1f}}% "
                              f"({x['inf'] * 100:.1f} a {x['sup'] * 100:.1f})<extra></extra>",
            ), row=fila, col=1)
        fig.update_xaxes(ticksuffix="%", gridcolor="#E6EBF0", zeroline=False,
                         range=rangos[p], row=fila, col=1)
        fig.update_yaxes(autorange="reversed", row=fila, col=1)
    fig.update_layout(height=380, showlegend=False, plot_bgcolor="white",
                      paper_bgcolor="white", margin=dict(l=0, r=10, t=30, b=10))
    return fig


def lectura(nombre: str, v: dict, ciudad: dict, mapa, pct_nr, mediana_nr,
            geografia: str) -> str:
    """El texto que interpreta la ficha. Solo afirma lo que los intervalos sostienen."""
    distintos = []
    for p in ETAPAS:
        c = ciudad.get(p)
        if c is not None and not (v[p]["inf"] <= c["est"] <= v[p]["sup"]):
            arriba = v[p]["est"] > c["est"]
            distintos.append((p, arriba))

    partes = []
    if not distintos:
        partes.append(
            f"**{nombre} no se distingue del resto de la ciudad.** Aquí la gente denuncia y "
            "las denuncias llegan a carpeta en la misma proporción que en toda la CDMX: "
            "las diferencias que se ven en la gráfica caben dentro del margen de error."
        )
    else:
        descr = ", ".join(
            f"{ETAPAS[p].lower()} {'más' if arriba else 'menos'} que el promedio"
            for p, arriba in distintos)
        cuantos = "un indicador sale" if len(distintos) == 1 else "dos indicadores salen" \
            if len(distintos) == 2 else "los tres indicadores salen"
        partes.append(f"**En {nombre}, {cuantos} del rango de la ciudad:** {descr}.")
        if geografia == "residencia" and any(p == "k" for p, _ in distintos):
            partes.append(
                "Por alcaldía donde vive la víctima, la proporción de denuncias que llegan a "
                "carpeta **sí varía entre alcaldías** más de lo que explica el azar. Es la "
                "única barrera con diferencias territoriales detectables, y solo con esta "
                "geografía."
            )
        else:
            partes.append(
                f"Tómalo como señal a vigilar, no como hallazgo: al comparar 16 alcaldías en "
                f"tres indicadores se esperan unos {FALSAS_ESPERADAS:.0f} casos así por puro "
                "azar, y la prueba que usa todas las alcaldías juntas no encuentra diferencias "
                "persistentes entre ellas."
            )

    if not distintos:
        partes.append(
            f"Su lugar {mapa['rango_obs']} de 16 en el mapa oficial se explica por **cuántos "
            "delitos ocurren ahí y quién llega a sufrirlos**, no por cuánto se denuncia."
        )
    if pct_nr is not None:
        if pct_nr > mediana_nr:
            partes.append(
                f"Además, {pct_nr:.0f} de cada 100 víctimas de delitos ocurridos aquí viven en "
                "otra alcaldía: la tasa por habitante se infla con personas que no viven ahí."
            )
        else:
            partes.append(
                f"Casi todas las víctimas son vecinas: solo {pct_nr:.0f} de cada 100 viven en "
                "otra alcaldía."
            )
    partes.append(
        "**Para decidir:** focalizar aquí campañas para que la gente denuncie no tiene "
        "respaldo en estos datos. Donde sí hay margen es en los delitos que casi no se "
        "denuncian y en las denuncias que no llegan a carpeta, en toda la ciudad."
        if not distintos else
        "**Para decidir:** antes de dirigir recursos aquí con base en esto, conviene "
        "confirmar que la diferencia se repite en otros años."
    )
    return "\n\n".join(partes)


# ---------------------------------------------------------------------------
periodo = st.session_state.get("periodo", "2020_2024")
variante = st.session_state.get("variante_c", "C_nucleo")
geografia = st.session_state.get("geografia", "ocurrencia")
if periodo != "2020_2024":
    geografia = "ocurrencia"

mapa = mapa_corregido()
mapa = mapa[(mapa["variante_C"] == variante) & (mapa["periodo"] == periodo)
            & (mapa["fuente_R"] == "FH_benchmark")]
nombres = dict(zip(mapa["nombre"], mapa["alc"]))
opciones = sorted(nombres)

st.title("Ficha de alcaldía")
nombre = st.selectbox("Alcaldía", opciones, index=opciones.index("Cuauhtémoc"), key="alcaldia")
alc = nombres[nombre]
m = mapa.set_index("alc").loc[alc]

v, fuente = visibilidad(alc, periodo, geografia)
ciudad = {}
for p in ETAPAS:
    c = nivel_ciudad(p, periodo)
    if c is not None:
        ciudad[p] = {"est": c["est"], "inf": c["ic95_inf"], "sup": c["ic95_sup"]}

res = residencia()
pct_nr = float(res.set_index("alc").loc[alc, "pct_no_residente"])
mediana_nr = float(res["pct_no_residente"].median())

st.caption(f"{PERIODOS[periodo]}. Carpetas: {VARIANTES_C[variante].lower()}. "
           f"Alcaldía asignada según: {GEOGRAFIAS[geografia].lower()}.")

# --- Lectura primero: es lo que el tomador de decisiones necesita ------------
st.info(lectura(nombre, v, ciudad, m, pct_nr, mediana_nr, geografia))

# --- Lo que dice el mapa oficial --------------------------------------------
st.subheader("Lo que dice el mapa oficial")
c1, c2, c3 = st.columns(3)
c1.metric("Carpetas por cada 100 mil adultos", f"{m['tasa_obs']:,.0f}",
          help="Conteo de carpetas de la Fiscalía entre la población de 18 años y más. "
               "Es un registro administrativo, no una estimación: no tiene margen de error.")
c2.metric("Lugar en la ciudad", f"{m['rango_obs']} de 16",
          help="1 = la tasa de carpetas más alta.")
inf_r, sup_r = int(m["rango_corr_ic_inf"]), int(m["rango_corr_ic_sup"])
c3.metric("Lugar si se corrige por visibilidad",
          f"{inf_r} de 16" if inf_r == sup_r else f"entre {inf_r} y {sup_r}",
          help="Lugar que tendría si se contaran también los delitos que no se denuncian o "
               "no llegan a carpeta. Rango de 95% por simulación.")
c3.caption(f"Probabilidad de moverse más de 2 lugares: {m['prob_mueve_mas_2'] * 100:.0f}%")

# --- Visibilidad --------------------------------------------------------------
st.subheader("¿Qué tan visible es el delito aquí?")
rangos = rangos_comunes(list(nombres.values()), periodo, geografia)
st.plotly_chart(figura_visibilidad(v, ciudad, nombre, rangos), width="stretch",
                config={"displayModeBar": False}, key="ficha_vis")
st.caption(f"Punto: estimación; línea: rango de 95%. Cada eje abarca lo que ocupan las 16 "
           f"alcaldías, así que la escala no cambia al elegir otra. Fuente: {fuente}.")

# --- Víctimas de fuera ---------------------------------------------------------
st.subheader("¿De dónde son las víctimas?")
orden_nr = int((res["pct_no_residente"] > pct_nr).sum()) + 1
col_a, col_b = st.columns([1, 2])
col_a.metric("Víctimas que viven en otra alcaldía", f"{pct_nr:.0f}%")
col_a.caption(f"Lugar {orden_nr} de 16, promedio 2020–2024")
col_b.markdown(
    "Las carpetas se cuentan donde ocurre el delito, pero la tasa se divide entre quienes "
    "**viven** ahí. En alcaldías a donde mucha gente llega a trabajar o a pasear, la tasa "
    f"oficial sube aunque sus vecinos no sean más víctimas. En la ciudad, este porcentaje va "
    f"de {res['pct_no_residente'].min():.0f}% a {res['pct_no_residente'].max():.0f}%."
)
col_b.caption("Proporción estimada con la encuesta; el archivo de resultados no incluye "
              "su margen de error.")

# --- Rezago de registro --------------------------------------------------------
with st.expander("¿Cuánto tarda en iniciarse una carpeta aquí?"):
    rt = razones_tiempo().set_index("termino")
    clave = f"Alcaldía: {nombre}"
    if clave not in rt.index:
        st.markdown(f"**{nombre} es el punto de comparación** de este análisis: las demás "
                    "alcaldías se miden contra ella.")
    else:
        f = rt.loc[clave]
        texto = (f["lectura"].replace("la mediana", "el tiempo típico")
                 .replace("más corta", "más corto").replace("más larga", "más largo"))
        st.markdown(
            f"Comparado con Cuauhtémoc, **{texto}** "
            f"(entre {f['ic95_inf']:.2f} y {f['ic95_sup']:.2f} veces). "
            + ("La diferencia es clara." if f["significativo"] == "sí"
               else "La diferencia cabe en el margen de error.")
        )
    st.caption("Días entre el delito y el inicio de la carpeta, con carpetas de la Fiscalía "
               "2020–2024 de los delitos comparables cometidos entre enero y marzo, seguidas "
               "hasta 120 días, descontando tipo de delito, año, canal digital y violencia. "
               "Técnicamente: razón de tiempos de un modelo de tiempo de "
               "falla acelerado log-logístico con censura por intervalos.")
