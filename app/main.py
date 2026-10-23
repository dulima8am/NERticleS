from fastapi import FastAPI
from app.api.endpoints import router as pipeline_router

app = FastAPI(
    title="MediaGroup LLM Pipeline",
    description="Pipeline de Análisis Inteligente para Artículos",
    version="1.0.0"
)

# Registramos las rutas
app.include_router(pipeline_router, prefix="/api/v1")

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Pipeline funcionando"}