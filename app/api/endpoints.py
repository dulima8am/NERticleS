from fastapi import APIRouter, BackgroundTasks, status, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.models.schemas import ArticleIngestSchema
from app.pipeline.orchestrator import run_pipeline
from app.core.config import settings
import jwt
from datetime import datetime, timedelta, timezone

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
security = HTTPBearer()

# Clave secreta para firmar los JWT (idealmente debe venir del .env)
JWT_SECRET = getattr(settings, "JWT_SECRET", "super_secret_key_bsg_2026")
JWT_ALGORITHM = "HS256"


# ==========================================
# ENDPOINT DE AUTENTICACIÓN (Generar Token)
# ==========================================
@router.post("/auth/login", tags=["Auth"])
def login():
    """
    Endpoint simulado de login.
    En un entorno real, aquí validarías el usuario y contraseña contra una base de datos.
    """
    payload = {
        "sub": "admin_user",
        "role": "admin",
        "exp": datetime.now(timezone.utc) + timedelta(hours=2)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}


# ==========================================
# DEPENDENCIA: Validar Token JWT
# ==========================================
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verifica que el token JWT sea válido y no haya expirado.
    """
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado. Vuelve a hacer login.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido.")


# ==========================================
# WEBHOOK PRINCIPAL (Etapa 01 + Seguridad)
# ==========================================
@router.post("/webhook/articles", status_code=status.HTTP_202_ACCEPTED, tags=["Pipeline"])
@limiter.limit("10/minute")
async def ingest_article(
    request: Request,  # Requerido por slowapi para el rate limiting
    article: ArticleIngestSchema,
    background_tasks: BackgroundTasks,
    token_data: dict = Depends(verify_token)  # Protegido con JWT
):
    """
    Etapa 01: Ingest
    Recibe el artículo, valida el token, responde de inmediato y procesa en background.
    """
    user_id = token_data.get("sub", "unknown")
    print(f"[Etapa 01] 📥 Recibido artículo de '{user_id}': {article.title}")
    
    # Lanzamos el pipeline completo en segundo plano
    background_tasks.add_task(run_pipeline, article)
    
    return {
        "status": "accepted",
        "message": "Artículo recibido. Procesando en background.",
        "article_id": article.id,
        "requested_by": user_id
    }