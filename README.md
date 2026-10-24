# NERticleS
Pipeline LLM de Análisisi Inteligente de artículos (extraer entidades, generar resúmenes SEO y clasifique por categoría y sentimiento)
# NERticleS - Pipeline de Análisis Inteligente

Pipeline asíncrono de 7 etapas para el análisis automático de artículos periodísticos, desarrollado para el Proyecto B del curso de Fundamentos de LLMs y APIs (BSG Institute).

## 🏗️ Arquitectura del Pipeline

El sistema implementa un flujo secuencial de 7 etapas, diseñado para procesar artículos sin bloquear al cliente:

1. **Ingest:** Webhook FastAPI (`POST /api/v1/webhook/articles`) que responde en <200ms usando `BackgroundTasks`.
2. **Validate:** Validación de reglas de negocio (mínimo de palabras, filtro anti-spam).
3. **Clean:** Limpieza de HTML, entidades y normalización del texto.
4. **Analyze:** Procesamiento con LLM (Google AI Studio - Gemini).
5. **Enrich:** Extracción de entidades (NER) y análisis de sentimiento.
6. **Summarize:** Generación de resumen SEO (máximo 160 caracteres).
7. **Export:** Persistencia de resultados en base de datos (SQLAlchemy / SQLite).

## 🛡️ Características Técnicas (Diferenciadores)

*   **Procesamiento Asíncrono:** Uso de `BackgroundTasks` de FastAPI. El webhook responde inmediatamente (HTTP 202 Accepted) mientras el pipeline se ejecuta en segundo plano.
*   **Arquitectura Multi-Proveedor (Fallback):** El sistema intenta usar Gemini (Google AI Studio) como proveedor principal. Si el costo estimado supera el umbral configurado (`COST_THRESHOLD`) o si hay un fallo de conexión, el sistema hace un *fallback* automático a **Ollama (Llama 3.2)** corriendo en local.
*   **Observabilidad:** Logs estructurados por cada etapa del pipeline (pueden ser capturados por Cloud Logging en producción).
*   **Configuración Centralizada:** Uso de `pydantic-settings` para manejar variables de entorno de forma segura (sin exponer secretos en el código).

## 🔧 Stack Tecnológico

*   **Backend:** Python 3.12 + FastAPI
*   **LLM Principal:** Google AI Studio (Gemini)
*   **LLM Fallback:** Ollama (Llama 3.2)
*   **Base de Datos:** SQLAlchemy (SQLite para desarrollo, compatible con Cloud SQL/PostgreSQL).
*   **Despliegue:** Docker (preparado para Google Cloud Run).

## 🚀 Ejecución Local

1. Clonar el repositorio y crear un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate
