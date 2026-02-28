from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.routes import admin, newsletter, promotions, reservations, reviews, search, support, vehicles
from app.router_auth import router as auth_router
from app.db import Base, engine, ensure_user_role_column


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
ensure_user_role_column()

# --- Static & templates ---
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# --- Session middleware for OAuth ---
app.add_middleware(
    SessionMiddleware,
    secret_key="your-secret-key-change-in-production-please-make-it-random"
)

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
app.include_router(support.router)
app.include_router(vehicles.router)  # Ya tiene el prefix en el router
app.include_router(reservations.router)  # Ya tiene el prefix en el router
app.include_router(admin.router)

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

@app.get("/admin", response_class=HTMLResponse, include_in_schema=False)
def admin_dashboard_page(request: Request):
    return templates.TemplateResponse("admin_dashboard.html", {"request": request})


@app.get("/payment", include_in_schema=False)
def payment_page():
    return FileResponse(str(STATIC_DIR / "payment.html"))

@app.get("/perfil", include_in_schema=False)
def perfil_page():
    return FileResponse(str(STATIC_DIR / "perfil.html"))

@app.get("/mis-reservas", include_in_schema=False)
def mis_reservas_page():
    return FileResponse(str(STATIC_DIR / "mis-reservas.html"))

@app.get("/metodos-pago", include_in_schema=False)
def metodos_pago_page():
    return FileResponse(str(STATIC_DIR / "metodos-pago.html"))
