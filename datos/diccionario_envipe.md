# Diccionario de variables — ENVIPE (microdatos)

Proyecto: visibilidad del delito por alcaldía de la CDMX (d, k, R).
Estado: **Día 2 cerrado.** Los cinco levantamientos (2021–2025) están verificados contra el archivo, el descriptor y las cifras publicadas por el INEGI. Geografía decidida: **ocurrencia** (principal) y residencia (robustez), ver §6.

Convención: "verificado" = confirmado en el CSV, no solo en el descriptor.
Cuando el descriptor y el archivo no coinciden, manda el archivo y se anota la discrepancia.

---

## 1. Archivos y lectura

| Concepto | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|
| Formato | .csv | .csv | .csv | .csv | .csv |
| Codificación | latin-1 (TMod_Vic es ASCII, compatible) | latin-1 (igual) | igual | igual | igual |
| Columna índice sin nombre (exportación de R) | Sí → `index_col=0` | Sí | Sí | Sí | Sí |
| Lectura | `dtype=str` siempre (preserva ceros: `"09"`, `"002"`) | igual | igual | igual | igual |

## 2. Tablas, nivel y llave (2021)

| Tabla | Nivel | Llave | Registros | Variables |
|---|---|---|---|---|
| TVivienda | vivienda | UPM + VIV_SEL | 90,335 | 20 |
| THogar | hogar | UPM + VIV_SEL + HOGAR | 92,143 | 18 |
| TSDem | integrante del hogar | UPM + VIV_SEL + HOGAR + N_REN | 318,419 | 26 |
| TPer_Vic1 | persona seleccionada (18+) | UPM + VIV_SEL + HOGAR + R_SEL | 92,051 | 180 |
| TPer_Vic2 | persona seleccionada (18+) | UPM + VIV_SEL + HOGAR + R_SEL | 92,051 | 149 |
| **TMod_Vic** | **incidente** | UPM + VIV_SEL + HOGAR + R_SEL + BPCOD + ND_TIPO | 37,156 | 129 |

- Cero llaves duplicadas o vacías en las seis tablas.
- 92 hogares de THogar no pasan a las tablas de persona: `RESUL_H` = C o D (entrevista incompleta).
- `RESUL_H = A` ("Entrevista completa con victimización"): 21,871 personas = exactamente las personas con al menos un incidente en TMod_Vic.
- `ID_DEL` = `ID_PER` + "." + `BPCOD` + "." + `ND_TIPO` (verificado en todas las filas).
- **TMod_Vic no trae municipio de residencia.** Se obtiene de TPer_Vic2 uniendo por UPM + VIV_SEL + HOGAR + R_SEL (`validate="many_to_one"`).

## 3. Variables sustantivas

| Rol | Variable | Tabla | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|
| Tipo de delito | `BPCOD` | TMod_Vic | 01–15 (ver §5) | igual | igual | igual | igual |
| Nº de incidente dentro del tipo | `ND_TIPO` | TMod_Vic | 1–5 | igual | igual | igual | igual |
| Total de incidentes del tipo (topado) | `TD_TIPO` | TMod_Vic | 1–5 ⚠️ | 1–5 ⚠️ (descriptor sigue diciendo 1–9) | igual | igual | igual |
| Veces que ocurrió (hogar) | `AP6_6_01` … `AP6_6_04` | TPer_Vic2 | ✔ | igual | igual | igual | igual |
| Veces que ocurrió (persona) | `AP7_4_05` … `AP7_4_15` | TPer_Vic2 | ✔ | igual | igual | igual | igual |
| **Denuncia de la víctima** (1.20) | `BP1_20` | TMod_Vic | 1 Sí, 2 No; sin vacíos | igual | igual | igual | igual |
| Denuncia de otro integrante (1.21) | `BP1_21` | TMod_Vic | 1, 2, 9; solo delitos 01–04 y solo si BP1_20 = 2 ⚠️ | igual | igual | igual | igual |
| ¿Conoció todo el proceso? (1.22) | `BP1_22` | TMod_Vic | 1, 2; solo si denunció otro integrante | igual | igual | igual | igual |
| **Razón de no denuncia** (1.23) | `BP1_23` | TMod_Vic | 01–09, 99 | igual | igual | igual | igual |
| **Inicio de carpeta** (1.24) | `BP1_24` | TMod_Vic | 1 Sí, 2 No, 9 NS/NR | igual | igual | igual | igual |
| Qué pasó con la carpeta (1.25) | `BP1_25` | TMod_Vic | 1–9; descriptor: 7 = Nada, 8 = Otra | ⚠️ **6 = Nada, 7 = Otra** (confirmar 2021 en datos) | 6 = Nada, 7 = Otra | 6 = Nada, 7 = Otra | 6 = Nada, 7 = Otra |
| Razón de no inicio de carpeta (1.26) | `BP1_26` | TMod_Vic | descriptor dice `BP1_26_1` ⚠️ | `BP1_26` (descriptor ya corregido) | igual | igual | igual |
| **Entidad de ocurrencia** (1.2) | `BP1_2C` | TMod_Vic | 01–32; 99 = no especificada | igual | igual | igual | igual |
| **Municipio de ocurrencia** (1.3) | `BP1_3C` | TMod_Vic | 001–570; 999 = no especificado | igual | igual | igual | igual |
| Área metropolitana | `AREAM_OCU` | TMod_Vic | 01 = Ciudad de México; no examinada a fondo | igual | igual | igual | igual |

