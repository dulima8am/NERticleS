from app.models.schemas import ArticleIngestSchema

def validate_article(article: ArticleIngestSchema) -> bool:
    """
    Etapa 02: Validar reglas de negocio.
    Pydantic ya validó el esquema básico. Aquí validamos la calidad del contenido.
    """
    # Regla 1: El contenido debe tener al menos 50 palabras
    if len(article.content.split()) < 50:
        print(f"[Etapa 02] ❌ Artículo {article.id} rechazado: Muy corto (menos de 50 palabras).")
        return False
        
    # Regla 2: Evitar artículos de prueba o spam
    palabras_prohibidas = ["lorem ipsum", "test article", "prueba de texto"]
    if any(palabra in article.content.lower() for palabra in palabras_prohibidas):
        print(f"[Etapa 02] ❌ Artículo {article.id} rechazado: Contenido de prueba detectado.")
        return False

    print(f"[Etapa 02] ✅ Artículo {article.id} validado correctamente.")
    return True