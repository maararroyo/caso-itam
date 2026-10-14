# Datos y reproduccion

Los microdatos y archivos originales descargados de fuentes oficiales NO se publican en este repositorio.

## Fuentes requeridas

| Fuente | Contenido | Uso |
|---|---|---|
| INEGI ENVIPE 2021-2025 | Tablas CSV de victimizacion | Incidentes, denuncias y carpetas reportadas |
| FGJ CDMX | Carpetas de investigacion, corte enero 2025 | Registros administrativos y rezagos |
| INEGI ITER 2020 | Censo a nivel localidad/municipio | Covariables y denominadores |
| CONAPO | Proyecciones de poblacion | Poblacion por alcaldia y anio |
| SESNSP | Incidencia municipal | Covariables administrativas |
| Marco Geoestadistico | Shapefiles CDMX | Vinculacion y variables espaciales |
| INEGI AGEB | Datos censales AGEB | Covariables territoriales |
| Agencias del MP | Ubicaciones de agencias | Medidas de accesibilidad |
| INEGI ENSU | Encuesta urbana | Validacion complementaria |

## Estructura local

Los datos descargados se organizan en `datos/crudos/`, conservando la estructura esperada por los notebooks.

Los datos transformados se guardan en `datos/procesados/`.

## Precaucion

Los notebooks de preparacion requieren archivos originales que no estan incluidos en GitHub.

El repositorio contiene resultados procesados seleccionados para facilitar el examen del trabajo.

## Pendiente de documentacion

Antes de declarar el proyecto plenamente reproducible deben incorporarse:

- URL oficiales exactas de descarga.
- Nombre y version de cada archivo utilizado.
- Instrucciones especificas de colocacion por fuente.
- Verificacion de ejecucion completa desde un entorno limpio.
