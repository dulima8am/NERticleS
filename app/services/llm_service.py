import os
import vertexai
from vertexai.generative_models import GenerativeModel
import httpx

class LLMService:
    def __init__(self):
        # Configuración de Vertex AI (ya validada por ti)
        self.project_id = os.getenv("GCP_PROJECT_ID", "llm-api-bsg")
        self.location = os.getenv("GCP_LOCATION", "us-central1")
        
        # Inicializamos Vertex AI una sola vez
        vertexai.init(project=self.project_id, location=self.location)
        self.vertex_model = GenerativeModel("gemini-2.5-flash") # Usamos Flash por ser más barato/rápido
        
        # Configuración de Ollama (Local Fallback)
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3:8b")
        
        # Umbral de costo (simulado) para activar el fallback
        self.cost_threshold = float(os.getenv("COST_THRESHOLD", "0.002"))

    async def analyze_text(self, text: str) -> dict:
        """
        Analiza el texto usando Vertex AI. Si falla o excede el umbral de costo,
        hace fallback a Ollama.
        """
        # --- INTENTO 1: VERTEX AI ---
        try:
            print("[LLM Service] 🔵 Intentando con Vertex AI (Gemini)...")
            
            prompt = f"Analiza el siguiente texto periodístico y extrae: 1) Entidades principales (NER), 2) Sentimiento general (Positivo/Negativo/Neutral), 3) Un resumen SEO de máximo 160 caracteres.\n\nTexto: {text}"
            
            response = self.vertex_model.generate_content(prompt)
            
            # Cálculo de costo simulado (En un caso real, se obtiene de response.usage_metadata)
            # Gemini Flash es ~$0.000075 por 1k tokens de entrada.
            estimated_cost = 0.0001 
            
            if estimated_cost > self.cost_threshold:
                print(f"[LLM Service] ⚠️ Costo estimado (${estimated_cost}) supera el umbral (${self.cost_threshold}). Forzando Fallback a Ollama...")
                return await self._fallback_to_ollama(text)
            
            return {
                "provider": "vertex_ai",
                "cost": estimated_cost,
                "result": response.text
            }

        except Exception as e:
            print(f"[LLM Service] ❌ Error con Vertex AI: {e}. Iniciando Fallback a Ollama...")
            return await self._fallback_to_ollama(text)

    async def _fallback_to_ollama(self, text: str) -> dict:
        """
        Método privado para conectar con Ollama local.
        """
        print("[LLM Service] 🟢 Usando Ollama local como Fallback...")
        
        prompt = f"Analiza el siguiente texto y extrae: 1) Entidades, 2) Sentimiento, 3) Resumen SEO (max 160 chars).\n\nTexto: {text}"
        
        payload = {
            "model": self.ollama_model,
            "prompt": prompt,
            "stream": False
        }

        try:
            async with httpx.AsyncClient() as client:
                # Nota: Si esto corre en Cloud Run, localhost no funcionará. 
                # En producción, aquí apuntarías a una IP pública o un túnel (ngrok).
                response = await client.post(self.ollama_url, json=payload, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                
                return {
                    "provider": "ollama_local",
                    "cost": 0.0, # Ollama es gratis
                    "result": data.get("response", "")
                }
        except Exception as e:
            return {
                "provider": "error",
                "cost": 0.0,
                "result": f"Error crítico: Vertex AI falló y Ollama no está disponible. Detalle: {e}"
            }

# Instancia global para usarla en el pipeline
llm_service = LLMService()