`BP1_23` (razones de no denuncia), 2021: 01 Miedo al agresor · 02 Miedo a extorsión · 03 Delito de poca importancia · 04 Pérdida de tiempo · 05 Trámites largos y difíciles · 06 Desconfianza en la autoridad · 07 No tenía pruebas · 08 Actitud hostil de la autoridad · 09 Otra · 99 NS/NR. Vacía en 3,962 incidentes = 3,828 (denunció la víctima) + 134 (denunció otro integrante).

## 4. Geografía de residencia y diseño muestral

| Rol | Variable | Tabla | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|
| Entidad de residencia | `CVE_ENT`, `NOM_ENT` | TPer_Vic2 | CDMX = `"09"` | igual | igual | igual | igual |
| Municipio de residencia | `CVE_MUN`, `NOM_MUN` | TPer_Vic2 | 16 alcaldías, `"002"`–`"017"` | igual | igual | igual | igual |
| **Estrato de diseño** | `EST_DIS` | TPer_Vic2, TMod_Vic | ✔ | igual | igual | igual | igual |
| **UPM de diseño** | `UPM_DIS` | TPer_Vic2, TMod_Vic | ✔ | igual | igual | igual | igual |
| ⚠️ NO es el estrato muestral | `ESTRATO` | | nivel socioeconómico | igual | igual | igual | igual |
| Factor de vivienda | `FAC_VIV` | | ✔ | igual | igual | igual | igual |
| Factor de hogar | `FAC_HOG` | TPer_Vic2 | ✔ | igual | igual | igual | igual |
| Factor de persona elegida | `FAC_ELE` | TPer_Vic2 | ✔ | igual | igual | igual | igual |
| **Factor de incidente** | **`FAC_DEL`** | TMod_Vic | ✔ | igual | igual | igual | igual |
| Factores de área metropolitana | `FAC_VIV_AM`, `FAC_HOG_AM`, `FAC_ELE_AM`, `FAC_DEL_AM` | | no se usan (33 AM, no alcaldías) | igual | igual | igual | igual |

Diseño 2021: 13,195 UPM en la muestra (10,332 con algún incidente). Ninguna UPM en más de un estrato, ningún estrato cruza entidades, ningún estrato con una sola UPM. `EST_DIS` y `UPM_DIS` son únicos a nivel nacional.

Diseño 2022: 13,092 UPM; mismos chequeos, todos en cero.

Alcaldías 2021 (personas seleccionadas): 002 Azcapotzalco 258 · 003 Coyoacán 491 · 004 Cuajimalpa de Morelos 161 · 005 Gustavo A. Madero 751 · 006 Iztacalco 282 · 007 Iztapalapa 873 · 008 La Magdalena Contreras 216 · **009 Milpa Alta 94** · 010 Álvaro Obregón 420 · 011 Tláhuac 203 · 012 Tlalpan 448 · 013 Xochimilco 246 · 014 Benito Juárez 372 · 015 Cuauhtémoc 412 · 016 Miguel Hidalgo 263 · 017 Venustiano Carranza 341. Total CDMX: 5,831.

