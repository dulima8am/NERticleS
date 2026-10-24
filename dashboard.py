import streamlit as st
import requests
import sqlite3
import pandas as pd
import time
import uuid
import json
from bs4 import BeautifulSoup

# Configuración de la página
st.set_page_config(page_title="NERticleS Dashboard", page_icon="📰", layout="wide")

st.title("📰 NERticleS - Dashboard de Análisis Inteligente")
st.markdown("Panel de control para el pipeline de análisis de artículos con LLMs.")

# Configuración de la API
API_URL = "http://localhost:8000/api/v1"

# --- FUNCIÓN DE SCRAPING ---
def extract_article_data(url):
    """Extrae el título y el contenido de una URL."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extraer título
        title = soup.title.string if soup.title else "Sin título"
        
        # Extraer contenido (párrafos)
        paragraphs = soup.find_all('p')
        content = " ".join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 20])
        
        if len(content) < 100:
            content = soup.get_text(separator=' ', strip=True)
            
        return title, content
    except Exception as e:
        return None, str(e)

# --- BARRA LATERAL: Autenticación ---
st.sidebar.header("🔐 Autenticación")
if "token" not in st.session_state:
    st.session_state.token = None

if st.session_state.token is None:
    if st.sidebar.button("Hacer Login"):
        try:
            response = requests.post(f"{API_URL}/auth/login")
            if response.status_code == 200:
                st.session_state.token = response.json()["access_token"]
                st.sidebar.success("✅ Login exitoso")
                st.rerun()
            else:
                st.sidebar.error("❌ Error en login")
        except Exception as e:
            st.sidebar.error(f"Error de conexión: {e}")
else:
    st.sidebar.success("✅ Autenticado como admin_user")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.token = None
        st.rerun()

st.sidebar.divider()

# --- BARRA LATERAL: Enviar Artículo ---
st.sidebar.header("📥 Analizar Nueva URL")
with st.sidebar.form("url_form"):
    art_url = st.text_input("Ingresa la URL del artículo", placeholder="https://www.semana.com/...")
    submitted = st.form_submit_button("Extraer y Enviar al Pipeline")
    
    if submitted:
        if st.session_state.token is None:
            st.error("Debes hacer login primero.")
        elif not art_url.startswith("http"):
            st.error("Por favor, ingresa una URL válida.")
        else:
            # 1. Extraemos el título (esto es rápido)
            with st.spinner("Extrayendo contenido..."):
                title, content_or_error = extract_article_data(art_url)
            
            if title is None:
                st.error(f"❌ Error al extraer: {content_or_error}")
            else:
                art_id = f"art-{uuid.uuid4().hex[:8]}"
                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                payload = {
                    "id": art_id,
                    "url": art_url,
                    "title": title,
                    "content": f"<p>{content_or_error}</p>"
                }
                
                # 2. Enviamos al backend (esto es rápido porque usa BackgroundTasks)
                try:
                    response = requests.post(f"{API_URL}/webhook/articles", json=payload, headers=headers)
                    if response.status_code == 202:
                        # 3. Refrescamos INMEDIATAMENTE para que aparezca en la tabla
                        st.success(f"✅ '{title[:30]}...' en cola de procesamiento.")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error(f"Error del servidor: {response.status_code}")
                except Exception as e:
                    st.error(f"Error de conexión: {e}")

# --- ÁREA PRINCIPAL: Visualización en Vivo ---
st.header("📊 Resultados del Pipeline (Actualización en vivo)")

# Contenedor para actualización automática
placeholder = st.empty()

with placeholder.container():
    try:
        conn = sqlite3.connect("pipeline.db")
        # Ordenar por fecha descendente (más reciente primero)
        df = pd.read_sql_query("SELECT * FROM articles_processed ORDER BY processed_at DESC", conn)
        conn.close()
        
        if df.empty:
            st.info("Aún no hay artículos procesados. Usa el panel izquierdo para enviar una URL.")
        else:
            # Métricas
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Artículos", len(df))
            
            df_procesados = df[df['status'] == 'Procesado']
            sentimiento_comun = df_procesados['sentimiento'].mode()[0] if not df_procesados.empty else "N/A"
            col2.metric("Sentimiento Predominante", sentimiento_comun)
            
            proveedor_comun = df_procesados['provider'].mode()[0] if not df_procesados.empty else "N/A"
            col3.metric("Proveedor Principal", proveedor_comun)
            
            st.divider()
            
            # Tabla (SIN el resumen)
            st.subheader("📋 Artículos Recientes (Haz clic en una fila para ver el resumen)")
            
            def parse_entities(x):
                try:
                    if x and x != "[]":
                        return ", ".join(json.loads(x))
                    return ""
                except:
                    return ""
            
            df['entidades_str'] = df['entidades'].apply(parse_entities)
            
            # Seleccionamos las columnas SIN el resumen_seo
            df_display = df[['id', 'title', 'status', 'provider', 'sentimiento', 'entidades_str']].copy()
            df_display.columns = ['ID', 'Título', 'Estado', 'Proveedor', 'Sentimiento', 'Entidades']
            
            # Mostrar tabla interactiva
            selection = st.dataframe(
                df_display, 
                use_container_width=True, 
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row"
            )
            
            # --- LÓGICA DE SELECCIÓN ---
            st.divider()
            if len(selection.selection.rows) > 0:
                selected_index = selection.selection.rows[0]
                selected_id = df_display.iloc[selected_index]['ID']
                row_data = df[df['id'] == selected_id].iloc[0]
                
                st.subheader(f"📝 Detalle del Artículo: {row_data['title']}")
                
                # Mostrar resumen SEO en un párrafo bonito
                st.info(f"**Resumen SEO:** {row_data['resumen_seo']}")
                
                # Mostrar el enlace original
                st.markdown(f"🔗 [Ver artículo original]({row_data['url']})")
                
                # Mostrar entidades en formato JSON crudo (por si acaso)
                with st.expander("Ver datos técnicos (JSON de entidades)"):
                    st.json(row_data['entidades'])
            else:
                st.info("👆 Selecciona una fila de la tabla para ver el resumen SEO del artículo.")
            
    except Exception as e:
        st.error(f"Error al leer la base de datos: {e}")

# Pausa de 3 segundos y recarga automática para simular "tiempo real"
time.sleep(3)
st.rerun()