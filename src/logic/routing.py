import networkx as nx
from src.utils.distance import calcular_distancia


def construir_grafo_estaciones(estaciones, umbral_km=1.0):
    """
    Construye un grafo de estaciones basado en la distancia entre ellas.

    Parámetros:
        - estaciones (list): Lista de diccionarios con información de las estaciones.
        - umbral_km (float): Distancia máxima en kilómetros para conectar dos estaciones.

    Retorna:
        networkx.Graph: Grafo con las estaciones como nodos y las conexiones como aristas.
    """
    G = nx.Graph()
    for est in estaciones:
        G.add_node(est["nombre"], lat=est["latitud"], lon=est["lon"], troncal=est["troncal"])
    for i, est1 in enumerate(estaciones):
        for est2 in estaciones[i + 1:]:
            dist = calcular_distancia(est1["latitud"], est1["lon"], est2["latitud"], est2["lon"])
            if dist <= umbral_km:
                G.add_edge(est1["nombre"], est2["nombre"], weight=dist)
    return G


def buscar_mejor_ruta_estaciones(grafo, origen, destino):
    """
    Busca la mejor ruta entre dos estaciones en el grafo usando el algoritmo de Dijkstra.

    Parámetros:
        - grafo (networkx.Graph): Grafo de estaciones.
        - origen (str): Nombre de la estación de origen.
        - destino (str): Nombre de la estación de destino.

    Retorna:
        tuple: Una tupla con la ruta (lista de nombres de estaciones) y la distancia total.
    """
    try:
        ruta = nx.dijkstra_path(grafo, source=origen, target=destino, weight='weight')
        distancia = nx.dijkstra_path_length(grafo, source=origen, target=destino, weight='weight')
        return ruta, distancia
    except nx.NetworkXNoPath:
        return None, None


def buscar_ruta_alternativa(grafo, estaciones, origen, destino):
    """
    Busca una ruta alternativa entre dos estaciones en el grafo.

    Parámetros:
        - grafo (networkx.Graph): Grafo de estaciones.
        - estaciones (list): Lista de diccionarios con información de las estaciones.
        - origen (str): Nombre de la estación de origen.
        - destino (str): Nombre de la estación de destino.

    Retorna:
        tuple: Una tupla con la ruta alternativa (lista de nombres de estaciones),
               la distancia de la ruta alternativa, la distancia mínima a la estación destino,
               y el nombre de la mejor estación alternativa.
    """
    est_dest = next((est for est in estaciones if est["nombre"] == destino), None)
    if not est_dest:
        return None, None, None, None

    dest_troncal = est_dest["troncal"]
    componente = nx.node_connected_component(grafo, origen)

    candidatos = [n for n in componente if grafo.nodes[n]['troncal'] == dest_troncal]
    if not candidatos:
        candidatos = list(componente)

    mejor_estacion = None
    min_dist = float('inf')
    for nodo in candidatos:
        nodo_data = grafo.nodes[nodo]
        dist = calcular_distancia(nodo_data['lat'],
                                  nodo_data['lon'],
                                  est_dest["latitud"],
                                  est_dest["lon"])
        if dist < min_dist:
            min_dist = dist
            mejor_estacion = nodo

    ruta_alternativa, dist_ruta = buscar_mejor_ruta_estaciones(grafo, origen, mejor_estacion)
    return ruta_alternativa, dist_ruta, min_dist, mejor_estacion
