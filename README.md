# NERticleS - Pipeline de Análisis Inteligente

Pipeline asíncrono de 7 etapas para el análisis automático de artículos periodísticos (extracción de entidades, resúmenes SEO, clasificación por sentimiento), desarrollado para el Proyecto B del curso de Fundamentos de LLMs y APIs (BSG Institute).

```
NERticleS/
│
├── app/                        # Código fuente principal de la aplicación
│   ├── api/                    # Endpoints de FastAPI (Webhook, Auth)
│   ├── core/                   # Configuración central (Settings, Pydantic)
│   ├── models/                 # Esquemas de datos (Pydantic)
│   ├── pipeline/               # Lógica de las 7 etapas del pipeline
│   ├── services/               # Servicios externos (LLM, Base de Datos)
│   ├── utils/                  # Utilidades (Observabilidad, decoradores)
│   └── main.py                 # Punto de entrada de la aplicación
│
├── docs/                       # 📁 Carpeta de Entregables (PDFs, Diagramas)
│   ├── DiagramaDeArquitectura.png
│   ├── Documento de Diseño.pdf
│   ├── Análisis de Costos.xlsx
│   └── Reflexión Crítica del Proyecto NERticleS.pdf
│
├── scripts/                    # Scripts de prueba (testing.py)
│
├── .dockerignore               # Archivos ignorados por Docker
├── .gitignore                  # Archivos ignorados por Git
├── dashboard.py                # Frontend en Streamlit (E4)
├── Dockerfile                  # Configuración para despliegue en Cloud Run
├── LICENSE                     # Licencia MIT
├── README.md                   # Documentación del proyecto
└── requirements.txt            # Dependencias de Python
```

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

## 📂 Entregables del Proyecto

A continuación se listan los artefactos entregables desarrollados para el Proyecto B:

| Entregable | Descripción | Enlace |
| :--- | :--- | :--- |
| **E1 - Diagrama de Arquitectura** | Diagrama de componentes y flujos de datos. | [Ver Diagrama](./docs/E1_Diagrama_Arquitectura.png) |
| **E2 - Documento de Diseño** | RFC técnico con justificación de decisiones y costos. | [Ver Documento](./docs/E2_Documento_Diseño.pdf) |
| **E3 - Backend Funcional** | API REST desplegada en Cloud Run (ver instrucciones abajo). | [Código Fuente](./app) |
| **E4 - Frontend Funcional** | Dashboard interactivo en Streamlit. | [Ver Dashboard](./dashboard.py) |
| **E5 - Video de Presentación** | Demo funcional y explicación arquitectónica. | [Ver Video en Google Drive](https://drive.google.com/drive/folders/1S2zzhixt_1wUpZJS3PUjKB_KjMwDp175?usp=sharing) |
| **E6 - Análisis de Costos** | Estimación de costos comparativa entre modalidades. | [Ver Análisis](./docs/E6_Analisis_Costos.csv) |
| **E7 - Reflexión Crítica** | Análisis de qué funcionó, qué cambiarías y aprendizajes. | [Ver Reflexión](./docs/E7_Reflexion_Critica.pdf) |


## 🚀 Ejecución Local

Paso 1: Clonar el repositorio y crear un entorno virtual:
    python -m venv venv
    source venv/bin/activate

Paso 2: Instalar las dependencias (con el entorno virtual activado):
    pip install -r requirements.txt

Paso 3: Configurar las variables de entorno.
Crea un archivo llamado `.env` en la raíz del proyecto y agrega tu configuración:
    GEMINI_API_KEY="tu_api_key_aqui"
    GEMINI_MODEL="gemini-3.8-flash"
    OLLAMA_URL="http://localhost:11434/api/generate"
    OLLAMA_MODEL="llama3.2:3b"
    COST_THRESHOLD="0.002"

Paso 4: Levantar el servidor:
    uvicorn app.main:app --reload

Paso 5: Acceder a la documentación.
Abre tu navegador y visita la interfaz de Swagger UI en: `http://127.0.0.1:8000/docs`

## 🧪 Pruebas y Uso

Para probar el pipeline, envía una petición POST al webhook con la estructura de un artículo:

    {
      "id": "art-001",
      "url": "https://ejemplo.com/noticia",
      "title": "Título de la noticia",
      "content": "<p>Contenido del artículo con al menos 50 palabras para pasar la validación...</p>"
    }

El servidor responderá con un `202 Accepted` y los resultados se podrán consultar en la base de datos.

## ☁️ Despliegue en Cloud Run (GCP)

El proyecto incluye un `Dockerfile` optimizado para desplegarse en Google Cloud Run. Para hacerlo, asegúrate de tener configurado el `gcloud CLI` y ejecuta:

    gcloud run deploy nerticles-pipeline \
      --source . \
      --region us-central1 \
      --allow-unauthenticated \
      --set-env-vars="GEMINI_MODEL=gemini-3.8-flash,OLLAMA_URL=http://localhost:11434/api/generate,OLLAMA_MODEL=llama3.2:3b,COST_THRESHOLD=0.002"

*(Nota: En producción, la `GEMINI_API_KEY` debe configurarse a través de Google Secret Manager y no como una variable de entorno plana).*

---
*Proyecto desarrollado para el Programa Certified AI-LLM Integration Engineer - Curso de Fundamentos de LLMs y APIs (BSG Institute).*
