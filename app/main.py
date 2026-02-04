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
