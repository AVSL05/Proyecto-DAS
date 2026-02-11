from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routes import search, promotions, reviews, newsletter
from app.router_auth import router as auth_router
from app.db import engine, Base


# --- Paths (según tu estructura) ---
APP_DIR = Path(__file__).resolve().parent              # .../Proyecto-DAS/app
PROJECT_ROOT = APP_DIR.parent                          # .../Proyecto-DAS

STATIC_DIR = PROJECT_ROOT / "static"                   # .../Proyecto-DAS/static
TEMPLATES_DIR = APP_DIR / "templates"                  # .../Proyecto-DAS/app/templates

app = FastAPI(
    title="Cuidado con el pug - Sistema de Renta de Transportes",
    description="API Backend para sistema de renta de transportes",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)

# --- Static & templates ---
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers API ---
app.include_router(search.router, prefix="/api/search", tags=["Búsqueda"])
app.include_router(promotions.router, prefix="/api/promotions", tags=["Promociones"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["Calificaciones"])
app.include_router(newsletter.router, prefix="/api/newsletter", tags=["Newsletter"])

# --- Auth router ---
app.include_router(auth_router)

# --- Frontend ---
@app.get("/", include_in_schema=False)
def root():
    return FileResponse(str(STATIC_DIR / "index.html"))

@app.get("/health", include_in_schema=False)
def health():
    return {"status": "ok"}

# --- Pages (Jinja) ---
@app.get("/register", response_class=HTMLResponse, include_in_schema=False)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/login", response_class=HTMLResponse, include_in_schema=False)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/forgot-password", response_class=HTMLResponse, include_in_schema=False)
def forgot_password_page(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})

@app.get("/reset-password", response_class=HTMLResponse, include_in_schema=False)
def reset_password_page(request: Request):
    return templates.TemplateResponse("reset_password.html", {"request": request})
