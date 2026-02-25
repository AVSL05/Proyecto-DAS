# Migración a MongoDB - Proyecto DAS

## ¡Bienvenido a la versión escalable con MongoDB! 🚀

Este proyecto ha sido migrado de SQLite/SQLAlchemy a MongoDB para mejorar la escalabilidad y el rendimiento.

## Cambios Principales

### Arquitectura

- **Base de datos**: SQLite → MongoDB
- **ORM/ODM**: SQLAlchemy → Beanie (ODM async para MongoDB)
- **Driver**: Motor (async MongoDB driver)

### Estructura de Archivos

#### Nuevos Archivos (MongoDB)

- `app/mongodb.py` - Configuración de conexión MongoDB
- `app/mongodb_models.py` - Modelos de documentos MongoDB
- `app/main_mongo.py` - Aplicación principal con MongoDB
- `app/router_auth_mongo.py` - Rutas de autenticación migradas
- `app/routes/*_mongo.py` - Todas las rutas migradas a MongoDB
- `app/schemas_reservations_mongo.py` - Schemas actualizados para MongoDB

#### Archivos Antiguos (mantener para referencia)

- `app/main.py` - Versión antigua con SQLAlchemy
- `app/db.py` - Configuración SQLAlchemy
- `app/db_models.py` - Modelos SQLAlchemy
- Otros archivos `*_old` o sin sufijo `_mongo`

## Instalación de MongoDB

### Opción 1: MongoDB Local (macOS)

```bash
# Instalar MongoDB con Homebrew
brew tap mongodb/brew
brew install mongodb-community@7.0

# Iniciar MongoDB como servicio
brew services start mongodb-community@7.0

# Verificar que está corriendo
mongosh --eval "db.version()"
```

### Opción 2: MongoDB Atlas (Cloud - Recomendado para producción)

