"""Vista 2 — ¿Dónde o qué?

La respuesta a la pregunta original: la visibilidad del delito varía mucho entre
tipos de delito y casi nada entre alcaldías. Todo con directos 2020–2024
agrupados, el mismo estimador en los dos lados de la comparación.
"""
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from datos import (ABREV, COLOR, TODOS, control_positivo, dispersion, ic_logit,
                   nivel_ciudad, plano_dk, potencia, residencia, tipos_delito)

PARAMS = {
    "d": "Que se denuncie",
    "k": "Que la denuncia llegue a carpeta",
    "R": "Que quede registrado",
}
EJE = {
    "d": "% de delitos que se denuncian",
    "k": "% de denuncias que llegan a carpeta",
    "R": "% de delitos que quedan registrados",
}
CHI2_2GL_95 = 5.991  # cuantil 0.95 de una ji cuadrada con 2 grados de libertad


# ---------------------------------------------------------------------------
# Datos de cada lado de la comparación
# ---------------------------------------------------------------------------
def puntos_tipos(param: str):
    """Tipos de delito, 2020–2024, solo estimaciones publicables (las mismas
    que entran al cálculo de dispersión)."""
    df = tipos_delito()
    df = df[(df["periodo"] == "2020_2024") & (df["param"] == param) & (df["tipo"] != TODOS)]
    omitidos = int((~df["publicable"]).sum())
    df = df[df["publicable"]].sort_values("est")
    return (df["tipo"].tolist(), df["est"].to_numpy(), df["ic95_inf"].to_numpy(),
            df["ic95_sup"].to_numpy(), omitidos)


def puntos_alcaldias(param: str, geografia: str):
    """Directos 2020–2024 por alcaldía, por ocurrencia o por residencia."""
    if geografia == "residencia":
        df = residencia()
        est, ee = df[f"{param}_res"].to_numpy(), df[f"ee_{param}_res"].to_numpy()
    else:
        df = plano_dk()
        est, ee = df[param].to_numpy(), np.sqrt(df[f"var_{param}"].to_numpy())
    inf, sup = ic_logit(est, ee)
    orden = np.argsort(est)
    return df["nombre"].to_numpy()[orden], est[orden], inf[orden], sup[orden]


# ---------------------------------------------------------------------------
# Figuras
# ---------------------------------------------------------------------------
def figura_dos_paneles(param: str, geografia: str):
    n_t, e_t, i_t, s_t, omitidos = puntos_tipos(param)
    n_a, e_a, i_a, s_a = puntos_alcaldias(param, geografia)

    fig = make_subplots(rows=1, cols=2, horizontal_spacing=0.22,
                        subplot_titles=("Entre tipos de delito", "Entre alcaldías"))
    lados = [(n_t, e_t, i_t, s_t, COLOR["carpeta"]), (n_a, e_a, i_a, s_a, COLOR["denuncia"])]
    for col, (nombres, e, i, s, color) in enumerate(lados, start=1):
        fig.add_trace(
            go.Scatter(
                x=e * 100, y=list(nombres), mode="markers",
                marker=dict(size=9, color=color),
                error_x=dict(type="data", symmetric=False, array=(s - e) * 100,
                             arrayminus=(e - i) * 100, color=color, thickness=1.5, width=0),
                hovertemplate="%{y}: %{x:.1f}%<extra></extra>",
            ),
            row=1, col=col,
        )

    # Misma escala horizontal en los dos paneles: es la clave de la vista
    tope = float(np.nanmax(np.concatenate([s_t, s_a]))) * 100
    rango = [0, min(100, tope * 1.08)]
    ciudad = nivel_ciudad(param)
    for col in (1, 2):
        fig.update_xaxes(range=rango, title_text=EJE[param], gridcolor="#E6EBF0",
                         zeroline=False, row=1, col=col)
        if ciudad is not None:
            fig.add_vline(x=ciudad["est"] * 100, line_dash="dot",
                          line_color=COLOR["tenue"], row=1, col=col)
    fig.update_yaxes(tickfont=dict(size=12))
    fig.update_layout(height=520, showlegend=False, plot_bgcolor="white",
                      paper_bgcolor="white", margin=dict(l=0, r=10, t=40, b=40))
    return fig, omitidos