Alcaldías 2022 (personas seleccionadas): 002 Azcapotzalco 293 · 003 Coyoacán 401 · 004 Cuajimalpa de Morelos 200 · 005 Gustavo A. Madero 610 · 006 Iztacalco 338 · 007 Iztapalapa 845 · 008 La Magdalena Contreras 200 · **009 Milpa Alta 60** · 010 Álvaro Obregón 345 · 011 Tláhuac 313 · 012 Tlalpan 375 · 013 Xochimilco 369 · 014 Benito Juárez 375 · 015 Cuauhtémoc 408 · 016 Miguel Hidalgo 282 · 017 Venustiano Carranza 406.

## 5. Catálogo BPCOD (2021)

| Código | Delito | Víctima | Incidentes (muestra) |
|---|---|---|---|
| 01 | Robo total de vehículo | hogar | 997 |
| 02 | Robo de accesorios/autopartes | hogar | 5,769 |
| 03 | Vandalismo (pinta, grafiti, rayones) | hogar | 4,515 — **excluido** |
| 04 | Robo a casa habitación | hogar | 4,552 |
| 05 | Robo/asalto en calle o transporte | persona | 4,554 |
| 06 | Otro tipo de robo | persona | 1,535 |
| 07 | Fraude bancario | persona | 3,106 |
| 08 | Fraude al consumidor | persona | 2,257 |
| 09 | Extorsión | persona | 4,446 |
| 10 | Amenazas verbales | persona | 2,814 |
| 11 | Lesiones | persona | 949 |
| 12 | Secuestro | persona | 63 |
| 13 | Hostigamiento/abuso sexual | persona | 1,381 |
| 14 | Violación sexual | persona | 95 |
| 15 | Otros delitos | persona | 123 |

### Estructura 2022

| Tabla | Registros | Variables | Cambio vs 2021 |
|---|---|---|---|
| TVivienda | 90,467 | 20 | — |
| THogar | 92,220 | 18 | — |
| TSDem | 312,144 | 26 | — |
| TPer_Vic1 | 92,103 | 181 | +1: `AP5_7_4` (percepción; no se usa) |
| TPer_Vic2 | 92,103 | 149 | — |
| TMod_Vic | 36,144 | 129 | mismas variables |

Llaves sin duplicados ni vacíos. `RESUL_H = A`: 21,783 = personas con incidente. Catálogo `BPCOD` 01–15 idéntico. `BP1_21` solo en delitos 01–04 (igual que 2021). El texto de las preguntas cambia de "Ministerio Público" a "Ministerio Público o Fiscalía Estatal", sin cambio de códigos en 1.20, 1.21 y 1.24. Nombres de archivo: confirmar en la carpeta local (en la carga aparecieron como `TPer_Vic1_1.csv`, etc.).

`FAC_DEL` 2022 = misma fórmula (dif. rel. máx. 0.41%; 405 incidentes con más de 5 veces; 30.03 M vs 29.59 M sin corrección).

### Estructura 2023–2025 (salida de `verificar_estructura` + revisión de descriptores)

| Chequeo | 2023 | 2024 | 2025 |
|---|---|---|---|
| Incidentes en TMod_Vic | 35,135 | 37,614 | 40,280 |
| Sin persona / sin "veces" / llave duplicada | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| TD_TIPO = mín(veces, 5); máximo | ✔; 5 | ✔; 5 | ✔; 5 |
| FAC_DEL vs fórmula (dif. rel. máx.) | 0.34% | 0.29% | 0.41% |
| Catálogo BPCOD | 01–15 | 01–15 | 01–15 |
| BP1_21 fuera de delitos del hogar | 0 | 0 | 0 |
| Valores BP1_20 / BP1_24 | 1,2 / 1,2,9 | 1,2 / 1,2,9 | 1,2 / 1,2,9 |
| Alcaldías CDMX | 16 (002–017) | 16 (002–017) | 16 (002–017) |
| Variables de TMod_Vic en el descriptor (vs 2022) | iguales | iguales | +5: `BP1_5A_1`…`BP1_5A_9` |

