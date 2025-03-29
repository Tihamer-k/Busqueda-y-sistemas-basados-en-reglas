# Búsqueda y sistemas basados en reglas 
## 🚏 Sistema Experto para Rutas de TransMilenio

Este es un sistema experto desarrollado en Python utilizando Tkinter para la interfaz gráfica.
Permite a los usuarios buscar estaciones de TransMilenio y encontrar la mejor ruta entre una estación de origen y una de destino.
La información de las estaciones se obtiene en tiempo real desde la API pública de TransMilenio.

## ✨ Características

- 🖥️ Interfaz gráfica intuitiva con Tkinter.
- 🔍 Búsqueda predictiva en los combobox para seleccionar origen y destino.
- 📌 Expansión automática del combobox con coincidencias mientras se escribe.
- 🛣️ Cálculo de la mejor ruta utilizando `networkx`.
- 🌐 Obtención de datos en tiempo real desde la API de TransMilenio.

## 📦 Requisitos

Antes de ejecutar el programa, asegúrate de tener instaladas las dependencias necesarias. Puedes instalarlas con el siguiente comando:

```bash
  pip install -r requirements.txt
```

## 🚀 Instalación y ejecución

1. 📥 Clona este repositorio o descarga los archivos.
2. 🐍 Asegúrate de tener Python >=3.9 instalado.
3. 📦 Instala las dependencias con `pip install -r requirements.txt`.
4. ▶️ Ejecuta la aplicación con: `python main.py`
5. 🖥️ La interfaz gráfica se abrirá y podrás comenzar a usar la aplicación.

## 🛠️ Uso

1. 🔄 Abre la aplicación.
2. 📍 Selecciona una estación de origen y una de destino en los combobox.
3. 🚏 La aplicación mostrará la mejor ruta entre ambas estaciones.
4. ⚙️ Puedes modificar los valores y recalcular la ruta en cualquier momento.

## 📂 Estructura del Proyecto

```
Proyecto/
│── src/
│   │── gui/                # 🎨 Código de la interfaz gráfica con Tkinter
│   │   │── app.py          # 🖥️ Inicializa la aplicación de rutas.
│   │   │── autocombo.py    # 🔍 Combobox con búsqueda predictiva
│   │── logic/              # 🧠 Lógica de cálculo de rutas y procesamiento de datos
│   │   │── data.py         # 📊 Manejo de datos de estaciones y rutas
│   │   │── routing.py      # 🗺️ Cálculo de la mejor ruta entre estaciones
│   │── utils/              # 🔧 Funciones auxiliares
|   |   │── distance.py     # 📏 Cálculo de distancias entre estaciones
│   └── version.py          # 📜 Versión del proyecto
│── LICENSE                 # 📜 Licencia del proyecto
|── main.py                 # 📌 Archivo principal que inicia la aplicación
│── README.md               # 📖 Documentación del proyecto
│── requirements.txt        # 📋 Lista de dependencias
└── 
```

## 🌍 API utilizada

Se utiliza la API pública de TransMilenio para obtener la lista de estaciones en tiempo real: [🔗 API TransMilenio](https://datosabiertos-transmilenio.hub.arcgis.com/datasets/Transmilenio::estaciones-troncales-de-transmilenio/about)

## 🤝 Contribuciones

Si deseas contribuir al proyecto, puedes realizar un fork, realizar mejoras y enviar un pull request.

## 📜 Licencia

Este proyecto está bajo la licencia MIT.

