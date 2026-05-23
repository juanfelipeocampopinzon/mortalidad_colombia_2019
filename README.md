# Laboratorio Final: Análisis de la Mortalidad en Colombia 2019

## 8.1 Introducción del proyecto
Esta es una aplicación web interactiva desarrollada en Python y Streamlit con el objetivo de analizar e interpretar los datos de mortalidad no fetal en Colombia para el año 2019. Se basa en los datos y archivos oficiales proporcionados por el DANE (Estadísticas Vitales - EEVV). Mediante visualizaciones gráficas interactivas, la plataforma permite realizar cruces de información y facilitar la comprensión de las tendencias demográficas y las causas de defunción.

## 8.2 Objetivo
El objetivo principal de este proyecto es cargar, transformar y visualizar el conjunto de microdatos de mortalidad colombiana (2019), con el fin de proporcionar un análisis descriptivo robusto que permita a los usuarios interpretar patrones territoriales, de género, etarios y las principales causas de muerte a nivel nacional y municipal.

## 8.3 Estructura del proyecto
La estructura de este repositorio se divide en los siguientes componentes clave:
* `main.py`: Código principal que arranca la aplicación web en Streamlit, procesa los DataFrames y construye las gráficas en Plotly.
* `requirements.txt`: Listado de librerías y dependencias utilizadas en el entorno de Python para garantizar la ejecución.
* `README.md`: Documentación del proyecto (este archivo).
* `datos/`: Carpeta en la cual deben disponerse los archivos en Excel (`NoFetal2019.xlsx`, `CodigosDeMuerte.xlsx`, `Divipola.xlsx`).
* `vistas/`: Carpeta opcional (preparada para futura segmentación de módulos en la interfaz).

## 8.4 Requisitos
Para ejecutar la aplicación localmente, se requieren las siguientes librerías:
```text
streamlit
pandas
plotly
openpyxl
requests
numpy
```
> Puedes instalar todo mediante: `pip install -r requirements.txt`

## 8.5 Despliegue en Azure App Service
La aplicación se despliega en **Azure App Service** garantizando que sea pública y funcional:
1. Desde el portal de Azure se creó un Web App de tipo "Code" utilizando Linux y el entorno de *Python 3.9+*.
2. A través del "Deployment Center" (Centro de Implementación), se vinculó el proyecto apuntando directamente a este repositorio de GitHub.
3. Se configuró el comando de inicio (*Startup Command*) para asegurar que Streamlit escuche en los puertos que requiere Azure:
   `python -m streamlit run main.py --server.port 8000 --server.address 0.0.0.0`
4. Al hacer guardado o realizar un push a la rama `main`, Azure se encarga de instalar las librerías del `requirements.txt` y correr la aplicación.

## 8.6 Software utilizado
El desarrollo del presente laboratorio implicó el uso de las siguientes herramientas:
* **Python**: Lenguaje de programación principal para la lógica y el análisis de datos.
* **Streamlit**: Framework para la construcción de interfaces y desarrollo rápido de la aplicación web.
* **Plotly**: Librería esencial empleada en la generación de todas las gráficas interactivas (Mapas, líneas, barras y pie).
* **Pandas**: Para la estructuración, limpieza, filtrado y transformación de los DataFrames de Excel.
* **Visual Studio Code**: IDE utilizado para la escritura del código fuente.
* **GitHub**: Plataforma de control de versiones para gestionar el repositorio.
* **Azure App Service**: Proveedor Cloud para el despliegue de la solución web.

## 8.7 Visualizaciones e interpretación de resultados
Dentro de la aplicación (URL desplegada) encontrarás las siguientes visualizaciones clave:

* **Mapa de Distribución Total de Muertes por Departamento:** Empleando un mapa coroplético que combina la división política de Colombia en formato GeoJSON, se visualizan los niveles de mortalidad, destacándose oscuramente los departamentos más poblados (como Antioquia y Bogotá) que en su mayoría concentran el mayor número de fallecimientos.
* **Variación a lo largo del año (Líneas):** Este gráfico facilita la identificación de fluctuaciones. Suele evidenciarse si hubo algún pico de mortalidad asociado a eventos puntuales o épocas festivas hacia finales del año.
* **Muertes por sexo en cada departamento (Barras Apiladas):** Permite ver en un solo cuadro tanto la mortalidad por departamento como la segmentación entre géneros, ayudando a determinar variaciones atípicas donde, por lo general, prevalecen más fallecimientos masculinos.
* **Ciudades más violentas (Homicidios):** Mediante un filtro hacia el código `X95` y similares, se aísla la variable de violencia armada. Aquí se evidencia qué municipios requieren mayor atención en materia de seguridad ciudadana.
* **10 Ciudades con menor índice de mortalidad:** Este gráfico en forma circular detalla los municipios que aportaron menos casos a la base de datos nacional, caracterizándose usualmente por ser territorios con densidad poblacional muy baja.
* **Distribución de muertes por grupo de edad:** Un histograma configurado por las 11 categorías de edades. Evidencia claramente cómo las enfermedades y procesos naturales elevan significativamente los reportes durante la adultez intermedia, vejez y longevidad, en contraste con otros ciclos vitales.
* **Top 10 Causas de Muerte (Tabla):** Ordena de mayor a menor aquellos diagnósticos críticos causales (por ejemplo infarto agudo, hipertensión, agresiones o neumonía), permitiendo que un tomador de decisiones pueda enfocar su política de salud pública de acuerdo a las amenazas más letales.
