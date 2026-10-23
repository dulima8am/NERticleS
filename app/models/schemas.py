from pydantic import BaseModel, Field, HttpUrl
from typing import Optional

class ArticleIngestSchema(BaseModel):
    id: str = Field(..., description="ID único del artículo")
    url: HttpUrl = Field(..., description="URL del artículo original")
    title: str = Field(..., min_length=5)
    content: str = Field(..., min_length=50, description="Texto plano del artículo")
    author: Optional[str] = None