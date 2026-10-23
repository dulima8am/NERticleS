import os
import json
import sqlite3
from datetime import datetime

DB_PATH = os.getenv("SQLITE_DB_PATH", "pipeline.db")

def init_db():
    """Crea la tabla si no existe."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles_processed (
            id TEXT PRIMARY KEY,
            url TEXT,
            title TEXT,
            provider TEXT,
            cost REAL,
            entidades TEXT,
            sentimiento TEXT,
            resumen_seo TEXT,
            processed_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def finalize_and_export(article_id: str, article_data: dict, analysis_result: dict) -> bool:
    """
    Etapas 06 y 07: Validar resumen SEO y exportar a base de datos.
    """
    print("[Etapa 06/07] 💾 Guardando resultados y validando resumen SEO...")
    
    data = analysis_result.get("result", {})
    
    # Etapa 06: Asegurar que el resumen SEO no pase de 160 caracteres
    resumen = data.get("resumen_seo", "")
    if len(resumen) > 160:
        resumen = resumen[:157] + "..."
        print("[Etapa 06] ⚠️ Resumen SEO truncado a 160 caracteres.")
    
    # Etapa 07: Guardar en SQLite
    try:
        init_db() # Asegura que la tabla exista
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO articles_processed 
            (id, url, title, provider, cost, entidades, sentimiento, resumen_seo, processed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            article_id,
            str(article_data.get("url", "")),
            article_data.get("title", ""),
            analysis_result.get("provider", "unknown"),
            analysis_result.get("cost", 0.0),
            json.dumps(data.get("entidades", [])),
            data.get("sentimiento", "Neutral"),
            resumen,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        print(f"[Etapa 07] ✅ Artículo {article_id} exportado a la base de datos.")
        return True
        
    except Exception as e:
        print(f"[Etapa 07] ❌ Error guardando en DB: {e}")
        return False