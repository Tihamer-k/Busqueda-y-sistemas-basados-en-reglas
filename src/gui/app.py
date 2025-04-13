import os
import tkinter as tk
import webbrowser
from tkinter import ttk, messagebox

import joblib
from PIL import ImageTk, Image
from dotenv import load_dotenv

from src.gui.autocombo import AutocompleteCombobox
from src.logic.data import cargar_estaciones_api
from src.logic.modelo_ml import predecir_troncal_por_coords, exportar_estaciones_csv
from src.logic.modelo_unsupervisado import realizar_agrupamiento_kmeans
from src.logic.routing import (
    construir_grafo_estaciones,
    buscar_mejor_ruta_estaciones,
    buscar_ruta_alternativa
)


def validate_lat_lon(self, lat, lon):
    # Validar si las coordenadas están dentro de las estaciones cargadas desde la API
    return any(est["latitud"] == lat and est["lon"] == lon for est in self.estaciones)



class RouteApp:
    """
    Aplicación para buscar rutas en el sistema de transporte Transmilenio.

    Atributos:
        root (tk.Tk): La ventana principal de la aplicación.
        estaciones (list): Lista de estaciones cargadas desde la API.
        grafo (networkx.Graph): Grafo de estaciones.
        lista_estaciones (list): Lista de nombres de estaciones.
        origen_cb (AutocompleteCombobox): Combobox para seleccionar la estación de origen.
        destino_cb (AutocompleteCombobox): Combobox para seleccionar la estación de destino.
        buscar_btn (ttk.Button): Botón para buscar la ruta.
        resultado_text (tk.Text): Área de texto para mostrar los resultados de la búsqueda.
    """
    def __init__(self, root):
        """
        Inicializa la aplicación de rutas.

        Parámetros:
            root (tk.Tk): La ventana principal de la aplicación.
        """
        self.root = root
        self.root.title("Sistema Experto de Rutas Transmilenio")
        self.root.geometry("760x600")

        # Configuración de tema
        style = ttk.Style()
        style.configure('TFrame', background='lightblue')
        style.configure('TLabel', background='lightblue', font=('Arial', 10))
        style.configure('TButton', background='lightblue', font=('Arial', 10))
        style.configure('TText', background='white', font=('Arial', 10))
        style.map('TButton', background=[('active', 'lightgreen')])
        style.map('TButton', foreground=[('active', 'green')])
        style.map('TText', background=[('active', 'lightyellow')])
        style.map('TText', foreground=[('active', 'black')])
        style.map('TCombobox', background=[('active', 'lightyellow')])
        style.map('TCombobox', foreground=[('active', 'black')])
        style.map('TCombobox', fieldbackground=[('active', 'lightyellow')])
        style.map('TCombobox', selectbackground=[('active', 'lightyellow')])
        style.map('TCombobox', selectforeground=[('active', 'black')])
        style.map('TCombobox', arrowcolor=[('active', 'black')])

        # Configuración de la ventana
        self.root.configure(bg='lightblue')
        self.root.resizable(False, False)

        # Cargar datos desde la API
        try:
            load_dotenv()  # Carga desde .env

            API_URL = os.getenv("API_TRANSMILENIO")

            if not API_URL:
                raise ValueError("No se encontró la variable API_TRANSMILENIO en el archivo .env")

            self.estaciones = cargar_estaciones_api(API_URL)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar las estaciones:\n{e}")
            self.root.destroy()
            return

        self.grafo = construir_grafo_estaciones(self.estaciones, umbral_km=1.0)
        self.lista_estaciones = sorted([est["nombre"] for est in self.estaciones])

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.tab_rutas = ttk.Frame(self.notebook)
        self.tab_prediccion = ttk.Frame(self.notebook)
        self.tab_mapa = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_rutas, text="Rutas entre estaciones")
        self.notebook.add(self.tab_prediccion, text="Predicción de Troncal (ML)")
        self.notebook.add(self.tab_mapa, text="Ubicación en Google Maps")

        self.init_tab_rutas()
        self.init_tab_prediccion()
        self.init_tab_mapa()

    def init_tab_rutas(self):
        frame = ttk.Frame(self.tab_rutas, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Sección: Selección de estaciones
        ttk.Label(frame, text="🔄 Selección de estaciones:").grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        ttk.Label(frame, text="Selecciona la estación de origen y destino para calcular la mejor ruta.").grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        ttk.Label(frame, text="Estación de Origen: ").grid(row=2, column=0, sticky=tk.W)
        self.origen_cb = AutocompleteCombobox(frame, width=50)
        self.origen_cb.set_completion_list(self.lista_estaciones)
        self.origen_cb.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Estación de Destino: ").grid(row=3, column=0, sticky=tk.W)
        self.destino_cb = AutocompleteCombobox(frame, width=50)
        self.destino_cb.set_completion_list(self.lista_estaciones)
        self.destino_cb.grid(row=3, column=1, padx=5, pady=5)

        # Divider
        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(row=4, column=0, columnspan=2, sticky=tk.EW, pady=10)

        # Sección: Búsqueda de ruta
        ttk.Label(frame, text="🔍 Búsqueda de ruta:").grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        ttk.Label(frame, text="Haz clic en el botón para buscar la mejor ruta entre las estaciones seleccionadas.").grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        self.buscar_btn = ttk.Button(frame, text="Buscar Ruta", command=self.calcular_ruta)
        self.buscar_btn.grid(row=7, column=0, columnspan=2, pady=10)

        # Divider
        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(row=8, column=0, columnspan=2, sticky=tk.EW, pady=10)

        # Sección: Resultados
        ttk.Label(frame, text="📋 Resultados:").grid(row=9, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))

        self.resultado_text = tk.Text(frame, wrap=tk.WORD, width=90, height=10)
        self.resultado_text.grid(row=11, column=0, columnspan=2, pady=10)

    def init_tab_prediccion(self):
        frame = ttk.Frame(self.tab_prediccion, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Sección: Entrada de coordenadas
        ttk.Label(frame, text="🔢 Entrada de Coordenadas:").grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        ttk.Label(frame, text="Ingresa la latitud y longitud para predecir la troncal correspondiente.").grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        ttk.Label(frame, text="Latitud:").grid(row=2, column=0, sticky=tk.W)
        self.lat_entry = ttk.Entry(frame, width=30)
        self.lat_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Longitud:").grid(row=3, column=0, sticky=tk.W)
        self.lon_entry = ttk.Entry(frame, width=30)
        self.lon_entry.grid(row=3, column=1, padx=5, pady=5)

        # Divider
        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(row=4, column=0, columnspan=2, sticky=tk.EW, pady=10)

        # Sección: Botones de acciones
        ttk.Label(frame, text="⚙️ Acciones Disponibles:").grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        ttk.Label(frame, text="Selecciona una acción para realizar predicciones o visualizar resultados.").grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        self.pred_btn = ttk.Button(frame, text="Predecir Troncal", command=self.mostrar_prediccion_troncal)
        self.pred_btn.grid(row=7, column=0, columnspan=2, pady=10)
        ttk.Label(frame, text="🔍 Predice la troncal correspondiente a las coordenadas ingresadas.").grid(row=8, column=0, columnspan=2, sticky=tk.W)

        self.arbol_btn = ttk.Button(frame, text="Ver Árbol de Decisión", command=self.mostrar_arbol_decision)
        self.arbol_btn.grid(row=9, column=0, columnspan=2, pady=10)
        ttk.Label(frame, text="🌳 Muestra el árbol de decisión utilizado para la predicción.").grid(row=10, column=0, columnspan=2, sticky=tk.W)

        self.kmeans_btn = ttk.Button(frame, text="Ver Agrupamiento KMeans", command=self.mostrar_agrupamiento_kmeans)
        self.kmeans_btn.grid(row=11, column=0, columnspan=2, pady=10)
        ttk.Label(frame, text="📊 Visualiza el agrupamiento KMeans de las estaciones.").grid(row=12, column=0, columnspan=2, sticky=tk.W)

        # Divider
        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(row=13, column=0, columnspan=2, sticky=tk.EW, pady=10)

        # Sección: Resultados
        ttk.Label(frame, text="📋 Resultados de Predecir Troncal:").grid(row=14, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))

        self.pred_text = tk.Text(frame, wrap=tk.WORD, width=90, height=5)
        self.pred_text.grid(row=16, column=0, columnspan=2, pady=10)

    def init_tab_mapa(self):
        frame = ttk.Frame(self.tab_mapa, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Selecciona una estación:").grid(row=0, column=0, sticky=tk.W)
        self.estacion_cb = AutocompleteCombobox(frame, width=50)
        self.estacion_cb.set_completion_list(self.lista_estaciones)
        self.estacion_cb.grid(row=0, column=1, padx=5, pady=5)

        self.ver_mapa_btn = ttk.Button(frame, text="Ver en Google Maps", command=self.mostrar_en_mapa)
        self.ver_mapa_btn.grid(row=1, column=0, columnspan=2, pady=10)

        self.mapa_text = tk.Text(frame, wrap=tk.WORD, width=80, height=12)
        self.mapa_text.grid(row=2, column=0, columnspan=2, pady=10)

    def calcular_ruta(self):
        """
        Calcula la mejor ruta entre las estaciones seleccionadas y muestra el resultado.

        Llama a las funciones `buscar_mejor_ruta_estaciones` y `buscar_ruta_alternativa` para encontrar
        la ruta directa o una ruta alternativa si no hay una ruta directa disponible.
        """
        origen = self.origen_cb.get().strip()
        destino = self.destino_cb.get().strip()
        self.resultado_text.config(state=tk.NORMAL)
        self.resultado_text.delete(1.0, tk.END)

        if not origen or not destino:
            messagebox.showwarning("Advertencia", "Seleccione la estación de origen y destino.")
            return

        ruta, dist_ruta = buscar_mejor_ruta_estaciones(self.grafo, origen, destino)
        if ruta:
            self.resultado_text.insert(tk.END, "Ruta directa encontrada:\n")
            self.resultado_text.insert(tk.END, " -> ".join(ruta) + "\n")
            self.resultado_text.insert(tk.END, f"Distancia total: {dist_ruta:.2f} km\n")
        else:
            self.resultado_text.insert(
                tk.END, "No se encontró una ruta directa entre las estaciones especificadas.\n"
            )
            ruta_alt, dist_alt, dist_restante, estacion_candidata = buscar_ruta_alternativa(
                self.grafo, self.estaciones, origen, destino)
            if ruta_alt:
                self.resultado_text.insert(tk.END, "\nRuta alternativa encontrada:\n")
                self.resultado_text.insert(tk.END, " -> ".join(ruta_alt) + "\n")
                self.resultado_text.insert(tk.END, f"Distancia de ruta: {dist_alt:.2f} km\n")
                self.resultado_text.insert(tk.END, f"La estación final es: {estacion_candidata}\n")
                self.resultado_text.insert(
                    tk.END, f"Distancia restante al destino: {dist_restante:.2f} km\n"
                )
            else:
                self.resultado_text.insert(
                    tk.END,
                    "\nNo se encontró ninguna ruta alternativa que se acerque al destino.")
            self.resultado_text.config(state=tk.DISABLED)

    def mostrar_prediccion_troncal(self):
        self.pred_text.config(state=tk.NORMAL)
        self.pred_text.delete(1.0, tk.END)

        try:
            lat = float(self.lat_entry.get())
            lon = float(self.lon_entry.get())
            if validate_lat_lon(self,lat, lon):
                troncal = predecir_troncal_por_coords(lat, lon)
                self.pred_text.insert(tk.END, f"Predicción de troncal para ({lat}, {lon}):\n")
                self.pred_text.insert(tk.END, f"➡️ Troncal: {troncal}\n")
                # Cargar el codificador para ver las etiquetas originales
                encoder = joblib.load("resources/label_encoder_troncal.pkl")
                self.pred_text.insert(tk.END, f"➡️ Etiquetas originales: {encoder.classes_}\n")
                self.pred_text.insert(tk.END, "✅ Predicción realizada con éxito.")

                # Exportar estaciones a CSV
                exportar_estaciones_csv(self.estaciones, "resources/estaciones_transmilenio.csv")
            else:
                self.pred_text.insert(tk.END, "❌ Coordenadas inválidas. Ingresa una latitud entre -90 y 90 y una longitud entre -180 y 180.")
        except ValueError:
            messagebox.showerror("Error", "Ingrese valores numéricos válidos para latitud y longitud.")

        self.pred_text.config(state=tk.DISABLED)

    def mostrar_arbol_decision(self):
        """
        Muestra el árbol de decisión en un pop-up.
        """
        try:
            # Cargar la imagen del árbol de decisión
            arbol_path = "resources/arbol_decision.png"
            arbol_img = Image.open(arbol_path)
            arbol_img = arbol_img.resize((600, 400), Image.Resampling.LANCZOS)  # Redimensionar si es necesario
            arbol_tk = ImageTk.PhotoImage(arbol_img)

            # Crear una nueva ventana para mostrar la imagen
            arbol_window = tk.Toplevel(self.root)
            arbol_window.title("Árbol de Decisión")
            arbol_window.geometry("720x520")

            # Mostrar la imagen en un label
            label = tk.Label(arbol_window, image=arbol_tk)
            label.image = arbol_tk  # Referencia para evitar que la imagen sea recolectada por el GC
            label.pack()

            # Agregar una descripción debajo de la imagen
            descripcion = tk.Label(arbol_window, text="Este es el árbol de decisión generado por el modelo.",
                                   font=("Arial", 10))
            descripcion.pack(pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el árbol de decisión:\n{e}")

    def mostrar_agrupamiento_kmeans(self):
        """
        Muestra la imagen del agrupamiento KMeans en un pop-up.
        """
        try:
            # Verificar si el archivo existe
            if not os.path.exists("resources/agrupamiento_kmeans.png"):
                realizar_agrupamiento_kmeans()


            # Cargar la imagen del agrupamiento KMeans
            agrupamiento_path = "resources/agrupamiento_kmeans.png"
            agrupamiento_img = Image.open(agrupamiento_path)
            agrupamiento_img = agrupamiento_img.resize((600, 400), Image.Resampling.LANCZOS)  # Redimensionar si es necesario
            agrupamiento_tk = ImageTk.PhotoImage(agrupamiento_img)

            # Crear una nueva ventana para mostrar la imagen
            agrupamiento_window = tk.Toplevel(self.root)
            agrupamiento_window.title("Agrupamiento KMeans")
            agrupamiento_window.geometry("720x520")

            # Mostrar la imagen en un label
            label = tk.Label(agrupamiento_window, image=agrupamiento_tk)
            label.image = agrupamiento_tk  # Referencia para evitar que la imagen sea recolectada por el GC
            label.pack()

            # Agregar una descripción debajo de la imagen
            descripcion = tk.Label(agrupamiento_window, text="Este es el resultado del agrupamiento KMeans.",
                                   font=("Arial", 10))
            descripcion.pack(pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el agrupamiento KMeans:\n{e}")

    def mostrar_en_mapa(self):
        estacion_nombre = self.estacion_cb.get().strip()
        self.mapa_text.config(state=tk.NORMAL)
        self.mapa_text.delete(1.0, tk.END)

        estacion = next((e for e in self.estaciones if e["nombre"] == estacion_nombre), None)

        if not estacion:
            self.mapa_text.insert(tk.END, "No se encontró la estación seleccionada.")
            return

        lat = estacion['latitud']
        lon = estacion['lon']
        link = f"https://www.google.com/maps?q={lat},{lon}"
        self.mapa_text.insert(tk.END, f"Estación: {estacion_nombre}\n")
        self.mapa_text.insert(tk.END, f"Troncal: {estacion['troncal']}\n")
        self.mapa_text.insert(tk.END, f"Coordenadas: ({lat}, {lon})\n")
        self.mapa_text.insert(tk.END, f"Ver en Google Maps: {link}\n")
        self.mapa_text.config(state=tk.DISABLED)
        webbrowser.open(link)
