"""Vista 1 — El embudo de la visibilidad (portada)."""
import plotly.graph_objects as go
import streamlit as st

from datos import COLOR, PERIODOS, TODOS, de_cada_100, intervalo, tipos_delito

COMPARACION_INICIAL = "Robo total de vehículo"


# ---------------------------------------------------------------------------
def valores(df, tipo: str, periodo: str) -> dict:
    """{'d': {...}, 'k': {...}, 'R': {...}} para un tipo y periodo."""
    filas = df[(df["tipo"] == tipo) & (df["periodo"] == periodo)].set_index("param")
    salida = {}
    for p in ("d", "k", "R"):
        f = filas.loc[p]
        salida[p] = {
            "est": f["est"], "inf": f["ic95_inf"], "sup": f["ic95_sup"],
            "ok": bool(f["publicable"]) and f["est"] == f["est"],  # NaN != NaN
        }
    return salida


def barrera_dominante(v: dict) -> str:
    """Compara las dos tasas de paso; solo afirma algo si los intervalos no se tocan."""
    d, k = v["d"], v["k"]
    if d["sup"] < k["inf"]:
        return "ciudadana"
    if k["sup"] < d["inf"]:
        return "institucional"
    return "indistinguible"


def figura_embudo(v: dict) -> go.Figure:
    etapas = ["Ocurren", "Se denuncian", "Llegan a carpeta"]
    est = [100, v["d"]["est"] * 100, v["R"]["est"] * 100]
    inf = [100, v["d"]["inf"] * 100, v["R"]["inf"] * 100]
    sup = [100, v["d"]["sup"] * 100, v["R"]["sup"] * 100]
    colores = [COLOR["ocurren"], COLOR["denuncia"], COLOR["carpeta"]]

    fig = go.Figure()
    # "Ocurren" va en su propia traza: es el 100 de referencia y no tiene incertidumbre
    fig.add_bar(y=etapas[:1], x=est[:1], orientation="h", marker_color=colores[0],
                width=0.62, hoverinfo="skip")
    fig.add_bar(
        y=etapas[1:], x=est[1:], orientation="h",
        marker_color=colores[1:], width=0.62,
        error_x=dict(
            type="data", symmetric=False,
            array=[s - e for s, e in zip(sup[1:], est[1:])],
            arrayminus=[e - i for e, i in zip(est[1:], inf[1:])],
            color=COLOR["tinta"], thickness=1.5, width=6,
        ),
        hoverinfo="skip",
    )
    # Etiqueta a la derecha del bigote, para que nunca lo tape
    for i, (e, lo, hi) in enumerate(zip(est, inf, sup)):
        texto = "<b>100</b>" if i == 0 else f"<b>{e:.1f}</b>  <span style='color:#5f6b77'>({lo:.1f} a {hi:.1f})</span>"
        fig.add_annotation(
            x=min(hi, 100) + 2 if i else 101, y=etapas[i], text=texto,
            showarrow=False, xanchor="left", font=dict(size=14, color=COLOR["tinta"]),
        )
    fig.update_layout(
        height=260, margin=dict(l=0, r=10, t=10, b=30),
        xaxis=dict(range=[0, 135], tickvals=[0, 25, 50, 75, 100],
                   title="de cada 100 delitos", gridcolor="#E6EBF0", zeroline=False),
        yaxis=dict(autorange="reversed", tickfont=dict(size=14),
                   categoryorder="array", categoryarray=etapas),
        plot_bgcolor="white", paper_bgcolor="white", showlegend=False,
        bargap=0.25,
    )
    return fig


