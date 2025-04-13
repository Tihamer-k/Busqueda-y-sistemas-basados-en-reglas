# Búsqueda y sistemas basados en reglas 
## 🚏 Sistema Experto para Rutas de TransMilenio

📎 Versión: `1.0.5`

Este es un sistema experto desarrollado en Python utilizando Tkinter para la interfaz gráfica.
Permite a los usuarios:

- Buscar estaciones de TransMilenio y encontrar la mejor ruta entre una estación de origen y una de destino.
- Obtener coordenadas y ubicación en Google Maps.
- Predecir la troncal a la que pertenece una ubicación usando aprendizaje automático con scikit-learn.
- Agrupar estaciones según su ubicación mediante aprendizaje no supervisado con KMeans.

Los datos de las estaciones se obtienen en tiempo real desde la API pública de TransMilenio.

## ✨ Características

- 💅 Interfaz gráfica intuitiva con Tkinter.
- 🔍 Búsqueda predictiva en los combobox para seleccionar estaciones.
- 📌 Expansión automática del combobox con coincidencias mientras se escribe.
- 🚳️ Cálculo de rutas utilizando `networkx`.
- 🧠 Predicción de troncales con `scikit-learn`.
- 🤖 Agrupamiento de estaciones con KMeans.
- 🌐 Enlace directo a la estación en Google Maps.
- 🌍 Obtención de datos en tiempo real desde la API de TransMilenio.

## 📦 Requisitos

Antes de ejecutar el programa, asegúrate de tener instaladas las dependencias necesarias. Puedes instalarlas con el siguiente comando:

```bash
  pip install -r requirements.txt
```

## 🚀 Instalación y ejecución

1. 📅 Clona este repositorio o descarga los archivos.
2. 🐍 Asegúrate de tener Python >=3.9 instalado.
3. 📦 Instala las dependencias con `pip install -r requirements.txt`.
4. 🛠️ Crea un archivo `.env` en la raíz del proyecto y define la variable `API_TRANSMILENIO` con la URL de la API pública de TransMilenio.
   ```text
   API_TRANSMILENIO=https://gis.transmilenio.gov.co/arcgis/rest/services/Troncal/consulta_estaciones_troncales/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson
   ```
5. ▶️ Ejecuta la aplicación con: `python main.py`
6. 💅 La interfaz gráfica se abrirá y podrás comenzar a usar la aplicación.

## 🛠️ Uso

1. 🔄 Abre la aplicación.
2. 📍 En la pestaña "Rutas entre estaciones":
   - Selecciona una estación de origen y una de destino.
   - El sistema te mostrará la mejor ruta y la distancia total.
3. 💡 En la pestaña "Predicción de Troncal (ML)":
   - Ingresa una latitud y longitud.
   - Obtendrás la troncal predicha según tu ubicación geográfica.
   - También puedes ver el árbol de decisión utilizado para la predicción.
4. 🌐 En la pestaña "Ubicación en Google Maps":
   - Selecciona una estación para abrir su ubicación en Google Maps.
5. 🔍 En la función de Agrupamiento (KMeans):
   - Se ejecuta `modelo_unsupervisado.py` para visualizar los clústeres espaciales de estaciones.
   - El resultado se guarda como imagen en la carpeta `resources/`.

## 📂 Estructura del Proyecto

```
Proyecto/
│── resources/                      # 📂 Recursos del proyecto
│   └── modelo_troncal.pkl          # 🎯 Modelo de predicción guardado
│   └── label_encoder_troncal.pkl   # 🧾 Codificador de etiquetas de troncal
│   └── estaciones_transmilenio.csv # 📊 Exportación del dataset procesado
│   └── arbol_decision.png          # 🌳 Visualización del árbol de decisión
│   └── agrupamiento_kmeans.png     # 📌 Visualización de clustering KMeans
│   └── estaciones_clusterizadas.csv# 📊 Dataset con clúster asignado
│── src/
│   │── gui/                        # 🎨 Código de la interfaz gráfica con Tkinter
│   │   │── app.py                  # 💅 Inicializa la aplicación de rutas y predicción
│   │   │── autocombo.py            # 🔍 Combobox con búsqueda predictiva
│   │── logic/                      # 🧠 Lógica de cálculo de rutas y procesamiento de datos
│   │   │── data.py                 # 📊 Manejo de datos de estaciones y rutas
│   │   │── routing.py              # 🗺️ Cálculo de rutas entre estaciones
│   │   │── modelo_ml.py            # 🤖 Predicción de troncal usando ML
│   │   │── modelo_unsupervisado.py # 🔎 Clustering con KMeans
│   └── version.py                  # 📜 Versión del proyecto
│── main.py                         # 📌 Archivo principal que inicia la aplicación
│── LICENSE                         # 📜 Licencia del proyecto
│── requirements.txt                # 📋 Lista de dependencias
└── README.md                       # 📖 Documentación del proyecto
```

## 🌍 API utilizada

Se utiliza la API pública de TransMilenio para obtener la lista de estaciones en tiempo real: [🔗 API TransMilenio](https://datosabiertos-transmilenio.hub.arcgis.com/datasets/Transmilenio::estaciones-troncales-de-transmilenio/about)

## 🤝 Contribuciones

Si deseas contribuir al proyecto, puedes realizar un fork, realizar mejoras y enviar un pull request.

## 📜 Licencia

Este proyecto está bajo la licencia MIT.
