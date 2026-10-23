from fastapi import APIRouter, BackgroundTasks, status
from app.models.schemas import ArticleIngestSchema
from app.pipeline.orchestrator import run_pipeline

router = APIRouter()

@router.post("/webhook/articles", status_code=status.HTTP_202_ACCEPTED)
async def ingest_article(article: ArticleIngestSchema, background_tasks: BackgroundTasks):
    """
    Etapa 01: Ingest
    Recibe el artículo, responde de inmediato y procesa en background.
    """
    print(f"[Etapa 01] 📥 Recibido artículo: {article.title}")
    
    # Lanzamos todo el pipeline en segundo plano
    background_tasks.add_task(run_pipeline, article)
    
    return {
        "status": "accepted",
        "message": "Artículo recibido. Procesando en background.",
        "article_id": article.id
    }