import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from dotenv import load_dotenv
from src.logic.data import cargar_estaciones_api

# Cargar la URL desde .env
load_dotenv()
API_URL = os.getenv("API_TRANSMILENIO")

def realizar_agrupamiento_kmeans():
    if not API_URL:
        raise ValueError("No se encontró la variable API_TRANSMILENIO en el archivo .env")

    # 1. Cargar estaciones desde la API
    estaciones = cargar_estaciones_api(API_URL)

    # 2. Crear DataFrame
    estaciones_df = pd.DataFrame(estaciones)

    # 3. Eliminar entradas sin coordenadas válidas
    estaciones_df = estaciones_df[(estaciones_df['latitud'] != 0) & (estaciones_df['lon'] != 0)]

    # 4. Seleccionar características (latitud y longitud)
    X = estaciones_df[['latitud', 'lon']]

    # 5. Aplicar KMeans con 5 clústeres (puedes ajustar el número de clústeres según el análisis)
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    estaciones_df['cluster'] = kmeans.fit_predict(X)

    # 6. Graficar agrupaciones
    plt.figure(figsize=(10, 6))
    colors = ['red', 'green', 'blue', 'purple', 'orange']
    for i in range(5):
        cluster_points = estaciones_df[estaciones_df['cluster'] == i]
        plt.scatter(cluster_points['lon'], cluster_points['latitud'],
                    c=colors[i], label=f'Cluster {i}', alpha=0.6)

    plt.title('Agrupación de Estaciones TransMilenio (KMeans)')
    plt.xlabel('Longitud')
    plt.ylabel('Latitud')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # 7. Guardar resultado
    output_path = "resources/agrupamiento_kmeans.png"
    plt.savefig(output_path)
    print(f"✅ Clustering realizado y gráfico guardado en: {output_path}")

    # 8. Exportar CSV con cluster asignado
    csv_path = "resources/estaciones_clusterizadas.csv"
    estaciones_df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"✅ Estaciones exportadas con clúster a: {csv_path}")
