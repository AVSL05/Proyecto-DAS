from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Importar configuración MongoDB
from app.mongodb import connect_to_mongo, close_mongo_connection

# Importar routers MongoDB
from app.routes import search
from app.routes import reviews_mongo as reviews
from app.routes import newsletter_mongo as newsletter
from app.routes import promotions_mongo as promotions
from app.routes import vehicles_mongo as vehicles
from app.routes import reservations_mongo as reservations
from app.router_auth_mongo import router as auth_router

# --- Paths (según tu estructura) ---
APP_DIR = Path(__file__).resolve().parent              # .../Proyecto-DAS/app
PROJECT_ROOT = APP_DIR.parent                          # .../Proyecto-DAS

STATIC_DIR = PROJECT_ROOT / "static"                   # .../Proyecto-DAS/static
TEMPLATES_DIR = APP_DIR / "templates"                  # .../Proyecto-DAS/app/templates

app = FastAPI(
    title="Cuidado con el pug - Sistema de Renta de Transportes (MongoDB)",
    description="API Backend para sistema de renta de transportes con MongoDB",
    version="2.0.0"
)


# --- Manejador de errores de validación ---
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"❌ Error de validación: {exc.errors()}")
    print(f"Body recibido: {exc.body}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": str(exc.body)},
    )


# --- Event handlers para MongoDB ---
@app.on_event("startup")
async def startup_db_client():
    """Conectar a MongoDB al iniciar la aplicación"""
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown_db_client():
    """Cerrar conexión a MongoDB al apagar la aplicación"""
    await close_mongo_connection()


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
app.include_router(vehicles.router)  # Ya tiene el prefix en el router
app.include_router(reservations.router)  # Ya tiene el prefix en el router
# app.include_router(admin.router)  # TODO: Migrar admin a MongoDB

# --- Auth router ---
app.include_router(auth_router)

# --- Frontend ---
@app.get("/", include_in_schema=False)
def root():
    return FileResponse(str(STATIC_DIR / "index.html"))

@app.get("/health", include_in_schema=False)
async def health():
    """Health check endpoint"""
    return {"status": "ok", "database": "mongodb"}

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
