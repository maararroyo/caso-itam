"""Lectura de resultados precalculados. La app NO estima nada: solo lee y formatea."""
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

CARPETA_DATOS = Path(__file__).parent / "datos"

# ---- Etiquetas que ve el usuario -------------------------------------------
PERIODOS = {
    "2020_2024": "Promedio 2020–2024",
    "2020": "2020", "2021": "2021", "2022": "2022", "2023": "2023", "2024": "2024",
}
VARIANTES_C = {
    "C_nucleo": "Delitos comparables (principal)",
    "C_nucleo_alta": "Delitos comparables, solo clasificación segura",
    "C_nucleo_vf": "Comparables + violencia familiar",
    "C_amplio": "Todas las carpetas clasificables",
}
GEOGRAFIAS = {
    "ocurrencia": "Donde ocurrió el delito",
    "residencia": "Donde vive la víctima",
}

# ---- Paleta (una sola fuente de verdad para todas las vistas) --------------
COLOR = {
    "ocurren": "#C9D3DD",     # gris azulado: el universo de delitos
    "denuncia": "#5B8DB8",    # azul medio: lo que llega al MP
    "carpeta": "#173F5F",     # azul profundo: lo que queda en la estadística
    "perdida": "#A23B72",     # magenta: lo que se pierde
    "tenue": "#9AA5B1",       # estimaciones poco precisas
    "tinta": "#1E2A36",
}


def _leer(nombre: str) -> pd.DataFrame:
    ruta = CARPETA_DATOS / nombre
    if nombre.endswith(".parquet"):
        return pd.read_parquet(ruta)
    return pd.read_csv(ruta)


TODOS = "Todos los delitos"

# Abreviaturas de alcaldía (las mismas de las figuras del escrito)
ABREV = {
    "002": "AZC", "003": "COY", "004": "CUJ", "005": "GAM", "006": "IZC",
    "007": "IZP", "008": "MAC", "009": "MIL", "010": "AOB", "011": "TLH",
    "012": "TLP", "013": "XOC", "014": "BJU", "015": "CUH", "016": "MHI",
    "017": "VCA",
}


@st.cache_data
def tipos_delito() -> pd.DataFrame:
    """d, k, R por tipo de delito a nivel ciudad, por año y promedio 2020–2024.

    Si existe embudo_ciudad.parquet (todos los delitos juntos, mismo formato),
    se agrega como un "tipo" más llamado "Todos los delitos".
    """
    df = _leer("R_por_tipo_delito_publicable.parquet")
    if (CARPETA_DATOS / "embudo_ciudad.parquet").exists():
        df = pd.concat([_leer("embudo_ciudad.parquet"), df], ignore_index=True)
    df["periodo"] = df["periodo"].astype(str)
    return df


def nivel_ciudad(param: str, periodo: str = "2020_2024"):
    """Valor de ciudad (todos los delitos) o None si no está el archivo."""
    df = tipos_delito()
    fila = df[(df["tipo"] == TODOS) & (df["periodo"] == periodo) & (df["param"] == param)]
    return None if fila.empty else fila.iloc[0]


@st.cache_data
def estimaciones_alcaldia() -> pd.DataFrame:
    return _leer("estimaciones_finales_benchmark.parquet")


@st.cache_data
def mapa_corregido() -> pd.DataFrame:
    df = _leer("mapa_corregido.parquet")
    df["periodo"] = df["periodo"].astype(str)
    return df


@st.cache_data
def plano_dk() -> pd.DataFrame:
    return _leer("plano_dk_directos_2020_2024.parquet")


@st.cache_data
def dispersion() -> pd.DataFrame:
    return _leer("dispersion_tipos_vs_alcaldias.csv")


@st.cache_data
def potencia() -> pd.DataFrame:
    return _leer("validacion_potencia.csv")


@st.cache_data
def control_positivo() -> pd.DataFrame:
    return _leer("control_positivo_tipos.csv")


@st.cache_data
def maestro() -> pd.DataFrame:
    return _leer("maestro_alcaldia.parquet")


@st.cache_data
def residencia() -> pd.DataFrame:
    df = _leer("robustez_residencia_ruta_adm.csv")
    df["alc"] = df["alc"].astype(str).str.zfill(3)   # 2 -> "002", como en los demás archivos
    return df


@st.cache_data
def razones_tiempo() -> pd.DataFrame:
    df = _leer("tabla_razones_tiempo.csv").rename(columns={"Unnamed: 0": "termino"})
    return df


@st.cache_data
def ranking() -> pd.DataFrame:
    return _leer("tabla_ranking_corregido.csv")


# ---- Formato ---------------------------------------------------------------
def de_cada_100(p: float) -> str:
    """0.0918 -> '9'. Redondeo comercial, no bancario."""
    return f"{int(p * 100 + 0.5)}"


def pct1(p: float) -> str:
    """0.0918 -> '9.2'."""
    return f"{p * 100:.1f}"


def ic_logit(p, ee, z: float = 1.959964):
    """Intervalo al 95% en escala logit, el mismo criterio del cuaderno dia13_14.
    Funciona con escalares o arreglos; devuelve NaN donde p es 0 o 1."""
    p, ee = np.asarray(p, float), np.asarray(ee, float)
    with np.errstate(divide="ignore", invalid="ignore"):
        lg = np.log(p / (1 - p))
        se = ee / (p * (1 - p))
        return 1 / (1 + np.exp(-(lg - z * se))), 1 / (1 + np.exp(-(lg + z * se)))


def intervalo(inf: float, sup: float) -> str:
    """Intervalo en 'de cada 100', con un decimal."""
    return f"{inf * 100:.1f} a {sup * 100:.1f}"

