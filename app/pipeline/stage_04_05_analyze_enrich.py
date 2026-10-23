from app.services.llm_service import llm_service
from app.utils.observability import observe_stage

@observe_stage("etapa_04_05_analisis_llm")

async def analyze_and_enrich(cleaned_text: str) -> dict:
    """
    Etapas 04 y 05: Analizar con LLM y enriquecer (NER + Sentimiento).
    """
    print("[Etapa 04/05] 🧠 Analizando texto con el LLM...")
    
    result = await llm_service.analyze_text(cleaned_text)
    
    if result["provider"] == "error":
        print(f"[Etapa 04/05] ❌ Error en el análisis: {result['result'].get('error')}")
    else:
        print(f"[Etapa 04/05] ✅ Análisis completado usando: {result['provider']}")

    return result