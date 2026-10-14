# Del delito a la carpeta de investigacion: una estimacion por alcaldia de la Ciudad de Mexico

## Pregunta de investigacion

¿Que fraccion de los delitos que ocurren en cada alcaldia de la Ciudad de Mexico llega a convertirse en una carpeta de investigacion, y por que varia esa fraccion entre alcaldias?

## Resumen

Este proyecto analiza la diferencia entre la incidencia delictiva estimada mediante encuestas de victimizacion y los delitos que llegan a registrarse formalmente en carpetas de investigacion.

Se descompone el proceso en tres probabilidades:

- **d**: probabilidad de que un delito sea denunciado.
- **k**: probabilidad de que una denuncia genere una carpeta de investigacion.
- **R**: probabilidad de que un delito llegue a convertirse en una carpeta de investigacion.

Por definicion, R = d * k para las probabilidades poblacionales correspondientes.

La investigacion compara las 16 alcaldias de la Ciudad de Mexico durante 2020-2024, usando cinco ediciones de ENVIPE y registros administrativos de la FGJ.

## Principales hallazgos

En terminos aproximados, por cada 100 delitos:

- 11 llegan a denunciarse.
- De cada 100 denuncias, 66 generan una carpeta.
- Alrededor de 7 de cada 100 delitos se convierten en carpeta de investigacion.

Aunque las tasas registradas de carpetas presentan diferencias importantes entre alcaldias, el analisis no encuentra evidencia estadistica suficiente para afirmar que R difiere territorialmente.

Las diferencias en los registros oficiales no deben interpretarse automaticamente como diferencias en la propension a denunciar o abrir carpetas.

## Metodologia

1. Integracion y armonizacion de cinco ediciones de ENVIPE.
2. Vinculacion territorial con registros de la FGJ y fuentes demograficas.
3. Estimacion directa de d, k y R con ponderadores de encuesta.
4. Analisis de rezago entre ocurrencia del delito e inicio de carpeta.
5. Estimacion en areas pequenas mediante modelos Fay-Herriot.
6. Comparacion con modelos Rao-Yu y calibracion de estimaciones.
7. Validacion estadistica, analisis de robustez y comparacion territorial.

## Estructura del repositorio

- `notebooks/`: desarrollo metodologico en orden de ejecucion.
- `src/`: funciones reutilizables.
- `datos/`: documentacion y archivos procesados seleccionados.
- `resultados/`: estimaciones, tablas y figuras.
- `app/`: aplicacion interactiva.
- `escrito/`: documento de investigacion.
- `presentacion/`: materiales de presentacion.

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

Abrir los notebooks desde la raiz del repositorio.

La ejecucion integral requiere descargar los archivos crudos indicados en `datos/README.md`.

## Estado de reproducibilidad

Los notebooks pasaron una auditoria estatica de sintaxis y se registraron las dependencias utilizadas. La ejecucion integral del pipeline desde un entorno limpio todavia no ha sido validada.

Los archivos de microdatos no se incluyen en el repositorio publico.

## Fuentes

- INEGI: Encuesta Nacional de Victimizacion y Percepcion sobre Seguridad Publica (ENVIPE).
- Fiscalia General de Justicia de la Ciudad de Mexico: carpetas de investigacion.
- INEGI: Censo de Poblacion y Vivienda 2020, Marco Geoestadistico y ENSU.
- CONAPO: proyecciones de poblacion.
- SESNSP: incidencia delictiva del fuero comun.

## Limitaciones

Los resultados dependen de la precision muestral de ENVIPE, la correspondencia entre clasificaciones delictivas, las diferencias entre lugar de residencia y ocurrencia, y los rezagos de registro administrativo.

La ausencia de diferencias estadisticamente detectables entre alcaldias no demuestra igualdad exacta.
