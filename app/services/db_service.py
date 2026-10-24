import json
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Float, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# Configuración de SQLAlchemy
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ArticleProcessed(Base):
    __tablename__ = "articles_processed"

    id = Column(String, primary_key=True, index=True)
    url = Column(String, nullable=True)
    title = Column(String, nullable=True)
    provider = Column(String, nullable=True)
    cost = Column(Float, default=0.0)
    entidades = Column(Text, nullable=True)
    sentimiento = Column(String, nullable=True)
    resumen_seo = Column(Text, nullable=True)
    status = Column(String, default="Procesando")
    processed_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    """Crea las tablas si no existen."""
    Base.metadata.create_all(bind=engine)


def save_article(article_id: str, article_data: dict, analysis_result: dict = None, status: str = "Procesando") -> bool:
    db = SessionLocal()
    try:
        data = analysis_result.get("result", {}) if analysis_result else {}
        
        resumen = data.get("resumen_seo", "")
        if len(resumen) > 160:
            resumen = resumen[:157] + "..."
        
        existing = db.query(ArticleProcessed).filter(ArticleProcessed.id == article_id).first()
        
        if existing:
            # Si ya existe, actualizamos los datos (Fin del pipeline)
            if analysis_result:
                existing.provider = analysis_result.get("provider")
                existing.cost = analysis_result.get("cost", 0.0)
                existing.entidades = json.dumps(data.get("entidades", []))
                existing.sentimiento = data.get("sentimiento", "Neutral")
                existing.resumen_seo = resumen
                existing.status = "Procesado"
                existing.processed_at = datetime.utcnow()
        else:
            # Si no existe, lo creamos (Inicio del pipeline)
            new_article = ArticleProcessed(
                id=article_id,
                url=str(article_data.get("url", "")),
                title=article_data.get("title", ""),
                provider=analysis_result.get("provider", "Pendiente") if analysis_result else "Pendiente",
                cost=analysis_result.get("cost", 0.0) if analysis_result else 0.0,
                entidades=json.dumps(data.get("entidades", [])) if analysis_result else "[]",
                sentimiento=data.get("sentimiento", "En análisis") if analysis_result else "En análisis",
                resumen_seo=resumen,
                status=status,
                processed_at=datetime.utcnow()
            )
            db.add(new_article)
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"[DB Service] ❌ Error guardando artículo: {e}")
        return False
    finally:
        db.close()

def get_all_articles():
    """Obtiene todos los artículos procesados (útil para el dashboard)."""
    db = SessionLocal()
    try:
        articles = db.query(ArticleProcessed).all()
        return articles
    finally:
        db.close()