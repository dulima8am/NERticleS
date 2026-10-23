from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.models.schemas import ArticleIngestSchema
from app.pipeline import stage_02_validate

router = APIRouter()

@router.post("/webhook/articles")
async def ingest_article(article: ArticleIngestSchema, background_tasks: BackgroundTasks):
    """
    Etapa 01: Ingest
    Recibe el artículo y lo manda a procesar en background.
    """
    # Aquí lanzamos todo el pipeline en segundo plano
    # background_tasks.add_task(process_pipeline, article)
    
    # Simulamos una validación rápida antes de enviar a background
    if not article.content:
        raise HTTPException(status_code=400, detail="El artículo no tiene contenido")
        
    return {
        "status": "accepted",
        "message": "Artículo recibido. Procesando en background.",
        "article_id": article.id
    }