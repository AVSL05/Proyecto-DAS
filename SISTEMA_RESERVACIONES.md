# Sistema de Reservaciones - Documentación

## ✅ Implementado

### Base de Datos

#### 📦 **Modelos Creados**:

1. **Vehicle** (Vehículos)
   - Información del vehículo (marca, modelo, año, tipo, capacidad)
   - Precios (por día y por hora)
   - Estado y disponibilidad
   - Características y descripción
   - Imagen

2. **Reservation** (Reservaciones)
   - Asociada a un usuario y un vehículo
   - Fechas de inicio y fin
   - Ubicación de recogida y devolución
   - Cálculo automático de días y precio total
   - Estados: pending, confirmed, in_progress, completed, cancelled
   - Notas del cliente y del administrador

#### 🔗 **Relaciones**:

- `User` → múltiples `Reservations`
- `Vehicle` → múltiples `Reservations`
- `Reservation` → un `User` y un `Vehicle`

---

## 🚀 API Endpoints

### **Vehículos** (`/api/vehicles`)

#### `GET /api/vehicles/`

Lista todos los vehículos disponibles con filtros opcionales.

**Query Parameters**:

- `vehicle_type`: van | pickup | truck | suv | minibus
- `min_capacity`: capacidad mínima
- `max_price`: precio máximo por día
- `is_available`: true (default) | false
- `skip`: paginación
- `limit`: límite de resultados

**Ejemplo**:

```bash
curl http://localhost:8000/api/vehicles/?vehicle_type=van&min_capacity=10
```

**Respuesta**:

```json
{
  "vehicles": [
    {
      "id": 1,
      "brand": "Toyota",
      "model": "Hiace",
      "year": 2022,
      "vehicle_type": "van",
      "capacity": 12,
      "plate": "ABC-1234",
      "price_per_day": "150.00",
      "status": "available",
      ...
    }
  ],
  "total": 1
}
```

---

#### `GET /api/vehicles/{vehicle_id}`

Obtiene detalles de un vehículo específico.

**Ejemplo**:

```bash
curl http://localhost:8000/api/vehicles/1
```

---

#### `GET /api/vehicles/types`

Lista todos los tipos de vehículos disponibles.

**Respuesta**:

```json
{
  "vehicle_types": ["van", "pickup", "truck", "suv", "minibus"]
}
```

---

#### `GET /api/vehicles/{vehicle_id}/availability`

Verifica si un vehículo está disponible en fechas específicas.

**Query Parameters**:

- `start_date`: fecha de inicio (ISO format)
- `end_date`: fecha de fin (ISO format)

**Ejemplo**:

```bash
curl "http://localhost:8000/api/vehicles/1/availability?start_date=2026-03-01T10:00:00Z&end_date=2026-03-05T10:00:00Z"
```

**Respuesta**:

```json
{
  "vehicle_id": 1,
  "start_date": "2026-03-01T10:00:00Z",
  "end_date": "2026-03-05T10:00:00Z",
  "is_available": true
}
```

---

### **Reservaciones** (`/api/reservations`)

> ⚠️ **Requiere autenticación**: Todas las rutas requieren token JWT en el header `Authorization: Bearer {token}`

#### `POST /api/reservations/`

Crea una nueva reservación.

**Body**:

```json
{
  "vehicle_id": 1,
  "start_date": "2026-03-01T10:00:00Z",
  "end_date": "2026-03-05T10:00:00Z",
  "pickup_location": "Aeropuerto Internacional",
  "return_location": "Centro de la ciudad",
  "notes": "Necesito GPS adicional"
}
```

**Validaciones**:

- ✅ El vehículo existe y está activo
- ✅ Las fechas son futuras
- ✅ El vehículo está disponible en esas fechas
- ✅ Calcula automáticamente días y precio total

**Respuesta**:

```json
{
  "id": 1,
  "user_id": 5,
  "vehicle_id": 1,
  "start_date": "2026-03-01T10:00:00Z",
  "end_date": "2026-03-05T10:00:00Z",
  "pickup_location": "Aeropuerto Internacional",
  "return_location": "Centro de la ciudad",
  "total_days": 4,
  "price_per_day": "150.00",
  "total_price": "600.00",
  "status": "pending",
  "notes": "Necesito GPS adicional",
  "created_at": "2026-02-16T10:00:00Z",
  "vehicle": { ... },
  "user_name": "Juan Pérez"
}
```

---

#### `GET /api/reservations/`

