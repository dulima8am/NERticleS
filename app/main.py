from contextlib import asynccontextmanager
from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.api.endpoints import router as pipeline_router
from app.services.db_service import init_db
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Ciclo de vida de la aplicación.
    Se ejecuta al arrancar y al detener el servidor.
    """
    print("[Main] 🚀 Iniciando aplicación...")
    init_db()
    print("[Main] ✅ Base de datos inicializada.")
    yield
    print("[Main] 🛑 Deteniendo aplicación...")

# Configurar Rate Limiting
limiter = Limiter(key_func=get_remote_address)

# Crear la aplicación
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Pipeline asíncrono de 7 etapas para el análisis automático de artículos periodísticos.",
    lifespan=lifespan
)

# Configurar Rate Limiting en la app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Registramos las rutas
app.include_router(pipeline_router, prefix="/api/v1")

@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "Pipeline de Análisis Inteligente funcionando",
        "version": settings.APP_VERSION
    }