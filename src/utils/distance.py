import math


def calcular_distancia(lat1, lon1, lat2, lon2):
    """
    Calcula la distancia entre dos puntos geográficos usando la fórmula del haversine.

    La fórmula del haversine se utiliza para encontrar la distancia entre dos puntos en
    la superficie de una esfera, dados sus latitudes y longitudes. Es especialmente útil
    para calcular distancias en la superficie de la Tierra.

    La fórmula es:
        - R = radio de la Tierra
        - Δ lat = lat2− lat1
        - Δ long = long2− long1
        - a = sin²(Δ lat/2) + cos(lat1) · cos(lat2) · sin²(Δ long/2)
        - c = 2 · atan2(√a, √(1−a))
        - d = R · c

    fuente: https://acortar.link/LpF41F

    Parámetros:
        - lat1 (float): Latitud del primer punto.
        - lon1 (float): Longitud del primer punto.
        - lat2 (float): Latitud del segundo punto.
        - lon2 (float): Longitud del segundo punto.

    Retorna:
    float: Distancia entre los dos puntos en kilómetros.
    """
    R = 6371  # Radio de la Tierra en km
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c
