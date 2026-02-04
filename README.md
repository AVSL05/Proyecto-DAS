# Proyecto-DAS

# 🚐 Renta de Camionetas (tipo SENDA)

Plataforma web para **rentar camionetas de transporte** (tipo SENDA) de forma sencilla y segura.  
Este proyecto se desarrolla como parte de la materia **Diseño de Arquitectura Informática**, utilizando:

- **Backend:** Python 3  
- **Frontend:** JavaScript (SPA o multipágina, según implementación)  
- **Base de Datos:** SQL (modelo relacional)

---

## 🎯 Objetivo del proyecto

Construir una aplicación web que permita:

- Consultar disponibilidad de camionetas por fecha/horario.
- Registrar y autenticar usuarios (clientes y administradores).
- Crear y gestionar reservas.
- Administrar unidades (camionetas), rutas/destinos y precios.
- Mantener un historial de rentas y control básico de estados.

---

## 🧩 Alcance (Features)

### 👤 Cliente
- Registro e inicio de sesión
- Búsqueda de camionetas disponibles
- Reservación (selección de fechas, origen/destino, número de pasajeros)
- Confirmación y consulta de reservas
- Cancelación (según políticas)

### 🛠️ Administrador
- Alta / baja / edición de camionetas
- Gestión de rutas o destinos
- Gestión de precios y disponibilidad
- Ver reservas y cambiar estados (pendiente, confirmada, cancelada, finalizada)
- Reporte básico (opcional)

---

## 🏗️ Arquitectura (alto nivel)

El sistema se divide en tres capas principales:

- **Frontend (JavaScript):** interfaz de usuario y consumo de API.
- **Backend (Python 3):** lógica de negocio, autenticación, validaciones y endpoints.
- **Base de datos (SQL):** persistencia (usuarios, reservas, unidades, etc.).

> Modelo recomendado: arquitectura por capas (presentación / negocio / datos) y API REST.

---

## 🧰 Tecnologías sugeridas

> Pueden ajustar esto según lo que estén usando realmente.

### Backend (Python 3)
- Framework sugerido: **Flask** o **FastAPI**
- Autenticación: JWT o sesiones
- Validaciones: Pydantic (si usan FastAPI) o validación manual
- ORM sugerido: SQLAlchemy (opcional)

### Frontend (JavaScript)
- Vanilla JS o framework (React/Vue) según se defina
- Fetch/Axios para consumir API
- UI: Bootstrap/Tailwind (opcional)

### Base de Datos
- SQL Server / MySQL / PostgreSQL (según decisión del equipo)
- Migraciones: Alembic / scripts SQL (opcional)

---

## 📁 Estructura del repositorio

```bash
/
├─ Main/                # API en Python 3
│  ├─ app/
│  ├─ requirements.txt
│  └─ README.md
├─ frontend/               # Interfaz en JavaScript
│  ├─ src/
│  └─ README.md
├─ database/               # Modelo y scripts SQL
│  ├─ schema/
│  ├─ seed/
│  └─ README.md
├─ docs/                   # Documentación (arquitectura, diagramas, decisiones)
├─ .github/                # Templates / workflows (opcional)
└─ README.md               # Este archivo