Revisión de descriptores 2023–2025: los códigos de `BPCOD`, `BP1_20`, `BP1_21`, `BP1_22`, `BP1_23`, `BP1_24`, `BP1_25`, `BP1_2C` y `BP1_3C` son los mismos que en 2022. Cambios solo de redacción:
- 2024–2025: lenguaje incluyente ("Lo (la) secuestraron", "agresor(a)", "Algún(a) otro(a) integrante").
- 2024–2025: la entidad 15 se rotula "México" en lugar de "Estado de México" (mismo código).
- **2025: la pregunta 1.24 cambia de "¿Inició el MP o Fiscalía Estatal una carpeta de investigación?" a "¿El MP o Fiscalía Estatal abrió una carpeta de investigación?"** Mismos códigos; anotarlo como cambio de redacción en el estimando k.
- **2025: nueva pregunta 1.5a** (`BP1_5A_*`): si el delito se realizó por internet o medios electrónicos. No afecta d ni k; posible covariable o estratificador (fraude, extorsión).


**⚠️ Cambio en las regiones de la CDMX a partir de la ENVIPE 2023:** Cuauhtémoc (015) pasa de la región Poniente a la Norte. 2023: Norte = 005, 006, 015, 017; Sur = 003, 008, 012, 014; Oriente = 007, 009, 011, 013; Poniente = 002, 004, 010, 016. Usar la definición de cada año al validar contra el cuadro 9.7.

**Cifras INEGI 2023 (delitos de 2022)**, presentaciones "Prevalencia e incidencia delictiva" y "Denuncia del delito": delitos 26.8 M; d nacional 10.9%; k nacional 69.3%; cifra negra nacional 92.4%; cifra negra CDMX 92.6%; tasa de delitos CDMX 46 032.

**Cifras INEGI 2024 (delitos de 2023)**, presentación "Principales resultados": delitos 31.3 M (diap. 19); d nacional 10.4% y k nacional 68.0% (diap. 52); cifra negra nacional 92.9% (diap. 52–53); cifra negra CDMX 93.0% (diap. 54); tasa de delitos CDMX 52 723 (diap. 22). Regiones de la CDMX con la definición de 2023 (Cuauhtémoc en Norte).

**Cifras INEGI 2025 (delitos de 2024)**, presentación "Principales resultados" (nuevo formato, 43 págs.): delitos 33.5 M, d nacional 9.6%, cifra negra nacional 93.2% (pág. 23); k nacional 70.5% (pág. 24); tasa de delitos CDMX 54 473 (pág. 13). **El INEGI renombra "cifra negra" como "cifra oculta"** (misma definición). La presentación 2025 no publica la cifra negra por entidad: para la CDMX hace falta el tabulado 3.1 o 3.3.

## 6. Decisiones metodológicas

**Factor de incidente = `FAC_DEL`.** Verificado empíricamente (2021):

FAC_DEL = factor_base × máx(1, veces / 5),  con factor_base = FAC_HOG (BPCOD 01–04) o FAC_ELE (BPCOD 05–15).

Coincide con el oficial en los 37,156 incidentes (diferencia relativa máx. 0.4%, por redondeo). Corrige el tope de 5 incidentes por tipo (afecta a 335 incidentes; +0.27 M delitos a nivel nacional). Supuesto: los incidentes sin detalle se comportan como los 5 captados.

**Definiciones a nivel incidente:**
- `denuncio` = (BP1_20 == 1) o (BP1_21 == 1)
- `carpeta` = denuncio y (BP1_24 == 1). NS/NR y vacíos cuentan como sin carpeta (convención de la cifra negra del INEGI). 98 incidentes con denuncia de otro integrante tienen BP1_24 vacío: son exactamente los casos con BP1_22 = 2 (la víctima no conoció el proceso).
- d = Σw·denuncio / Σw · k = Σw·carpeta / Σw·denuncio · R = Σw·carpeta / Σw

**Universo: se excluye el vandalismo (BPCOD 03).** Con esa exclusión se reproducen los totales nacionales del INEGI (ver §7). Es necesario para el benchmarking del día 12.

**Geografía (DECISIÓN TOMADA): ocurrencia como estimación principal, residencia como prueba de robustez.** Registrada también en `Envipe_2021_a_2025.ipynb` (celdas 5 y 6).