def elipse(cx, cy, var_x, var_y, cov, n=60):
    """Contorno de la región de confianza al 95% de una normal bivariada."""
    valores, vectores = np.linalg.eigh(np.array([[var_x, cov], [cov, var_y]]))
    t = np.linspace(0, 2 * np.pi, n)
    circulo = np.stack([np.cos(t), np.sin(t)])
    puntos = vectores @ (np.sqrt(np.maximum(valores, 0) * CHI2_2GL_95)[:, None] * circulo)
    return cx + puntos[0], cy + puntos[1]


def figura_plano():
    pl = plano_dk()
    fig = go.Figure()
    for _, f in pl.iterrows():
        x, y = elipse(f["d"], f["k"], f["var_d"], f["var_k"], f["cov_dk"])
        fig.add_trace(go.Scatter(
            x=x * 100, y=np.clip(y, 0, 1) * 100, mode="lines", fill="toself",
            line=dict(width=0.6, color=COLOR["denuncia"]),
            fillcolor="rgba(91,141,184,0.07)", hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(
        x=pl["d"] * 100, y=pl["k"] * 100, mode="markers+text",
        text=[ABREV.get(a, a) for a in pl["alc"]], textposition="top center",
        textfont=dict(size=10, color=COLOR["tinta"]),
        marker=dict(size=7, color=COLOR["denuncia"]),
        customdata=pl["nombre"], name="Alcaldías",
        hovertemplate="%{customdata}<br>Se denuncia: %{x:.1f}%<br>"
                      "Llega a carpeta: %{y:.1f}%<extra></extra>"))

    cd, ck = nivel_ciudad("d"), nivel_ciudad("k")
    if cd is not None:
        fig.add_vline(cd["est"] * 100, line_dash="dot", line_color=COLOR["tenue"])
    if ck is not None:
        fig.add_hline(ck["est"] * 100, line_dash="dot", line_color=COLOR["tenue"])

    fig.update_layout(
        height=520, plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=0, r=10, t=10, b=40),
        showlegend=False,
        xaxis=dict(title=EJE["d"], gridcolor="#E6EBF0", zeroline=False, range=[2, 20]),
        yaxis=dict(title=EJE["k"], gridcolor="#E6EBF0", zeroline=False, range=[30, 100]),
    )
    return fig


def figura_potencia(param: str):
    sim = potencia()
    sim = sim[(sim["bloque"] == "simulacion") & (sim["param"] == param)]
    fig = go.Figure()
    estilos = {"carpetas": ("Con el mismo orden que las carpetas", COLOR["carpeta"], "solid"),
               "aleatorio": ("Con un orden al azar", COLOR["denuncia"], "dash")}
    for patron, (etiqueta, color, guion) in estilos.items():
        s = sim[sim["patron"] == patron].sort_values("razon_inyectada")
        x = s["razon_inyectada"].to_numpy()
        y = s["potencia"].to_numpy()
        ee = s["ee_potencia"].to_numpy()
        fig.add_trace(go.Scatter(  # banda de ±1.96 errores estándar de simulación
            x=np.concatenate([x, x[::-1]]),
            y=np.concatenate([np.clip(y + 1.96 * ee, 0, 1),
                              np.clip(y - 1.96 * ee, 0, 1)[::-1]]) * 100,
            fill="toself", fillcolor=color, opacity=0.12, line=dict(width=0),
            hoverinfo="skip", showlegend=False))
        fig.add_trace(go.Scatter(
            x=x, y=y * 100, mode="lines+markers", name=etiqueta,
            line=dict(color=color, dash=guion), marker=dict(size=6),
            hovertemplate="Brecha de %{x:.2f} a 1: detectada %{y:.0f} de cada 100 veces"
                          "<extra></extra>"))
    fig.add_hline(80, line_dash="dot", line_color=COLOR["tenue"],
                  annotation_text="80 de cada 100", annotation_position="bottom right")
    if param != "k":
        fig.add_vline(3.54, line_dash="dot", line_color=COLOR["perdida"],
                      annotation_text="desigualdad del<br>mapa de carpetas",
                      annotation_position="bottom left")
    fig.update_layout(
        height=380, plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=0, r=10, t=30, b=40),
        legend=dict(orientation="h", y=-0.28, x=0),
        xaxis=dict(title="Brecha entre la alcaldía más alta y la más baja (veces)",
                   gridcolor="#E6EBF0", range=[0.95, 3.75]),
        yaxis=dict(title="De cada 100 simulaciones, cuántas la detectan",
                   range=[0, 102], gridcolor="#E6EBF0"),
    )
    return fig


