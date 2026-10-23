import vertexai

#vertexai.init(project="llm-api-bsg", location="us-central1")
#print("Vertex AI initialized")

import asyncio
from app.services.llm_service import llm_service

async def test_llm():
    texto_prueba = "La economía de Colombia creció un 2.5% en el último trimestre, impulsada por el sector agrícola. Sin embargo, el desempleo sigue siendo un desafío."
    print("Iniciando prueba de LLM...")
    resultado = await llm_service.analyze_text(texto_prueba)
    print("\n--- RESULTADO ---")
    print(f"Proveedor usado: {resultado['provider']}")
    print(f"Costo estimado: ${resultado['cost']}")
    print(f"Respuesta:\n{resultado['result']}")

if __name__ == "__main__":
    asyncio.run(test_llm())