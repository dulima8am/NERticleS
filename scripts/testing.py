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
    content="""<p>La economía de <b>Colombia</b> creció un 2.5% en el último trimestre, impulsada por el sector agrícola y la recuperación del consumo interno. Según el DANE, este resultado superó las expectativas de los analistas, quienes esperaban un crecimiento moderado debido a la inflación persistente. Sin embargo, el desempleo sigue siendo un desafío importante para el país, especialmente entre los jóvenes y las mujeres. El gobierno ha anunciado nuevas medidas para fomentar la creación de empleo formal y apoyar a las pequeñas y medianas empresas. Los expertos señalan que, aunque el panorama es alentador, aún queda trabajo por hacer para consolidar una recuperación económica sostenible e inclusiva.</p>"""
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