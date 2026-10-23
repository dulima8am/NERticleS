import os
import json
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
        try:
            print("[LLM Service] 🔵 Intentando con Google AI Studio (Gemini)...")
            
            prompt = f"""
Analiza el siguiente texto periodístico y devuelve ÚNICAMENTE un objeto JSON válido.
NO uses markdown, NO uses bloques de código (```), NO agregues texto antes ni después.
La estructura exacta debe ser:
{{
  "entidades": ["entidad1", "entidad2"],
  "sentimiento": "Positivo" | "Negativo" | "Neutral",
  "resumen_seo": "Resumen de máximo 160 caracteres"
}}

Texto: {text}
"""
            
            # Llamada a AI Studio
            response = self.ai_studio_client.models.generate_content(
                model='gemini-3.8-flash',
                contents=prompt
            )
            
            # Cálculo de costo simulado
            estimated_cost = 0.0001
            
            if estimated_cost > self.cost_threshold:
                print("[LLM Service] ⚠️ Costo supera el umbral. Forzando Fallback a Ollama...")
                return await self._fallback_to_ollama(text)
            
            # Parseo seguro del JSON (por si Gemini devuelve ```json ... ```)
            raw_text = response.text.strip()
            if raw_text.startswith("```"):
                raw_text = raw_text.strip("`").replace("json\n", "", 1).strip()
            
            parsed_result = json.loads(raw_text)
            
            return {
                "provider": "google_ai_studio",
                "cost": estimated_cost,
                "result": parsed_result
            }

        except Exception as e:
            print(f"[LLM Service] ❌ Error con AI Studio: {e}. Iniciando Fallback a Ollama...")
            return await self._fallback_to_ollama(text)

    async def _fallback_to_ollama(self, text: str) -> dict:
        print("[LLM Service] 🟢 Usando Ollama local como Fallback...")
        
        prompt = f"""
Analiza el siguiente texto y devuelve ÚNICAMENTE un JSON válido con esta estructura:
{{"entidades": [], "sentimiento": "", "resumen_seo": ""}}
Texto: {text}
"""
        payload = {"model": self.ollama_model, "prompt": prompt, "stream": False}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.ollama_url, json=payload, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                
                raw_text = data.get("response", "").strip()
                if raw_text.startswith("```"):
                    raw_text = raw_text.strip("`").replace("json\n", "", 1).strip()
                
                return {
                    "provider": "ollama_local",
                    "cost": 0.0,
                    "result": json.loads(raw_text)
                }
        except Exception as e:
            return {
                "provider": "error",
                "cost": 0.0,
                "result": {"error": f"Fallo total: {e}"}
            }

llm_service = LLMService()