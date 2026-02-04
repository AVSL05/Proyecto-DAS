# Cuidado con el pug - Sistema de Renta de Transportes (Backend)

## Descripción

Backend del sistema de renta de transportes "Cuidado con el pug" desarrollado con FastAPI y Python 3.

## Características

- API REST para búsqueda de transportes
- Sistema de promociones
- Calificaciones y reviews de usuarios
- Suscripción a newsletter

## Estructura del Proyecto

```
Proyecto DAS/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Aplicación principal FastAPI
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Modelos Pydantic
│   └── routes/
│       ├── __init__.py
│       ├── search.py           # Endpoints de búsqueda
│       ├── promotions.py       # Endpoints de promociones
│       ├── reviews.py          # Endpoints de calificaciones
│       └── newsletter.py       # Endpoints de newsletter
├── requirements.txt
└── README.md
```

## Instalación

### 1. Crear entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

## Ejecutar el servidor

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

El servidor estará disponible en: `http://localhost:8000`

## Documentación de la API

Una vez el servidor esté corriendo, puedes acceder a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Endpoints Principales

### Homepage/Root

- `GET /` - Información general de la API
- `GET /health` - Health check del servicio

### Búsqueda de Transportes

- `POST /api/search/transport` - Buscar transportes disponibles
- `GET /api/search/locations` - Obtener ubicaciones disponibles
- `GET /api/search/available-dates` - Obtener fechas disponibles

### Promociones

- `GET /api/promotions` - Obtener todas las promociones activas
- `GET /api/promotions/{id}` - Obtener promoción específica

### Calificaciones/Reviews

- `GET /api/reviews` - Obtener reviews de usuarios
- `POST /api/reviews` - Crear nueva calificación
- `GET /api/reviews/average` - Obtener promedio de calificaciones

### Newsletter

- `POST /api/newsletter/subscribe` - Suscribirse al boletín
- `GET /api/newsletter/subscribers` - Listar suscriptores
- `DELETE /api/newsletter/unsubscribe/{email}` - Dar de baja

## Ejemplo de Uso

### Buscar transporte

```bash
curl -X POST "http://localhost:8000/api/search/transport" \
  -H "Content-Type: application/json" \
  -d '{
    "origen": "Ciudad de México",
    "destino": "Guadalajara",
    "fecha_salida": "2026-02-10",
    "num_pasajeros": 2
  }'
```

### Obtener promociones

```bash
curl -X GET "http://localhost:8000/api/promotions"
```

### Suscribirse al newsletter

```bash
curl -X POST "http://localhost:8000/api/newsletter/subscribe" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@example.com"
  }'
```

## Tecnologías Utilizadas

- **Python 3.11+**
- **FastAPI** - Framework web moderno y rápido
- **Pydantic** - Validación de datos
- **Uvicorn** - Servidor ASGI

## Notas

- Este es el backend para la homepage del sistema
- Actualmente usa datos en memoria (simulados)
- En producción se debe implementar conexión a base de datos (PostgreSQL/MongoDB)
- Falta implementar autenticación/autorización (JWT)
- El frontend se implementará posteriormente

## Próximos Pasos

- Implementar sistema de login/autenticación
- Integrar base de datos
- Agregar más funcionalidades de gestión de reservas
- Implementar sistema de pagos

## Contacto

Cuidado con el pug N.L., Calle linsana #69, cp 42067, San Nicolas de los Garza, Mexico

Copyright 2026 Cuidado con el pug | Todos los derechos reservados
