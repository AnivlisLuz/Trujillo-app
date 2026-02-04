#!/usr/bin/env python3
"""
Función para obtener el ID de distrito (relación OSM) dado un punto (lat, lng).
Usa el GeoJSON de distritos de Trujillo.
"""

import json
from pathlib import Path
from shapely.geometry import Point, Polygon

# Ruta al GeoJSON de distritos
GEOJSON_PATH = Path(__file__).parent / "distritos_trujillo.geojson"

# Cache de polígonos (se carga una sola vez)
_distritos = None


def _cargar_distritos():
    """Carga y convierte los distritos del GeoJSON a polígonos."""
    global _distritos
    if _distritos is not None:
        return _distritos

    with open(GEOJSON_PATH) as f:
        data = json.load(f)

    _distritos = []
    for feat in data['features']:
        if feat['geometry']['type'] != 'LineString':
            continue

        props = feat['properties']
        coords = feat['geometry']['coordinates']

        # Convertir LineString cerrado a Polygon
        # GeoJSON usa [lng, lat], Shapely también
        polygon = Polygon(coords)

        # Extraer ID de relación (formato: "relation/1968040")
        rel_id = props.get('@id', '')
        if rel_id.startswith('relation/'):
            rel_id = int(rel_id.replace('relation/', ''))
        else:
            continue

        _distritos.append({
            'id': rel_id,
            'name': props.get('name', ''),
            'ubigeo': props.get('pe:ubigeo', ''),
            'polygon': polygon
        })

    print(f"Cargados {len(_distritos)} distritos")
    return _distritos


def obtener_distrito(lat: float, lng: float) -> dict | None:
    """
    Obtiene el distrito al que pertenece un punto.

    Args:
        lat: Latitud
        lng: Longitud

    Returns:
        dict con 'id', 'name', 'ubigeo' o None si no está en ningún distrito
    """
    distritos = _cargar_distritos()
    punto = Point(lng, lat)  # Shapely usa (x, y) = (lng, lat)

    for distrito in distritos:
        if distrito['polygon'].contains(punto):
            return {
                'id': distrito['id'],
                'name': distrito['name'],
                'ubigeo': distrito['ubigeo']
            }

    return None


def obtener_distrito_id(lat: float, lng: float) -> int | None:
    """
    Obtiene solo el ID de relación OSM del distrito.

    Args:
        lat: Latitud
        lng: Longitud

    Returns:
        ID de relación OSM o None
    """
    resultado = obtener_distrito(lat, lng)
    return resultado['id'] if resultado else None


# Ejemplo de uso
if __name__ == "__main__":
    # Punto de prueba en Trujillo centro
    lat, lng = -8.1116, -79.0288

    print(f"Punto: ({lat}, {lng})")
    distrito = obtener_distrito(lat, lng)

    if distrito:
        print(f"Distrito: {distrito['name']}")
        print(f"ID OSM: {distrito['id']}")
        print(f"UBIGEO: {distrito['ubigeo']}")
    else:
        print("No encontrado en ningún distrito")