1. Ve a [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Crea una cuenta gratuita
3. Crea un cluster (el tier gratuito es suficiente)
4. Obtén tu connection string
5. Actualiza el `.env`:

```env
MONGODB_URL=mongodb+srv://usuario:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=proyecto_das_db
```

### Opción 3: Docker (Desarrollo)

```bash
# Crear y ejecutar contenedor MongoDB
docker run -d \
  --name mongodb-das \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password \
  -v mongodb_data:/data/db \
  mongo:7.0

# Connection string para .env
# MONGODB_URL=mongodb://admin:password@localhost:27017/
```

## Configuración

### 1. Variables de Entorno (.env)

```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=proyecto_das_db

# JWT Configuration
JWT_SECRET=tu-secreto-super-seguro-cambiar-en-produccion
JWT_ALG=HS256
JWT_TTL_SECONDS=3600

# Google OAuth (opcional)
GOOGLE_CLIENT_ID=tu_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=tu_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
```

### 2. Instalar Dependencias

```bash
pip install -r requirements.txt
```

## Ejecutar la Aplicación

### Con MongoDB (Nueva versión)

```bash
# Asegúrate de que MongoDB esté corriendo
uvicorn app.main_mongo:app --reload --host 0.0.0.0 --port 8000
```

### Con SQLite (Versión antigua - para referencia)

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Colecciones de MongoDB

El sistema crea las siguientes colecciones automáticamente:

1. **users** - Usuarios del sistema
   - Índices: email, google_id, role
2. **password_reset_tokens** - Tokens de reseteo de contraseña
   - Índices: user_id, token_hash, expires_at
3. **vehicles** - Vehículos disponibles
   - Índices: plate, vehicle_type, status, is_active
4. **reservations** - Reservaciones de vehículos
   - Índices: user_id, vehicle_id, status, start_date, end_date
5. **reviews** - Calificaciones y reseñas
   - Índices: fecha, calificacion
6. **newsletter_subscribers** - Suscriptores del boletín
   - Índices: email, active
7. **promotions** - Promociones activas
   - Índices: activa, fecha_inicio, fecha_fin

## Migración de Datos (SQLite → MongoDB)

Si tienes datos en SQLite que deseas migrar a MongoDB, ejecuta:

```bash
python migrate_to_mongodb.py
```

Este script:

1. Lee todos los datos de `dev.db` (SQLite)
2. Los convierte al formato MongoDB
3. Los inserta en las colecciones correspondientes

## API Endpoints

Todos los endpoints permanecen igual:

- **Auth**: `/api/auth/*`
- **Vehicles**: `/api/vehicles/*`
- **Reservations**: `/api/reservations/*`
- **Reviews**: `/api/reviews/*`
- **Newsletter**: `/api/newsletter/*`
- **Promotions**: `/api/promotions/*`
- **Search**: `/api/search/*`
- **Admin**: `/api/admin/*` (pendiente migración)

## Documentación API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Ventajas de MongoDB

### 1. **Escalabilidad Horizontal**

- Fácil sharding y replicación
- Manejo de grandes volúmenes de datos

### 2. **Flexibilidad del Esquema**

- Esquemas dinámicos
- Fácil adición de nuevos campos

### 3. **Performance**

- Queries más rápidas en datasets grandes
- Índices eficientes

### 4. **Alta Disponibilidad**

- Replica sets automáticos
- Failover automático

### 5. **Consultas Ricas**

- Agregaciones complejas
- Búsquedas geoespaciales
- Full-text search

## Verificar la Instalación

```bash
# 1. Verificar MongoDB
mongosh

# 2. Listar bases de datos
show dbs

# 3. Usar la base de datos del proyecto
use proyecto_das_db

# 4. Ver colecciones
show collections

# 5. Contar documentos
db.users.countDocuments()
db.vehicles.countDocuments()
db.reservations.countDocuments()
```

## Monitoreo y Administración

### MongoDB Compass (GUI)

Descarga: https://www.mongodb.com/try/download/compass

Connection string: `mongodb://localhost:27017`

### Comandos Útiles

```javascript
// Ver todos los usuarios
db.users.find().pretty();

// Ver vehículos disponibles
db.vehicles.find({ is_active: true, status: "available" });

// Ver reservaciones pendientes
db.reservations.find({ status: "pending" });

// Crear índices manualmente (ya se crean automáticamente)
db.users.createIndex({ email: 1 }, { unique: true });
db.vehicles.createIndex({ plate: 1 }, { unique: true });
```

## Troubleshooting

### Error: "Connection refused"

```bash
# Verificar que MongoDB esté corriendo
brew services list | grep mongodb

# Reiniciar MongoDB
brew services restart mongodb-community@7.0
```

### Error: "Database not found"

- MongoDB crea la base de datos automáticamente al insertar el primer documento
- No es necesario crearla manualmente

### Error: "Module not found: motor/beanie"

```bash
# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

## Backup y Restore

### Backup

```bash
mongodump --db proyecto_das_db --out ./backup
```

### Restore

```bash
mongorestore --db proyecto_das_db ./backup/proyecto_das_db
```

## Desarrollo y Testing

### Datos de Prueba

Ejecuta los scripts existentes:

```bash
# Crear vehículos de prueba
python seed_vehicles.py

# Ver usuarios
python see_users.py

# Establecer roles
python set_user_role.py
```

## Próximos Pasos

1. ✅ Migración completa a MongoDB
2. ⏳ Migrar rutas de admin
3. ⏳ Implementar búsqueda full-text
4. ⏳ Agregar caché con Redis
5. ⏳ Implementar websockets para notificaciones en tiempo real

## Soporte

Para preguntas o problemas:

- Documentación MongoDB: https://docs.mongodb.com/
- Beanie ODM: https://beanie-odm.dev/
- Motor Driver: https://motor.readthedocs.io/

---

**¡Felicidades! Tu proyecto ahora es más escalable con MongoDB** 🎉
