import os
from dotenv import load_dotenv
from google import genai
import httpx

# Cargar variables de entorno al inicio del módulo
load_dotenv()

class LLMService:
    def __init__(self):
        # Configuración de Google AI Studio (Gemini API)
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Falta la variable de entorno GEMINI_API_KEY")
        self.ai_studio_client = genai.Client(api_key=api_key)
        
        # Configuración de Ollama (Local Fallback)
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3:8b")
        
        # Umbral de costo (simulado)
        self.cost_threshold = float(os.getenv("COST_THRESHOLD", "0.002"))

    async def analyze_text(self, text: str) -> dict:
        """
        Analiza el texto usando Google AI Studio. Si falla o excede el umbral,
        hace fallback a Ollama.
        """
        try:
            print("[LLM Service] 🔵 Intentando con Google AI Studio (Gemini)...")
            
            prompt = f"Analiza el siguiente texto periodístico y extrae: 1) Entidades principales (NER), 2) Sentimiento general (Positivo/Negativo/Neutral), 3) Un resumen SEO de máximo 160 caracteres.\n\nTexto: {text}"
            
            # Llamada a AI Studio
            response = self.ai_studio_client.models.generate_content(
                model='gemini-3.8-flash',
                contents=prompt
            )
            
            # Cálculo de costo simulado
            estimated_cost = 0.0001 
            
            if estimated_cost > self.cost_threshold:
                print(f"[LLM Service] ⚠️ Costo estimado supera el umbral. Forzando Fallback a Ollama...")
                return await self._fallback_to_ollama(text)
            
            return {
                "provider": "google_ai_studio",
                "cost": estimated_cost,
                "result": response.text
            }

        except Exception as e:
            print(f"[LLM Service] ❌ Error con AI Studio: {e}. Iniciando Fallback a Ollama...")
            return await self._fallback_to_ollama(text)

    async def _fallback_to_ollama(self, text: str) -> dict:
        """
        Método privado para conectar con Ollama local.
        (Este método se mantiene exactamente igual que antes)
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
                response = await client.post(self.ollama_url, json=payload, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                
                return {
                    "provider": "ollama_local",
                    "cost": 0.0,
                    "result": data.get("response", "")
                }
        except Exception as e:
            return {
                "provider": "error",
                "cost": 0.0,
                "result": f"Error crítico: AI Studio falló y Ollama no está disponible. Detalle: {e}"
            }

# Instancia global para usarla en el pipeline
llm_service = LLMService()
