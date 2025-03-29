import requests


def cargar_estaciones_api(url):
    """
    Carga las estaciones desde una API y las convierte en una lista de diccionarios.

    Parámetros:
        - url (str): La URL de la API desde donde se cargarán las estaciones.

    Retorna:
        list: Una lista de diccionarios con la información de las estaciones.

    Lanza:
        Exception: Si ocurre un error al llamar a la API o al procesar los datos.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        raise Exception(f"Error al llamar a la API: {e}")

    estaciones = []
    for feature in data.get("features", []):
        props = feature.get("properties", {})
        nombre = props.get("nombre_estacion", "Desconocida")
        lat = props.get("latitud_estacion", 0)
        lon = props.get("longitud_estacion", 0)
        troncal = props.get("troncal_estacion", "Sin troncal")
        estaciones.append({
            "nombre": nombre,
            "latitud": lat,
            "lon": lon,
            "troncal": troncal.strip().upper()
        })
    return estaciones