| | Principal: ocurrencia | Robustez: residencia |
|---|---|---|
| Entidad | `BP1_2C == "09"` (TMod_Vic) | `CVE_ENT == "09"` (TPer_Vic2) |
| Alcaldía | `BP1_3C` (`"002"`–`"017"`) | `CVE_MUN` (`"002"`–`"017"`) |
| Excluidos | `BP1_3C == "999"` (alcaldía no especificada) | ninguno |
| Pregunta que responde | ¿Qué fracción de los delitos ocurridos en la alcaldía llega a carpeta? | ¿Qué fracción de los delitos que sufren sus habitantes llega a carpeta? |

Justificación:
1. **Consistencia con el numerador.** Las carpetas (SESNSP, Fiscalía CDMX) se registran por lugar del hecho; el mapa corregido exige que R esté en la misma geografía.
2. **Consistencia con el INEGI.** La cifra negra y la tasa de delitos por entidad (2021–2025) y las regiones de la CDMX (cuadro 9.7) se publican por ocurrencia; se reproducen exactamente con esta definición (§7, §7bis).
3. **Interpretación de k.** Por ocurrencia, k refleja la respuesta del MP ante los delitos de ese territorio; por residencia mezcla agencias de distintas alcaldías.
4. **Aportación frente a la literatura.** Buil-Gil, Medina y Shlomo (2021) estiman por residencia ("area victimization rates") y señalan como limitación (4) que esto complica la comparación con registros policiales; sugieren seleccionar los delitos ocurridos en el área local. Su prueba de robustez (solo delitos en el área local) da ρ de Spearman = 0.91 (LAD) y 0.88 (MSOA). Aquí se invierte el orden: ocurrencia como principal, residencia como robustez, reportando la correlación de rangos entre ambas.

Costos que deben declararse en la metodología:
- **Errores de muestreo correlacionados entre alcaldías.** Por ocurrencia, una UPM puede aportar incidentes a varias alcaldías (2022: 278 de 1,123 UPM). El Fay-Herriot estándar supone errores independientes entre áreas; cuantificar la fracción de varianza que proviene de UPM compartidas y declararlo como limitación acotada.
- **Covariables del Censo describen residentes**, no a la población flotante (relevante en Cuauhtémoc, Benito Juárez, Miguel Hidalgo).
- **Incidentes con alcaldía no especificada (`999`)**: se excluyen de las alcaldías, pero cuentan en el total de la CDMX. Reportar su peso cada año.
- **Víctimas no residentes**: el dominio de ocurrencia incluye incidentes de residentes de otras entidades (2022: 210 de 3,029 incidentes CDMX sin vandalismo), captados por su propia muestra y factor.

Alcaldías de ocurrencia por año (`BP1_2C == "09"`, todas las categorías de delito):

| Año | Alcaldías válidas | Incidentes con `BP1_3C = 999` |
|---|---|---|
| 2021 | 16 (002–017) | 71 |
| 2022 | 16 (002–017) | 59 |
| 2023 | 16 (002–017) | 59 |
| 2024 | 16 (002–017) | 79 |
| 2025 | 16 (002–017) | 90 |

Ejemplo de la diferencia entre definiciones (2022, sin vandalismo, sin ponderar): Cuauhtémoc pasa de 246 incidentes / 33 denuncias por residencia a 360 / 50 por ocurrencia; Milpa Alta de 48 / 8 a 37 / 7. En ambas definiciones, varias alcaldías tienen menos de 15 denuncias en un año: k no es estimable de forma directa con un solo levantamiento (justificación del Rao-Yu).

**Varianza:** linealización de Taylor, estratos `EST_DIS`, conglomerados `UPM_DIS`, estimación por dominio (sin filtrar la base) e incluyendo las UPM sin incidentes con z = 0. Validada contra `samplics` (archivado; no usar en el proyecto).

## 7. Verificación piloto (2021, sin vandalismo, FAC_DEL)

| Dominio | Parámetro | Estimación | EE | CV | IC 90% |
|---|---|---|---|---|---|
| Nacional | d | 10.07% | 0.30 | 3.0% | 9.57–10.57 |
| Nacional | k | 66.86% | 1.25 | 1.9% | 64.81–68.91 |
| Nacional | R | 6.73% | 0.24 | 3.5% | 6.34–7.12 |
| CDMX | d | 11.85% | 0.78 | 6.6% | 10.57–13.12 |
| CDMX | k | 67.82% | 2.88 | 4.2% | 63.09–72.55 |
| CDMX | R | 8.03% | 0.66 | 8.2% | 6.95–9.12 |

