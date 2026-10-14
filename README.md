# Del delito a la carpeta de investigacion: una estimación por alcaldía de la Ciudad de Mexico

## Pregunta de investigación

¿Que fracción de los delitos que ocurren en cada alcaldía de la Ciudad de México llega a convertirse en una carpeta de investigación, y por qué varía esa fracción entre alcaldías?

## Resumen

Este proyecto analiza la diferencia entre la incidencia delictiva estimada mediante encuestas de victimización y los delitos que llegan a registrarse formalmente en carpetas de investigación.

Se descompone el proceso en tres probabilidades:

- **d**: probabilidad de que un delito sea denunciado.
- **k**: probabilidad de que una denuncia genere una carpeta de investigación.
- **R**: probabilidad de que un delito llegue a convertirse en una carpeta de investigación.

Por definición, R = d * k para las probabilidades poblacionales correspondientes.

La investigación compara las 16 alcaldías de la Ciudad de México durante 2020-2024, usando cinco ediciones de ENVIPE y registros administrativos de la FGJ.

## Principales hallazgos

En términos aproximados, por cada 100 delitos:

- 11 llegan a denunciarse.
- De cada 100 denuncias, 66 generan una carpeta.
- Alrededor de 7 de cada 100 delitos se convierten en carpeta de investigación.

Aunque las tasas registradas de carpetas presentan diferencias importantes entre alcaldías, el análisis no encuentra evidencia estadística suficiente para afirmar que R difiere territorialmente.

Las diferencias en los registros oficiales no deben interpretarse automáticamente como diferencias en la propensión a denunciar o abrir carpetas.

## Metodología

1. Integración y armonización de cinco ediciones de ENVIPE.
2. Vinculacion territorial con registros de la FGJ y fuentes demográficas.
3. Estimación directa de d, k y R con ponderadores de encuesta.
4. Análisis de rezago entre ocurrencia del delito e inicio de carpeta.
5. Estimación en áreas pequeñas mediante modelos Fay-Herriot.
6. Comparación con modelos Rao-Yu y calibración de estimaciones.
7. Validación estadística, análisis de robustez y comparación territorial.

## Estructura del repositorio

- `notebooks/`: desarrollo metodológico en orden de ejecución.
- `src/`: funciones reutilizables.
- `datos/`: documentación y archivos procesados seleccionados.
- `resultados/`: estimaciones, tablas y figuras.
- `app/`: aplicación interactiva.
- `escrito/`: documento de investigación.
- `presentacion/`: materiales de presentación.

## Notebooks

1. `01_preparacion_envipe.ipynb`
2. `02_integracion_territorial.ipynb`
3. `03_estimacion_directa.ipynb`
4. `04_modelo_supervivencia.ipynb`
5. `05_estimacion_areas_pequenas.ipynb`
6. `06_comparacion_modelos.ipynb`
7. `07_validacion_resultados.ipynb`

## Instalacion

Se recomienda Miniconda y Python 3.12.

```bash
conda env create -f environment.yml
conda activate caso
```

Abrir los notebooks desde la raíz del repositorio.

La ejecución integral requiere descargar los archivos crudos indicados en `datos/README.md`.

## Estado de reproducibilidad

Los notebooks pasaron una auditoría estática de sintaxis y se registraron las dependencias utilizadas. La ejecución integral del pipeline desde un entorno limpio todavía no ha sido validada.

Los archivos de microdatos no se incluyen en el repositorio público.

## Fuentes

- INEGI: Encuesta Nacional de Victimización y Percepción sobre Seguridad Pública (ENVIPE).
- Fiscalía General de Justicia de la Ciudad de México: carpetas de investigación.
- INEGI: Censo de Población y Vivienda 2020, Marco Geoestadístico y ENSU.
- CONAPO: proyecciones de población.
- SESNSP: incidencia delictiva del fuero común.

## Limitaciones

Los resultados dependen de la precisión muestral de ENVIPE, la correspondencia entre clasificaciones delictivas, las diferencias entre lugar de residencia y ocurrencia, y los rezagos de registro administrativo.

La ausencia de diferencias estadísticamente detectables entre alcaldías no demuestra igualdad exacta.
