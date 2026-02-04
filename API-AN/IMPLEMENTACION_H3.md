# Implementación H3 y Distritos - Proyecto Trujillo

**Fecha:** 4 de febrero 2026

---

## 1. Índice H3

**Resolución:** 15 (máxima, ~1 metro)

### Función de Cálculo

```python
import h3

def calcular_h3(lat: float, lng: float) -> str:
    """Calcula el índice H3 en resolución máxima (15)."""
    return h3.latlng_to_cell(lat, lng, 15)
```

**Instalación:** `pip install h3`

### Truncar Resolución (responsabilidad del consumidor)

```python
import h3

h3_res15 = "8f8f53ac5c6dcca"
h3_res9 = h3.cell_to_parent(h3_res15, 9)   # ~360m
```

| Resolución | Tamaño |
|------------|--------|
| 7 | ~2.6 km |
| 9 | ~360 m |
| 11 | ~50 m |
| 15 | ~1 m |

---

## 2. Distrito (ID relación OSM)

### Función de Cálculo

```python
from obtener_distrito import obtener_distrito_id

def calcular_distrito(lat: float, lng: float) -> int | None:
    """Obtiene el ID de relación OSM del distrito."""
    return obtener_distrito_id(lat, lng)
```

**Requiere:** `pip install shapely`

**Archivo:** `obtener_distrito.py` + `distritos_trujillo.geojson`

---

## 3. ID de Usuario

Se requiere un campo de identificación de usuario para cada petición.

> **Nota:** La notación del campo puede cambiar según la implementación (ej: `user_id`, `usuario_id`, `device_id`), pero es obligatorio tener un identificador único por usuario/dispositivo.

---

## 4. Ejemplo Completo

```
ANTES:
{
  "user_id": "usr_abc123",
  "origen_lat": -8.1116,
  "origen_lng": -79.0288,
  "destino_lat": -8.1050,
  "destino_lng": -79.0350,
  "timestamp": "2026-02-04T15:30:00Z"
}

DESPUÉS:
{
  "user_id": "usr_abc123",
  "origen_lat": -8.1116,
  "origen_lng": -79.0288,
  "h3_origen": "8f8f53ac5c6dcca",
  "distrito_origen": 1968056,
  "destino_lat": -8.1050,
  "destino_lng": -79.0350,
  "h3_destino": "8f8f53ac5c43f36",
  "distrito_destino": 1968056,
  "timestamp": "2026-02-04T15:30:00Z"
}
```

---

## 5. Visualización en Power BI (responsabilidad del consumidor)

> **Nota:** La visualización es responsabilidad del consumidor de la API. Esta sección solo documenta que es posible consumir los datos H3 en Power BI.

Usar **Icon Map Pro** (visual custom):

1. Instalar desde AppSource: buscar "Icon Map Pro"
2. Pasar campo `h3_index` y valor a mostrar
3. Renderiza hexágonos automáticamente

Más info: https://www.iconmappro.com/docs/data/h3

---

## 6. Documentación

- H3: https://h3geo.org/docs/
- H3 Python: https://uber.github.io/h3-py/api_quick_overview.html
- Shapely: https://shapely.readthedocs.io/
