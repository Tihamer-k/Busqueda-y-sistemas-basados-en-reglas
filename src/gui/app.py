import re
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser

import joblib
from PIL import ImageTk, Image

from src.gui.autocombo import AutocompleteCombobox
from src.logic.data import cargar_estaciones_api
from src.logic.routing import (
    construir_grafo_estaciones,
    buscar_mejor_ruta_estaciones,
    buscar_ruta_alternativa
)
from src.logic.modelo_ml import predecir_troncal_por_coords

API_URL = ("https://gis.transmilenio.gov.co/arcgis/rest/services/"
           "Troncal/consulta_estaciones_troncales/FeatureServer/0/"
           "query?outFields=*&where=1%3D1&f=geojson")


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

        ttk.Label(frame, text="Estación de Origen: ").grid(row=0, column=0, sticky=tk.W)
        self.origen_cb = AutocompleteCombobox(frame, width=50)
        self.origen_cb.set_completion_list(self.lista_estaciones)
        self.origen_cb.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Estación de Destino: ").grid(row=1, column=0, sticky=tk.W)
        self.destino_cb = AutocompleteCombobox(frame, width=50)
        self.destino_cb.set_completion_list(self.lista_estaciones)
        self.destino_cb.grid(row=1, column=1, padx=5, pady=5)

        self.buscar_btn = ttk.Button(frame, text="Buscar Ruta", command=self.calcular_ruta)
        self.buscar_btn.grid(row=2, column=0, columnspan=2, pady=10)

        self.resultado_text = tk.Text(frame, wrap=tk.WORD, width=80, height=20)
        self.resultado_text.grid(row=3, column=0, columnspan=2, pady=10)

    def init_tab_prediccion(self):
        frame = ttk.Frame(self.tab_prediccion, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Latitud:").grid(row=0, column=0, sticky=tk.W)
        self.lat_entry = ttk.Entry(frame, width=30)
        self.lat_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Longitud:").grid(row=1, column=0, sticky=tk.W)
        self.lon_entry = ttk.Entry(frame, width=30)
        self.lon_entry.grid(row=1, column=1, padx=5, pady=5)

        self.pred_btn = ttk.Button(frame, text="Predecir Troncal", command=self.mostrar_prediccion_troncal)
        self.pred_btn.grid(row=2, column=0, columnspan=2, pady=10)

        self.pred_text = tk.Text(frame, wrap=tk.WORD, width=80, height=12)
        self.pred_text.grid(row=3, column=0, columnspan=2, pady=10)

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

            else:
                self.pred_text.insert(tk.END, "❌ Coordenadas inválidas. Ingresa una latitud entre -90 y 90 y una longitud entre -180 y 180.")
        except ValueError:
            messagebox.showerror("Error", "Ingrese valores numéricos válidos para latitud y longitud.")

        self.pred_text.config(state=tk.DISABLED)

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