Total nacional de delitos: 27.64 M. Cifra negra nacional: 93.27%.

**Verificación contra INEGI, "ENVIPE 2021. Principales resultados" (presentación, septiembre 2021):**

| Cifra | INEGI | Reproducido | Diapositiva |
|---|---|---|---|
| Delitos 2020, nacional | 27.6 M | 27.64 M | 17 |
| % denunciado, nacional | 10.1% | 10.07% | 40 |
| % con carpeta entre denunciados, nacional | 66.9% | 66.86% | 40 |
| % con carpeta del total, nacional | 6.7% | 6.73% | 40 |
| Cifra negra, nacional | 93.3% | 93.27% | 40–41 |
| Cifra negra, CDMX | 92.6% | **92.60% (por ocurrencia)**; 91.97% por residencia | 42 |
| Tasa de delitos por 100 mil hab., CDMX | 53 334 | **53 334 (por ocurrencia)** | 15 |

- [x] Nacional verificado.
- [x] CDMX verificado: **el INEGI publica las cifras por entidad según el lugar de OCURRENCIA** (`BP1_2C`), no de residencia. Numerador por ocurrencia; denominador de la tasa = población de 18+ residente (Σ FAC_ELE de residentes CDMX = 7,345,443).
- [x] Precisión verificada contra INEGI, Tabulados básicos ENVIPE 2021, cuadro 3.1 (estimaciones, CV e IC al 90%), CDMX por ocurrencia:

| CDMX (ocurrencia) | INEGI | Reproducido |
|---|---|---|
| Delitos ocurridos | 3,917,649 | 3.92 M |
| **d (denunciados)** | **11.20%**, CV 6.78%, IC90 9.95–12.45 | **11.20%**, CV 6.78%, IC90 9.95–12.45 |
| k (carpeta entre denunciados) | 66.07%, CV 4.73%, IC90 60.94–71.21 | 66.07%, CV 4.72%, IC90 60.94–71.21 |

- [x] Subentidad verificada contra el cuadro 9.7 (cifra negra por región de la CDMX). Las regiones se arman por **alcaldía de ocurrencia** (`BP1_3C`) y se reproducen exactamente:

| Región (alcaldías) | Delitos INEGI | Reproducido | Cifra negra INEGI | Reproducida |
|---|---|---|---|---|
| Norte (005, 006, 017) | 583,665 | 583,665 | 91.52% | 91.52% |
| Sur (003, 008, 012, 014) | 882,961 | 882,961 | 93.09% | 93.09% |
| Oriente (007, 009, 011, 013) | 1,236,809 | 1,236,809 | 91.83% | 91.83% |
| Poniente (002, 004, 010, 015, 016) | 1,135,589 | 1,135,589 | 93.23% | 93.23% |

78,625 delitos ocurridos en la CDMX tienen alcaldía no especificada (`BP1_3C = 999`), 2.0% del total: cuentan para la entidad y para ninguna región.

**Número verificado del día: tasa de denuncia de la CDMX 2021 (delitos de 2020) = 11.20%** (IC 90%: 9.95–12.45), igual a la publicada.

CDMX por ocurrencia (sin vandalismo): 3,512 incidentes, 3.92 M delitos, d = 11.20%, k = 66.07%, R = 7.40%. Incluye delitos de víctimas que residen fuera de la CDMX.

### Verificación piloto 2022 (delitos de 2021, sin vandalismo, FAC_DEL)

| Cifra | INEGI ("ENVIPE 2022. Principales resultados") | Reproducido |
|---|---|---|
| Delitos, nacional | 28.1 M (diap. 17) | 28.12 M |
| % denunciado, nacional | 10.1% (diap. 40) | 10.09% |
| % con carpeta entre denunciados | 67.3% (diap. 40) | 67.29% |
| % con carpeta del total | 6.8% (diap. 40) | 6.79% |
| Cifra negra, nacional | 93.2% (diap. 40) | 93.21% |
| Cifra negra, CDMX (ocurrencia) | 92.2% (diap. 42) | 92.20% |
| Tasa de delitos CDMX por 100 mil | 45 336 (diap. 15) | 45 336 |