def bloque_tipo(df, tipo: str, periodo: str, clave: str):
    """Embudo + lectura de pérdidas para un tipo de delito."""
    v = valores(df, tipo, periodo)

    if any(v[p]["est"] != v[p]["est"] for p in ("d", "k", "R")):  # algún NaN
        st.markdown(f"#### {tipo}")
        st.warning("La encuesta no tiene suficientes casos de este delito en el periodo "
                   "elegido para estimar el embudo. Prueba con el promedio 2020–2024.")
        return v

    st.markdown(
        f"#### De cada 100, **{de_cada_100(v['d']['est'])}** se denuncian "
        f"y **{de_cada_100(v['R']['est'])}** quedan registrados"
    )
    st.plotly_chart(figura_embudo(v), width="stretch",
                    config={"displayModeBar": False}, key=f"embudo_{clave}")

    no_d = {"est": 1 - v["d"]["est"], "inf": 1 - v["d"]["sup"], "sup": 1 - v["d"]["inf"]}
    no_k = {"est": 1 - v["k"]["est"], "inf": 1 - v["k"]["sup"], "sup": 1 - v["k"]["inf"]}
    c1, c2 = st.columns(2)
    c1.markdown(
        f"<span style='color:{COLOR['perdida']}'>**Barrera ciudadana**</span><br>"
        f"De cada 100 delitos, **{de_cada_100(no_d['est'])} no se denuncian**<br>"
        f"<small>entre {intervalo(no_d['inf'], no_d['sup'])}</small>",
        unsafe_allow_html=True,
    )
    c2.markdown(
        f"<span style='color:{COLOR['perdida']}'>**Barrera institucional**</span><br>"
        f"De cada 100 denuncias, **{de_cada_100(no_k['est'])} no llegan a carpeta**<br>"
        f"<small>entre {intervalo(no_k['inf'], no_k['sup'])}</small>",
        unsafe_allow_html=True,
    )

    barrera = barrera_dominante(v)
    if barrera == "ciudadana":
        st.info("**Dónde se pierde más:** antes de llegar al ministerio público. "
                "La mayoría de las víctimas no denuncia.")
    elif barrera == "institucional":
        st.info("**Dónde se pierde más:** dentro del ministerio público. "
                "Las víctimas denuncian, pero la denuncia no se convierte en carpeta.")
    else:
        st.info("**Dónde se pierde más:** con estos datos no se puede distinguir cuál "
                "de las dos barreras pesa más.")

    if not all(v[p]["ok"] for p in ("d", "k", "R")):
        st.warning("Hay pocos casos en la encuesta para este delito en el periodo elegido: "
                   "las cifras son poco precisas. Los rangos entre paréntesis muestran cuánto.")
    return v


def veces(r: float) -> str:
    return f"{r:.1f}" if r < 3 else f"{r:.0f}"


# ---------------------------------------------------------------------------
df = tipos_delito()
periodo = st.session_state.get("periodo", "2020_2024")
# "Todos los delitos" va primero; el resto en orden alfabético
tipos = sorted(t for t in df["tipo"].unique() if t != TODOS)
if TODOS in set(df["tipo"]):
    tipos = [TODOS] + tipos
TIPO_INICIAL = tipos[0] if tipos[0] == TODOS else "Robo o asalto en calle o transporte"

st.title("¿Cuántos delitos llegan a la estadística oficial?")
st.markdown(
    "Cada delito pasa por dos filtros antes de aparecer en el mapa oficial: "
    "**la víctima decide si denuncia**, y **el ministerio público decide si abre una carpeta**. "
    f"Periodo: **{PERIODOS[periodo]}**."
)

col_a, col_b = st.columns(2, gap="large")
with col_a:
    tipo_a = st.selectbox("Tipo de delito", tipos, index=tipos.index(TIPO_INICIAL), key="tipo_a")
    v_a = bloque_tipo(df, tipo_a, periodo, "a")
with col_b:
    tipo_b = st.selectbox("Comparar con", tipos, index=tipos.index(COMPARACION_INICIAL), key="tipo_b")
    v_b = bloque_tipo(df, tipo_b, periodo, "b")

# Frase de cierre: cuántas veces más visible es uno que otro
if tipo_a != tipo_b and v_a["R"]["ok"] and v_b["R"]["ok"] and v_a["d"]["ok"] and v_b["d"]["ok"]:
    mayor, menor = (tipo_a, tipo_b) if v_a["R"]["est"] >= v_b["R"]["est"] else (tipo_b, tipo_a)
    r_may = max(v_a["R"]["est"], v_b["R"]["est"])
    r_men = min(v_a["R"]["est"], v_b["R"]["est"])
    # Solo se afirma la diferencia si los intervalos no se traslapan
    sin_traslape = (v_a["R"]["inf"] > v_b["R"]["sup"]) or (v_b["R"]["inf"] > v_a["R"]["sup"])
    st.divider()

    def nombre(t: str) -> str:
        return "un delito cualquiera" if t == TODOS else f"uno de *{t.lower()}*"

    if sin_traslape:
        sujeto = "Un delito cualquiera" if mayor == TODOS else f"Un caso de *{mayor.lower()}*"
        st.markdown(
            f"### {sujeto} tiene **{veces(r_may / r_men)} veces** más "
            f"probabilidad de quedar registrado que {nombre(menor)}."
        )
    else:
        st.markdown("### Con estos datos, los dos delitos no se distinguen en cuánto quedan registrados.")