Lista todas las reservaciones del usuario actual.

**Query Parameters**:

- `status_filter`: pending | confirmed | in_progress | completed | cancelled
- `skip`: paginación
- `limit`: límite de resultados

**Ejemplo**:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/reservations/?status_filter=pending"
```

---

#### `GET /api/reservations/stats`

Obtiene estadísticas de reservaciones del usuario.

**Respuesta**:

```json
{
  "total_reservations": 10,
  "active_reservations": 2,
  "completed_reservations": 7,
  "cancelled_reservations": 1,
  "total_spent": "3500.00"
}
```

---

#### `GET /api/reservations/{reservation_id}`

Obtiene detalles de una reservación específica.

**Ejemplo**:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/reservations/1
```

---

#### `PUT /api/reservations/{reservation_id}`

Actualiza una reservación (solo si está en estado `pending`).

**Body** (todos los campos son opcionales):

```json
{
  "start_date": "2026-03-02T10:00:00Z",
  "end_date": "2026-03-06T10:00:00Z",
  "pickup_location": "Nueva ubicación",
  "notes": "Notas actualizadas"
}
```

**Validaciones**:

- ✅ Solo se pueden modificar reservaciones pendientes
- ✅ Verifica disponibilidad con las nuevas fechas
- ✅ Recalcula precios automáticamente

---

#### `DELETE /api/reservations/{reservation_id}`

Cancela una reservación.

**Restricciones**:

- ❌ No se pueden cancelar reservaciones completadas o ya canceladas

**Respuesta**:

```json
{
  "message": "Reservación cancelada exitosamente",
  "reservation_id": 1
}
```

---

## 🔒 Autenticación

Para hacer reservaciones, el usuario debe:

1. **Registrarse** o **iniciar sesión**:

   ```bash
   # Login
   curl -X POST http://localhost:8000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "password123"}'
   ```

2. **Usar el token** en todas las peticiones:
   ```bash
   curl -H "Authorization: Bearer eyJhbGc..." \
     http://localhost:8000/api/reservations/
   ```

---

## 📊 Datos de Ejemplo

Ya se agregaron **10 vehículos** de ejemplo:

- 2 Vans (Toyota Hiace, Mercedes Sprinter)
- 2 Pickups (Ford F-150, Chevrolet Silverado)
- 2 SUVs (Toyota Land Cruiser, Nissan Pathfinder)
- 2 Camiones (Isuzu NPR, Hino Serie 300)
- 2 Minibuses (Mercedes Sprinter Passenger, VW Crafter)

---

## 🧪 Pruebas Rápidas

### 1. Ver vehículos disponibles:

```bash
curl http://localhost:8000/api/vehicles/
```

### 2. Verificar disponibilidad:

```bash
curl "http://localhost:8000/api/vehicles/1/availability?start_date=2026-03-01T10:00:00Z&end_date=2026-03-05T10:00:00Z"
```

### 3. Crear reservación (requiere login):

```bash
# Primero login
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "tu@email.com", "password": "tu_password"}' \
  | jq -r '.token')

# Crear reservación
curl -X POST http://localhost:8000/api/reservations/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": 1,
    "start_date": "2026-03-01T10:00:00Z",
    "end_date": "2026-03-05T10:00:00Z",
    "pickup_location": "Aeropuerto"
  }'
```

### 4. Ver mis reservaciones:

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/reservations/
```

---

## 🔧 Características Implementadas

✅ **CRUD completo** de reservaciones
✅ **Validación de disponibilidad** automática
✅ **Cálculo automático** de días y precios
✅ **Prevención de reservaciones conflictivas**
✅ **Estados de reservación** (pending, confirmed, etc.)
✅ **Filtros y búsqueda** de vehículos
✅ **Estadísticas** de usuario
✅ **Autenticación** con JWT
✅ **Relaciones** entre usuarios, vehículos y reservaciones
✅ **Datos de ejemplo** pre-cargados

---

## 📱 Próximos Pasos (Frontend)

Ahora puedes crear el frontend para:

1. Mostrar catálogo de vehículos
2. Formulario de reservación con selector de fechas
3. Dashboard de usuario con sus reservaciones
4. Página de detalles de vehículo
5. Gestión de reservaciones (ver, editar, cancelar)

---

## 📚 Documentación Interactiva

Visita: **http://localhost:8000/docs**

Ahí encontrarás toda la documentación interactiva de Swagger con ejemplos y la posibilidad de probar todos los endpoints.