CDMX 2022 por ocurrencia: **d = 11.83%** (CV 7.06%, IC90 10.45–13.20); k = 65.92% (CV 5.29%, IC90 60.18–71.66). Pendiente: confirmar d contra el cuadro 3.1 de los tabulados 2022.

Regiones 2022 (ocurrencia; cifra negra): Norte 91.37% · Sur 89.14% · Oriente 92.27% · Poniente 94.59%. Pendiente: comparar con el cuadro 9.7 de 2022. Alcaldía no especificada: 63,779 delitos.

## 7bis. Verificación piloto 2021–2025 (cuaderno `Envipe_2021_a_2025.ipynb`)

Sin vandalismo, FAC_DEL, CDMX por ocurrencia. ENVIPE = cálculo propio; INEGI = cifra publicada.

| Cifra | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|
| Delitos nacional (M) | 27.64 / 27.6 | 28.12 / 28.1 | 26.83 / 26.8 | 31.28 / 31.3 | 33.45 / 33.5 |
| d nacional (%) | 10.07 / 10.1 | 10.09 / 10.1 | 10.90 / 10.9 | 10.42 / 10.4 | 9.58 / 9.6 |
| k nacional (%) | 66.86 / 66.9 | 67.29 / 67.3 | 69.30 / 69.3 | 67.99 / 68.0 | 70.51 / 70.5 |
| Cifra negra nacional (%) | 93.27 / 93.3 | 93.21 / 93.2 | 92.44 / 92.4 | 92.91 / 92.9 | 93.25 / 93.2 |
| Cifra negra CDMX (%) | 92.60 / 92.6 | 92.20 / 92.2 | 92.56 / 92.6 | 93.01 / 93.0 | 93.17 / — |
| Tasa delitos CDMX | 53 334 / 53 334 | 45 336 / 45 336 | 46 032 / 46 032 | 52 723 / 52 723 | 54 473 / 54 473 |
| **d CDMX (%)** | **11.20** / 11.20 | **11.83** / — | **11.09** / — | **10.81** / — | **9.97** / — |
| d CDMX: CV (%) | 6.78 / 6.78 | 7.06 | 7.02 | 7.50 | 9.28 |
| k CDMX (%) | 66.07 / 66.07 | 65.92 | 67.05 | 64.64 | 68.46 |
| k CDMX: CV (%) | 4.72 / 4.73 | 5.29 | 4.72 | 5.41 | 6.42 |

Todas las cifras publicadas se reproducen al redondeo. Pendiente opcional: tabulados 3.1 de 2022–2025 para confirmar d y k de la CDMX (y la cifra negra CDMX 2025).

## 8. Discrepancias descriptor vs. archivo (2021)

1. `TD_TIPO`: el descriptor dice 1–9; el archivo solo trae 1–5 (tope del módulo).
2. Razón de no inicio de carpeta: el descriptor la llama `BP1_26_1`; en el CSV es `BP1_26`.
3. Codificación: no se documenta; cinco de las seis tablas vienen en latin-1.

2022: persiste la discrepancia de `TD_TIPO` (descriptor 1–9, archivo 1–5). El descriptor ya llama `BP1_26` a la 1.26. Los códigos de `BP1_25` cambian respecto al descriptor 2021.

## 9. Qué revisar en cada año nuevo

- Formato (.csv/.dbf) y codificación.
- Que existan `BP1_20`, `BP1_21`, `BP1_24`, `BP1_23`, `BP1_2C`, `BP1_3C`, `FAC_DEL`, `EST_DIS`, `UPM_DIS` con los mismos códigos.
- Catálogo `BPCOD`: mismos 15 delitos y mismos códigos.
- Tope de `TD_TIPO` y que la fórmula de `FAC_DEL` siga reproduciéndose.
- Salto de `BP1_21` (solo hogar, solo si BP1_20 = 2).
- Que las 16 alcaldías aparezcan con clave `"002"`–`"017"`.
- Que el piloto nacional reproduzca el boletín de ese año, y la CDMX **por ocurrencia**.
- Que `BP1_3C` (con `BP1_2C = 09`) traiga las 16 alcaldías y contar los `999`.
