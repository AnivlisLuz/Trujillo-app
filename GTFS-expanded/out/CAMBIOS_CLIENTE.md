# Cambios solicitados por el cliente

Fecha: 2026-02-05

## Cambios aplicados manualmente a los archivos GTFS

### 1. feed_info.txt - Cambio de feed_id

**Archivo:** `gtfs/feed_info.txt`

**Cambio:**
- Antes: `feed_id = trujillo-peru`
- Después: `feed_id = pe-trujillo`

**Motivo:** El cliente solicitó usar el formato `pe-trujillo` para el identificador del feed.

---

### 2. routes.txt - Diferenciar route_short_name de route_long_name

**Archivo:** `gtfs/routes.txt`

**Problema:** Según el estándar GTFS, `route_short_name` debe ser diferente de `route_long_name`. Anteriormente ambos campos tenían el mismo valor (ej: "M-01 C").

**Solución aplicada:**
- `route_short_name`: Se mantiene el código de ruta (tag `ref` de OSM). Ej: "M-01 C"
- `route_long_name`: Se usa el nombre descriptivo de OSM (tag `name`). Ej: "Via Panamericana Norte → Av. Manuel Seoane"

**Lógica para obtener route_long_name:**
1. Desde `trips.txt` se obtiene el primer `shape_id` para cada `route_id`
2. El `shape_id` corresponde al ID de la relación en OSM
3. Desde `log.json` se obtiene el tag `name` de esa relación OSM
4. El `name` de OSM tiene el formato "Origen → Destino"

**Ejemplo:**
```
route_id: 0
route_short_name: M-01 C
route_long_name: Via Panamericana Norte → Av. Manuel Seoane
```

---

### 3. trips.txt - Agregar direction_id (ida/vuelta)

**Archivo:** `gtfs/trips.txt`

**Problema:** El archivo no tenía la columna `direction_id`. Según GTFS, sin este campo se asume `0` para todos los viajes, lo que no diferencia ida de vuelta.

**Importancia:** La app del Driver necesita `direction_id` para asignar automáticamente el sentido del recorrido sin intervención manual del conductor.

**Solución aplicada:**
- Se agregó la columna `direction_id` después de `shape_id`
- `direction_id = 0`: Ida (primer shape de cada ruta)
- `direction_id = 1`: Vuelta (segundo shape de cada ruta)

**Lógica para asignar direction_id:**
1. Para cada `route_id`, se ordenan los `shape_id` únicos
2. El primer shape → `direction_id = 0`
3. El segundo shape → `direction_id = 1`
4. Si hay más shapes (variantes), se alternan (0, 1, 0, 1...)

**Ejemplo:**
```
route_id: 0 (M-01 C)
├── shape 19946662 → direction_id=0 (ida)    → headsign: "Av. Manuel Seoane"
└── shape 19946938 → direction_id=1 (vuelta) → headsign: "Via Panamericana Norte"
```

**Estructura del archivo:**
```
Antes:  trip_id,route_id,service_id,shape_id,trip_headsign
Después: trip_id,route_id,service_id,shape_id,direction_id,trip_headsign
```

---

## Para hacer estos cambios permanentes en el generador (index.ts)

Para que estos cambios sobrevivan una regeneración del GTFS, se debe modificar `index.ts`:

### Cambio 1: feed_id

En la sección `gtfsOptions.feed`, cambiar:
```typescript
id: 'trujillo-peru-stoptimes',
```
Por:
```typescript
id: 'pe-trujillo',
```

### Cambio 2: route_long_name

El `trufi-gtfs-builder` actualmente usa el tag `ref` de OSM para ambos campos.
Se necesita modificar la configuración para usar:
- `ref` → `route_short_name`
- `name` → `route_long_name`

Esto puede requerir modificar el builder o agregar un post-procesamiento.

### Cambio 3: direction_id

El `trufi-gtfs-builder` no genera `direction_id` por defecto.
Opciones para implementarlo:
1. **Post-procesamiento**: Script que agrega la columna después de generar el GTFS
2. **Modificar el builder**: Agregar lógica para determinar dirección basándose en el orden de shapes por ruta

La lógica recomendada:
- Agrupar shapes por `route_id`
- Ordenar por `shape_id`
- Primer shape = `direction_id=0`, segundo = `direction_id=1`
- Alternar para rutas con más de 2 shapes

---

## Notas adicionales

### Rutas con múltiples shapes

Algunas rutas tienen más de 2 shapes (ida/vuelta) porque tienen:
1. **Variantes de ruta** con diferentes terminales
2. **Duplicados** en OSM (misma ruta mapeada varias veces)

Para el `route_long_name` se usa el `name` del primer shape encontrado.

### Relación de IDs

| GTFS | OSM |
|------|-----|
| `route_id` | Número secuencial (0, 1, 2...) |
| `shape_id` | ID de relación OSM |
| `trip_id` | Formato: `{OSM_ID}{secuencia}` |

El `shape_id` en GTFS corresponde directamente al ID de la relación en OSM.
