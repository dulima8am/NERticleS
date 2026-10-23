import asyncio
from dotenv import load_dotenv
load_dotenv()

from app.models.schemas import ArticleIngestSchema
from app.pipeline.stage_02_validate import validate_article
from app.pipeline.stage_03_clean import clean_text
from app.pipeline.stage_04_05_analyze_enrich import analyze_and_enrich

async def test_full_pipeline():
    # 1. Simulamos el JSON que llegaría por el webhook
    raw_article = ArticleIngestSchema(
        id="art-999",
        url="https://ejemplo.com/noticia",
        title="Crecimiento económico en Colombia",
        content="<p>La economía de <b>Colombia</b> creció un 2.5% en el último trimestre, impulsada por el sector agrícola. Sin embargo, el desempleo sigue siendo un desafío para el país.</p>"
    )
    
    print("--- 🚀 Iniciando Prueba del Pipeline Completo ---")
    
    # Etapa 02: Validar
    if not validate_article(raw_article):
        print("Pipeline detenido en Etapa 02.")
        return
        
    # Etapa 03: Limpiar
    cleaned_text = clean_text(raw_article.content)
    
    # Etapa 04/05: Analizar con LLM
    analysis = await analyze_and_enrich(cleaned_text)
    
    print("\n--- ✅ RESULTADO FINAL (JSON) ---")
    print(f"Proveedor: {analysis['provider']}")
    print(f"Data: {analysis['result']}")

if __name__ == "__main__":
    asyncio.run(test_full_pipeline())