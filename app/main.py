from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routes import search, promotions, reviews, newsletter

app = FastAPI(
    title="Cuidado con el pug - Sistema de Renta de Transportes",
    description="API Backend para sistema de renta de transportes",
    version="1.0.0"
)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas
app.include_router(search.router, prefix="/api/search", tags=["Búsqueda"])
app.include_router(promotions.router, prefix="/api/promotions", tags=["Promociones"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["Calificaciones"])
app.include_router(newsletter.router, prefix="/api/newsletter", tags=["Newsletter"])

# Ruta para servir el frontend
@app.get("/")
async def serve_frontend():
    return FileResponse("static/index.html")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Cuidado con el pug Backend"}

# Registro, login y recuperación de contraseña se manejan en app/routers_auth.py

import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from .db import engine, Base
from .routers_auth import router as auth_router

app = FastAPI(title="Renta de Camionetas (tipo SENDA)")

Base.metadata.create_all(bind=engine)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

app.include_router(auth_router)

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/register")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/forgot-password", response_class=HTMLResponse)
def forgot_password_page(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})

@app.get("/reset-password", response_class=HTMLResponse)
def reset_password_page(request: Request):
    # El token viene en querystring: /reset-password?token=...
    return templates.TemplateResponse("reset_password.html", {"request": request})