# ---------------------------------------------------------------------------
# Página
# ---------------------------------------------------------------------------
geografia = st.session_state.get("geografia", "ocurrencia")

st.title("¿La visibilidad depende de dónde vives o de qué te pasó?")
st.markdown("### De qué te pasó.")
st.markdown(
    "Que un delito llegue a la estadística oficial depende mucho del **tipo de delito** "
    "y casi nada de la **alcaldía**. Esta comparación usa siempre el promedio 2020–2024, "
    "que es donde la encuesta tiene casos suficientes."
)

param = st.radio("Qué comparar", list(PARAMS), format_func=PARAMS.get,
                 horizontal=True, key="param_v2")

# --- Cifras de dispersión ---------------------------------------------------
disp = dispersion().set_index(["param", "particion"])
tip = disp.loc[(param, "tipos")]
sinv = disp.loc[(param, "tipos_sin_vehiculo")]
alc = disp.loc[(param, "alcaldias")]
AYUDA = ("Cuánto se separa típicamente una categoría del nivel común, en puntos "
         "porcentuales, ya descontado el error de la encuesta. Técnicamente: desviación "
         "estándar de la señal entre categorías, de un modelo de efectos aleatorios "
         "estimado por REML, con intervalo por verosimilitud perfil.")

c1, c2, c3 = st.columns(3)
for col, titulo, fila in ((c1, "Diferencia típica entre tipos de delito", tip),
                          (c2, "Diferencia típica entre alcaldías", alc),
                          (c3, "Entre tipos, sin robo de vehículo", sinv)):
    col.metric(titulo, f"{fila['de_pp']:.1f} puntos", help=AYUDA)
    col.caption(f"entre {fila['de_pp_ic_inf']:.1f} y {fila['de_pp_ic_sup']:.1f}")

# Lectura: solo se afirma lo que los intervalos sostienen
if alc["de_pp"] == 0:
    lectura = (f"Entre alcaldías **no se detecta ninguna diferencia**; entre tipos de "
               f"delito, la diferencia típica es de {tip['de_pp']:.1f} puntos.")
else:
    lectura = (f"La diferencia entre tipos de delito es **{tip['de_pp'] / alc['de_pp']:.0f} "
               f"veces** la diferencia entre alcaldías, y **{sinv['de_pp'] / alc['de_pp']:.0f} "
               f"veces** aun quitando el robo de vehículo.")
if tip["de_pp_ic_inf"] > alc["de_pp_ic_sup"]:
    lectura += (" Se sostiene incluso en el caso más desfavorable: el mínimo plausible "
                "entre tipos supera al máximo plausible entre alcaldías.")
else:
    lectura += (" En el caso más desfavorable los dos rangos se tocan, así que aquí la "
                "conclusión descansa en la estimación central.")
st.markdown(lectura)
if geografia == "residencia":
    st.caption("Estas tres cifras están calculadas por alcaldía donde ocurrió el delito. "
               "Las gráficas de abajo sí usan la alcaldía donde vive la víctima.")

# --- Los dos paneles ---------------------------------------------------------
fig, omitidos = figura_dos_paneles(param, geografia)
st.plotly_chart(fig, width="stretch", config={"displayModeBar": False}, key="paneles")
nota = "Cada punto es una estimación; la línea, su rango de 95%. "
if nivel_ciudad(param) is not None:
    nota += "La línea punteada es el nivel de toda la ciudad. "
if omitidos:
    nota += f"Se omiten {omitidos} tipos de delito con muy pocos casos en la encuesta."
