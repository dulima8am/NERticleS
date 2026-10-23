import re
import html

from app.utils.observability import observe_stage

@observe_stage("etapa_03_limpieza")

def clean_text(raw_text: str) -> str:
    """
    Etapa 03: Limpiar el texto.
    Elimina HTML, saltos de línea múltiples, espacios extra y decodifica entidades.
    """
    print("[Etapa 03] 🧹 Limpiando texto...")
    
    # 1. Decodificar entidades HTML (ej. &amp; -> &)
    text = html.unescape(raw_text)
    
    # 2. Eliminar etiquetas HTML (ej. <p>, <br>, <div>)
    text = re.sub(r'<[^>]+>', '', text)
    
    # 3. Reemplazar saltos de línea y tabulaciones múltiples por un solo espacio
    text = re.sub(r'\s+', ' ', text)
    
    # 4. Eliminar espacios en blanco al principio y al final
    text = text.strip()
    
    print(f"[Etapa 03] ✅ Texto limpio. Longitud original: {len(raw_text)}, Longitud nueva: {len(text)}")
    return text