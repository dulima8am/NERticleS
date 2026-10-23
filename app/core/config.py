from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Configuración central de la aplicación.
    Lee las variables del archivo .env automáticamente.
    """
    # API Keys
    GEMINI_API_KEY: str = ""
    
    # Configuración de la base de datos
    SQLITE_DB_PATH: str = "pipeline.db"
    DATABASE_URL: str = "sqlite:///./pipeline.db"  # Para producción sería postgresql://...
    
    # Configuración de Ollama (Fallback)
    OLLAMA_URL: str = "http://localhost:11434/api/generate"
    OLLAMA_MODEL: str = "llama3:8b"
    
    # Umbral de costo para activar el fallback
    COST_THRESHOLD: float = 0.002
    
    # Configuración del modelo principal
    GEMINI_MODEL: str = "gemini-3.8-flash"
    
    # Configuración de la app
    APP_NAME: str = "NERticleS - Pipeline de Análisis Inteligente"
    APP_VERSION: str = "1.0.0"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Ignora variables extra que no estén definidas aquí
    )

# Instancia global de configuración
settings = Settings()