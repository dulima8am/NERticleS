from app.models.schemas import ArticleIngestSchema
from app.pipeline.stage_02_validate import validate_article
from app.pipeline.stage_03_clean import clean_text
from app.pipeline.stage_04_05_analyze_enrich import analyze_and_enrich
from app.pipeline.stage_06_07_finalize_export import finalize_and_export

async def run_pipeline(article: ArticleIngestSchema):
    """
    Orquestador principal: ejecuta todas las etapas del pipeline en orden.
    """
    print(f"\n--- 🚀 Iniciando pipeline completo para artículo {article.id} ---")
    
    # Etapa 02
    if not validate_article(article):
        print(f"--- 🛑 Pipeline detenido para {article.id} ---\n")
        return
    
    # Etapa 03
    cleaned_text = clean_text(article.content)
    
    # Etapa 04 y 05
    analysis = await analyze_and_enrich(cleaned_text)
    
    # Etapa 06 y 07
    if analysis["provider"] != "error":
        finalize_and_export(article.id, article.model_dump(), analysis)
    
    print(f"--- ✅ Pipeline finalizado para {article.id} ---\n")