st.caption(nota)

# --- Plano d contra k --------------------------------------------------------
st.divider()
st.subheader("Las dos barreras a la vez, alcaldía por alcaldía")
st.markdown(
    "Cada óvalo es la zona donde razonablemente está cada alcaldía, considerando las dos "
    "barreras juntas. Si todos se enciman alrededor del cruce de las líneas punteadas "
    "(el nivel de la ciudad), ninguna alcaldía se distingue del resto."
)
st.plotly_chart(figura_plano(), width="stretch",
                config={"displayModeBar": False}, key="plano")
if geografia == "residencia":
    st.caption("El plano usa la alcaldía donde ocurrió el delito: la región de confianza "
               "conjunta solo se calculó con esa geografía.")

# --- Evidencia de potencia ---------------------------------------------------
st.divider()
with st.expander("¿Y si el método simplemente no podía ver diferencias entre alcaldías?"):
    pot = potencia()
    umbral = pot[(pot["bloque"] == "umbral") & (pot["param"] == param)].set_index("patron")
    sim = pot[(pot["bloque"] == "simulacion") & (pot["param"] == param)
              & (pot["patron"] == "carpetas")]
    # Número de simulaciones, recuperado de p(1−p)/ee² en una fila no degenerada
    nd = sim[(sim["potencia"] > 0) & (sim["potencia"] < 1)].iloc[0]
    n_sim = int(round(nd["potencia"] * (1 - nd["potencia"]) / nd["ee_potencia"] ** 2))

    st.markdown(
        "Para responderlo, se fabricaron datos donde **sí hay** diferencias entre "
        "alcaldías, con el mismo ruido que tiene la encuesta, y se revisó si el método las "
        f"encontraba. Cada punto de la gráfica resume {n_sim} simulaciones."
    )
    cf = umbral.loc["carpetas", "potencia_contrafactual_3p5"]
    if cf == cf:  # no es NaN
        st.markdown(
            "**Si las alcaldías difirieran tanto como difieren sus carpetas (3.5 a 1), "
            f"el método lo habría detectado {cf * 100:.0f} de cada 100 veces.**"
        )
    else:
        tope = sim.sort_values("razon_inyectada").iloc[-1]
        st.markdown(
            "**Aquí no se puede simular una brecha de 3.5 a 1:** con un nivel de ciudad de "
            "66%, la alcaldía más alta tendría que pasar de 100%. Con la brecha más grande "
            f"que sí es posible simular ({tope['razon_inyectada']:.2f} a 1), el método la "
            f"detectó {tope['potencia'] * n_sim:.0f} de {n_sim} veces."
        )
    st.plotly_chart(figura_potencia(param), width="stretch",
                    config={"displayModeBar": False}, key="potencia")
    u = umbral.loc["carpetas"]
    st.markdown(
        f"El método encuentra, 80 de cada 100 veces, brechas de **{u['razon_pot80']:.2f} a 1** "
        f"o más ({u['brecha_pp_pot80']:.1f} puntos entre la alcaldía más alta y la más "
        f"baja). Cuando no hay ninguna diferencia, da una falsa alarma "
        f"{u['tamano_prueba'] * 100:.0f} de cada 100 veces, como debe ser."
    )

    cp = control_positivo()
    cp = cp[(cp["bloque"] == "contraste_vs_resto") & (cp["BPCOD"] == 1)
            & (cp["param"] == "d")].iloc[0]
    st.markdown(
        "**Y cuando una diferencia existe, el método la ve.** El robo total de vehículo, "
        "donde denunciar es requisito para cobrar el seguro, se denuncia "
        f"{cp['tipo_pct']:.1f}% de las veces, contra {cp['resto_pct']:.1f}% del resto de "
        f"los delitos: {cp['dif_pp']:.1f} puntos de diferencia "
        f"(± {1.96 * cp['ee_dif_pp']:.1f})."
    )
    st.caption("Técnicamente: potencia de la prueba de razón de verosimilitudes de "
               "σ²_alcaldía = 0, por simulación con los ψ y la σ²_celda observados.")
