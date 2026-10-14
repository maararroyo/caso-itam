"""
sae_utils.py — Funciones de estimación en áreas pequeñas (días 9 y 10)
======================================================================

Extraídas sin cambios de lógica del cuaderno `dia09_10_seleccion_eblup.ipynb`
(celdas 4, 9, 15, 17, 25 y 27), para que los cuadernos siguientes las reusen
sin re-ejecutar la selección ni los 63 ajustes.

Contenido
---------
construir_base      Une directos de ocurrencia con las covariables (celda 4).
matriz_X            Constante + efectos de año + covariables (celda 17).
sigma2u_momentos    Estimador de momentos de Prasad-Rao (celda 9).
_componentes_reml   Score, información y log-verosimilitud restringida (celda 15).
estimar_s2u         Scoring de Fisher, REML o REML ajustada de Li-Lahiri (celda 15).
ajustar_fh          Fay-Herriot completo: σ²_u, β, EBLUP y ECM de Prasad-Rao (celda 15).
ajustar_con_regla   REML, salvo frontera; entonces, ajustada (celda 27).
p_desde_theta       Regreso a proporción con corrección de sesgo (celda 25).

Si algo aquí se modifica, los resultados de los días 9 y 10 dejan de ser
reproducibles con este módulo. Las extensiones (Rao-Yu, efectos de alcaldía)
van en funciones nuevas, no en estas.
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm

# ----------------------------------------------------------------------------
# Covariables (celda 4)
# ----------------------------------------------------------------------------
COV_FIJAS = ["z_prop_fem_18", "z_prop_ocupada_12", "z_log_densidad",
             "z_eje_socio_1", "z_eje_socio_2", "z_agencias_mp_100k",
             "z_dist_mp_km"]                       # censo 2020: no cambian
COV_TIEMPO = ["z_sesnsp_nucleo", "z_prop_7d_std", "z_prop_digital_robo"]
CANDIDATAS = COV_FIJAS + COV_TIEMPO

# Especificaciones congeladas el día 10 (celda 13)
ESPECIFICACIONES = {
    ("d", "principal"):    ["z_sesnsp_nucleo", "z_prop_7d_std", "z_prop_digital_robo"],
    ("k", "principal"):    [],
    ("k", "sens_acceso"):  ["z_log_densidad", "z_dist_mp_km"],
    ("R", "principal"):    ["z_prop_digital_robo"],
    ("R", "sens_sesnsp"):  ["z_sesnsp_nucleo", "z_prop_7d_std", "z_prop_digital_robo"],
}


def construir_base(directos, maestro, cov_fgj, geografia="ocurrencia"):
    """Base de análisis: una fila por (alcaldía, año, parámetro) con θ, ψ y
    las 10 covariables candidatas en escala z. Réplica de la celda 4."""
    fgj = cov_fgj[["cve_mun", "anio_ref", "prop_7d_std", "prop_digital_robo"]].copy()
    for v in ["prop_7d_std", "prop_digital_robo"]:
        fgj["z_" + v] = (fgj[v] - fgj[v].mean()) / fgj[v].std(ddof=1)

    covs = (maestro[["cve_mun", "anio_ref", "nombre"] + COV_FIJAS + ["z_sesnsp_nucleo"]]
            .merge(fgj, on=["cve_mun", "anio_ref"], how="inner", validate="1:1"))
    assert len(covs) == 80, "La unión de covariables no dio 80 filas"

    base = (directos.query("geografia == @geografia")
            .merge(covs.drop(columns="nombre"), left_on=["alc", "anio_ref"],
                   right_on=["cve_mun", "anio_ref"], how="left", validate="m:1"))
    assert len(base) == 240 and base[CANDIDATAS].notna().all().all()
    return base, covs


# ----------------------------------------------------------------------------
# Matriz de diseño (celda 17)
# ----------------------------------------------------------------------------
def matriz_X(df, covariables, efectos_anio=True):
    partes = [df[covariables]]
    if efectos_anio:
        partes.insert(0, pd.get_dummies(df["anio_ref"], prefix="a",
                                        drop_first=True, dtype=float))
    return sm.add_constant(pd.concat(partes, axis=1),
                           has_constant="add").to_numpy(float)


# ----------------------------------------------------------------------------
# Estimador de momentos de Prasad-Rao (celda 9)
#   E[SSE] = (n − p)·σ²_u + Σ ψ_d (1 − h_dd)
# ----------------------------------------------------------------------------
def sigma2u_momentos(y, X, psi):
    X = np.asarray(X, dtype=float)
    n, p = X.shape
    Q, _ = np.linalg.qr(X)                   # X = QR; la matriz sombrero es QQ'
    h = (Q ** 2).sum(axis=1)                 # diagonal de la matriz sombrero
    resid = y - Q @ (Q.T @ y)
    return (resid @ resid - np.sum(psi * (1 - h))) / (n - p)


# ----------------------------------------------------------------------------
# Fay-Herriot por REML (celda 15)
# ----------------------------------------------------------------------------
def _componentes_reml(s2, y, X, psi):
    """Score, información de Fisher y log-verosimilitud restringida en σ²_u = s2."""
    v = s2 + psi                                  # varianza total de cada celda
    Xv = X / v[:, None]                           # V⁻¹X (V es diagonal)
    A = np.linalg.inv(X.T @ Xv)                   # (X'V⁻¹X)⁻¹
    P = np.diag(1 / v) - Xv @ A @ Xv.T            # proyecta fuera de las columnas de X
    Py = P @ y
    score = -0.5 * np.trace(P) + 0.5 * Py @ Py    # derivada de ℓ_REML
    info = 0.5 * np.sum(P * P)                    # ½ tr(PP), información esperada
    _, logdet_xvx = np.linalg.slogdet(X.T @ Xv)   # el término que hace "restringida"
    loglik = -0.5 * (np.log(v).sum() + logdet_xvx + y @ Py)
    return score, info, loglik


def estimar_s2u(y, X, psi, metodo="reml", tol=1e-10, max_iter=200):
    """Scoring de Fisher. metodo: 'reml' o 'ajustada' (Li-Lahiri: + log σ²_u).
    Devuelve (σ²_u, iteraciones, frontera)."""
    if metodo == "reml":
        score0, _, _ = _componentes_reml(0.0, y, X, psi)
        if score0 <= 0:          # la verosimilitud ya baja desde cero:
            return 0.0, 0, True  # el máximo está en la frontera
    s2 = np.median(psi)          # valor inicial, el mismo que usa eblupFH
    for it in range(1, max_iter + 1):
        score, info, _ = _componentes_reml(s2, y, X, psi)
        if metodo == "ajustada":             # derivadas del término log σ²_u
            score += 1 / s2
            info += 1 / s2 ** 2
        paso = score / info
        while s2 + paso <= 0:                # nunca salir del dominio σ²_u > 0
            paso /= 2
        if abs(paso) < tol:
            return s2 + paso, it, False
        s2 += paso
    print("  AVISO: el scoring de Fisher no convergió")
    return s2, max_iter, False


def ajustar_fh(df, covariables, efectos_anio=True, metodo="reml"):
    """Ajusta un Fay-Herriot sobre las filas de df. Las celdas sin directo
    (theta nulo) reciben la predicción sintética."""
    df = df.reset_index(drop=True)
    X_todas = matriz_X(df, covariables, efectos_anio)
    obs = df["theta"].notna().to_numpy()
    theta = df["theta"].to_numpy()
    psi_todas = df["var_theta_asen"].to_numpy()
    y, psi, X = theta[obs], psi_todas[obs], X_todas[obs]

    # 1. Varianza del efecto aleatorio
    s2, iters, frontera = estimar_s2u(y, X, psi, metodo)

    # 2. β por mínimos cuadrados generalizados y predicción sintética x'β
    v = s2 + psi
    Xv = X / v[:, None]
    A = np.linalg.inv(X.T @ Xv)
    beta = A @ (Xv.T @ y)
    sintetico = X_todas @ beta

    # 3. EBLUP: combinación convexa con γ = σ²_u / (σ²_u + ψ)
    gamma = np.where(obs, s2 / (s2 + psi_todas), 0.0)
    eblup = np.where(obs, gamma * np.nan_to_num(theta) + (1 - gamma) * sintetico,
                     sintetico)

    # 4. ECM: g1 + g2 + 2·g3 (REML); celdas sin directo: σ²_u + x'Ax
    xAx = np.einsum("ij,jk,ik->i", X_todas, A, X_todas)
    var_s2 = 2 / np.sum(1 / v ** 2)                     # varianza asintótica de σ̂²_u
    with np.errstate(invalid="ignore"):
        g1 = gamma * psi_todas
        g2 = (1 - gamma) ** 2 * xAx
        g3 = psi_todas ** 2 / (s2 + psi_todas) ** 3 * var_s2
    ecm = np.where(obs, g1 + g2 + 2 * g3, s2 + xAx)

    salida = df[["alc", "nombre", "anio_ref", "param", "tipo_celda"]].assign(
        theta_dir=theta, psi=psi_todas, sintetico=sintetico, gamma=gamma,
        theta_eblup=eblup, ecm_theta=ecm)
    info = {"s2u": s2, "iteraciones": iters, "frontera": frontera,
            "beta": beta, "n": int(obs.sum()), "p": X.shape[1]}
    return salida, info


def ajustar_con_regla(df, covs, efectos_anio=True):
    """REML; si cae en la frontera, REML ajustada (celda 27)."""
    res, info = ajustar_fh(df, covs, efectos_anio, "reml")
    frontera = info["frontera"]
    if frontera:
        res, info = ajustar_fh(df, covs, efectos_anio, "ajustada")
    return res, info, frontera


# ----------------------------------------------------------------------------
# Regreso a proporción (celda 25)
# ----------------------------------------------------------------------------
def p_desde_theta(theta, var):
    """Media de sin²(T) con T ~ N(theta, var).
    sin²x = (1 − cos 2x)/2  y  E[cos 2T] = cos(2θ)·exp(−2·var)."""
    return 0.5 - 0.5 * np.cos(2 * theta) * np.exp(-2 * var)
