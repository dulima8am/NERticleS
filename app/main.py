from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.endpoints import router as pipeline_router
from app.services.db_service import init_db
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Ciclo de vida de la aplicación.
    Se ejecuta al arrancar y al detener el servidor.
    """
    # Al arrancar: inicializar la base de datos
    print("[Main] 🚀 Iniciando aplicación...")
    init_db()
    print("[Main] ✅ Base de datos inicializada.")
    yield
    # Al detener (si necesitas limpiar algo, va aquí)
    print("[Main] 🛑 Deteniendo aplicación...")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Pipeline asíncrono de 7 etapas para el análisis automático de artículos periodísticos.",
    lifespan=lifespan
)

# Registramos las rutas
app.include_router(pipeline_router, prefix="/api/v1")

@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "Pipeline de Análisis Inteligente funcionando",
        "version": settings.APP_VERSION
    }