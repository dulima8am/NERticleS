from app.services.db_service import init_db, save_article

def finalize_and_export(article_id: str, article_data: dict, analysis_result: dict) -> bool:
    """
    Etapas 06 y 07: Validar resumen SEO y exportar a base de datos.
    """
    print("[Etapa 06/07] 💾 Guardando resultados y validando resumen SEO...")
    
    # Asegurar que las tablas existan
    init_db()
    
    # Guardar en la base de datos (la validación del resumen se hace dentro)
    success = save_article(article_id, article_data, analysis_result)
    
    if success:
        print(f"[Etapa 07] ✅ Artículo {article_id} exportado correctamente.")
    
    return success