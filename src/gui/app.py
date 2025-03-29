import tkinter as tk
from tkinter import ttk, messagebox
from src.gui.autocombo import AutocompleteCombobox
from src.logic.data import cargar_estaciones_api
from src.logic.routing import (
    construir_grafo_estaciones,
    buscar_mejor_ruta_estaciones,
    buscar_ruta_alternativa
)

API_URL = ("https://gis.transmilenio.gov.co/arcgis/rest/services/"
           "Troncal/consulta_estaciones_troncales/FeatureServer/0/"
           "query?outFields=*&where=1%3D1&f=geojson")


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
        self.root.geometry("720x500")

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

        frame = ttk.Frame(root, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Estación de Origen:").grid(row=0, column=0, sticky=tk.W)
        self.origen_cb = AutocompleteCombobox(frame, width=50)
        self.origen_cb.set_completion_list(self.lista_estaciones)
        self.origen_cb.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Estación de Destino:").grid(row=1, column=0, sticky=tk.W)
        self.destino_cb = AutocompleteCombobox(frame, width=50)
        self.destino_cb.set_completion_list(self.lista_estaciones)
        self.destino_cb.grid(row=1, column=1, padx=5, pady=5)

        self.buscar_btn = ttk.Button(frame, text="Buscar Ruta", command=self.calcular_ruta)
        self.buscar_btn.grid(row=2, column=0, columnspan=2, pady=10)

        self.resultado_text = tk.Text(frame, wrap=tk.WORD, width=80, height=20)
        self.resultado_text.grid(row=3, column=0, columnspan=2, pady=10)

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
