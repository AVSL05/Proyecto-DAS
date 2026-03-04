# Panel Administrativo - Instrucciones de Uso

## ✅ Problemas Resueltos

1. **Frontend actualizado** con diseño consistente con las páginas de usuario
2. **Router de administración migrado a MongoDB** (`admin_mongo.py`)
3. **JavaScript corregido** para cambio de pestañas
4. **Modelos MongoDB actualizados** con Payment y SupportTicket
5. **Datos de prueba** para visualizar información en el panel

## 🚀 Cómo Iniciar

### 1. Insertar Datos de Prueba (si aún no los tienes)

```bash
cd "/Users/angel/Desktop/Proyecto DAS"
source .venv/bin/activate
python3 seed_admin_data.py
```

Esto creará:

- Pagos para las reservaciones existentes
- Tickets de soporte de prueba
- Datos para visualizar en el panel

### 2. Iniciar el Servidor

```bash
cd "/Users/angel/Desktop/Proyecto DAS"
source .venv/bin/activate
python3 -m uvicorn app.main_mongo:app --reload --host 0.0.0.0 --port 8000
```

### 3. Acceder al Panel Administrativo

1. Abre tu navegador y ve a: `http://localhost:8000`
2. Inicia sesión con una cuenta **administrativa**
3. El sistema automáticamente te redirigirá al panel administrativo

**Cuentas de administrador:**

- Debes tener un usuario con `role: "administrativo"` en la base de datos
- Si no tienes uno, usa el script `set_user_role.py` para convertir un usuario en admin:
  ```bash
  python3 set_user_role.py <email> administrativo
  ```

## 🎨 Funcionalidades del Panel Administrativo

### **Configuración** (Vista Principal)

- **Estadísticas generales**: Usuarios totales, reservaciones, vehículos activos
- **Gestión de Reservaciones**: Ver, editar estados, agregar notas de admin
- **Gestión de Vehículos**: Actualizar precios, estados, activar/desactivar
- **Gestión de Usuarios**: Cambiar roles (cliente ↔ administrativo)

### **Ventas**

- **Ingresos del día y del mes**
- **Reservas cerradas y canceladas**
- **Reembolsos pendientes**
- **Ticket promedio**
- **Tabla de transacciones** con detalles de pagos

### **CRM** (Servicio al Cliente)

- **Casos totales y abiertos**
- **Alta prioridad**
- **Tabla de tickets** con información detallada
- **Panel de detalles** al seleccionar un caso

### **Sucursales**

- Vista de las sucursales disponibles
- Información de gerentes y contacto
- Flota y personal por sucursal

### **Lista de Prioridad**

- Alertas de pagos con más de 45 días sin cobertura
- Tareas operativas prioritarias

### **Organigrama**

- Estructura del equipo (Dirección, Gerencias, Operaciones)
- Fichas detalladas de colaboradores
- Información de contacto y certificaciones

### **Proveedores**

- Lista de proveedores con contratos activos
- Control de SLA y vigencias

## 🔧 Cambios de Pestañas

El problema del cambio de pestañas se resolvió agregando:

```javascript
document.addEventListener("DOMContentLoaded", function () {
  // Todo el código JavaScript se ejecuta después de que el DOM esté listo
});
```

Ahora los botones del sidebar funcionan correctamente:

- ✅ Cambia entre vistas
- ✅ Actualiza la URL con hash (#configuracion, #ventas, etc.)
- ✅ Recuerda la vista al recargar la página
- ✅ Se adapta a dispositivos móviles

## 📊 Conexión con la Base de Datos

Todas las rutas están conectadas a MongoDB:

| Ruta                | Endpoint                             | Función                 |
| ------------------- | ------------------------------------ | ----------------------- |
| Resumen             | GET `/api/admin/summary`             | Estadísticas generales  |
| Ventas              | GET `/api/admin/sales`               | Transacciones y totales |
| Alertas             | GET `/api/admin/payment-alerts`      | Pagos vencidos          |
| CRM                 | GET `/api/admin/crm`                 | Tickets de soporte      |
| Usuarios            | GET `/api/admin/users`               | Lista de usuarios       |
| Actualizar Rol      | PATCH `/api/admin/users/{id}/role`   | Cambiar rol de usuario  |
| Reservaciones       | GET `/api/admin/reservations`        | Lista de reservas       |
| Actualizar Reserva  | PATCH `/api/admin/reservations/{id}` | Editar reserva          |
| Vehículos           | GET `/api/admin/vehicles`            | Lista de vehículos      |
| Actualizar Vehículo | PATCH `/api/admin/vehicles/{id}`     | Editar vehículo         |

## 🎯 Funcionalidades Implementadas

### ✅ Cambio de Pestañas

- Navegación fluida entre secciones
- Animaciones suaves
- Sidebar colapsable
- Responsive design

### ✅ Gestión de Datos

- **Leer**: Todas las tablas cargan datos desde MongoDB
- **Actualizar**: Editar reservaciones, vehículos y usuarios
- **Refrescar**: Botones para actualizar datos en tiempo real

### ✅ Interfaz Mejorada

- Diseño consistente con páginas de usuario
- Fuente Abhaya Libre (font-weight: 800)
- Colores corporativos (#3575F6, #6366EB, #37399C)
- Footer con información de la empresa
- Mensajes de éxito/error animados

## 🎨 Diseño Visual

El panel administrativo ahora comparte el mismo diseño que las páginas de usuario:

- Header azul (#3575F6) con logo blanco
- Tipografía Abhaya Libre en negrita
- Cards con sombras suaves
- Botones con hover effects
- Footer corporativo

## 🐛 Solución de Problemas

### El panel no carga:

- Verifica que el servidor esté corriendo en el puerto 8000
- Comprueba que estés usando `main_mongo.py` (no `main.py`)
- Verifica la conexión a MongoDB

### No puedo iniciar sesión como admin:

```bash
python3 set_user_role.py <tu_email> administrativo
```

### Las tablas están vacías:

```bash
python3 seed_admin_data.py
```

### Errores de JavaScript en consola:

- Abre las herramientas de desarrollo (F12)
- Revisa la pestaña Console
- Verifica que `/static/admin.js` se cargue correctamente

## 📝 Notas Finales

- Todos los datos son ficticios y de prueba
- El organigrama usa datos estáticos (no en MongoDB)
- Las sucursales son datos de ejemplo
- Los proveedores son datos hardcoded

¡El panel administrativo está listo para usar! 🎉
