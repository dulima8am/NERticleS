import json
import httpx
from google import genai
from app.core.config import settings


class LLMService:
    def __init__(self):
        # Validar que la API key exista al arrancar
        if not settings.GEMINI_API_KEY:
            raise ValueError("Falta la variable de entorno GEMINI_API_KEY en el archivo .env")

        # Cliente de Google AI Studio
        self.ai_studio_client = genai.Client(api_key=settings.GEMINI_API_KEY)

        # Configuración del modelo principal (viene de config.py)
        self.gemini_model = settings.GEMINI_MODEL

        # Configuración del Fallback (Ollama)
        self.ollama_url = settings.OLLAMA_URL
        self.ollama_model = settings.OLLAMA_MODEL

        # Umbral de costo para activar el fallback
        self.cost_threshold = settings.COST_THRESHOLD

    async def analyze_text(self, text: str) -> dict:
        """
        Analiza el texto usando Google AI Studio (Gemini).
        Si falla o excede el umbral de costo, hace fallback a Ollama.
        """
        try:
            print("[LLM Service] 🔵 Intentando con Google AI Studio (Gemini)...")

            prompt = f"""
Analiza el siguiente texto periodístico y devuelve ÚNICAMENTE un objeto JSON válido.
NO uses markdown, NO uses bloques de código, NO agregues texto antes ni después.
La estructura exacta debe ser:
{{
  "entidades": ["entidad1", "entidad2"],
  "sentimiento": "Positivo" | "Negativo" | "Neutral",
  "resumen_seo": "Resumen de máximo 160 caracteres"
}}

Texto: {text}
"""

            response = self.ai_studio_client.models.generate_content(
                model=self.gemini_model,
                contents=prompt
            )

            estimated_cost = 0.0001

            if estimated_cost > self.cost_threshold:
                print(f"[LLM Service] ⚠️ Costo estimado (${estimated_cost}) supera el umbral (${self.cost_threshold}). Forzando Fallback a Ollama...")
                return await self._fallback_to_ollama(text)

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
        """
        Método privado para conectar con Ollama local como respaldo.
        """
        print("[LLM Service] 🟢 Usando Ollama local como Fallback...")

        prompt = f"""You are a JSON generator. Respond ONLY with a valid JSON object. No explanations, no markdown, no code blocks.

The JSON must have exactly these keys:
- "entidades": a list of strings (named entities found in the text)
- "sentimiento": one of "Positivo", "Negativo", or "Neutral"
- "resumen_seo": a string summary in Spanish, maximum 160 characters

Text to analyze:
{text}

JSON response:"""

        payload = {
            "model": self.ollama_model,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.ollama_url, json=payload, timeout=60.0)
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
                "result": {"error": f"Fallo total: AI Studio y Ollama no disponibles. Detalle: {e}"}
            }


# Instancia global para usarla en el pipeline
llm_service = LLMService()