import streamlit as st
import requests
import sqlite3
import pandas as pd
import time
import uuid
from bs4 import BeautifulSoup
from urllib.parse import urlparse

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
        
        # Intentar extraer el título
        title = soup.title.string if soup.title else "Sin título"
        
        # Intentar extraer el contenido (buscando etiquetas <p>)
        paragraphs = soup.find_all('p')
        content = " ".join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 20])
        
        # Si no encontramos suficiente texto en <p>, usamos todo el body
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

# --- BARRA LATERAL: Enviar Artículo (Solo URL) ---
st.sidebar.header("📥 Analizar Nueva URL")
with st.sidebar.form("url_form"):
    art_url = st.text_input("Ingresa la URL del artículo", placeholder="https://www.semana.com/...")
    submitted = st.form_submit_button("Extraer y Enviar al Pipeline")
    
    if submitted:
        if st.session_state.token is None:
            st.error("Debes hacer login primero.")
        elif not art_url.startswith("http"):
            st.error("Por favor, ingresa una URL válida que empiece con http:// o https://")
        else:
            with st.spinner("Extrayendo contenido de la URL..."):
                title, content_or_error = extract_article_data(art_url)
                
                if title is None:
                    st.error(f"❌ Error al extraer el artículo: {content_or_error}")
                else:
                    # Generar ID único automáticamente
                    art_id = f"art-{uuid.uuid4().hex[:8]}"
                    
                    headers = {"Authorization": f"Bearer {st.session_state.token}"}
                    payload = {
                        "id": art_id,
                        "url": art_url,
                        "title": title,
                        "content": f"<p>{content_or_error}</p>"
                    }
                    
                    try:
                        response = requests.post(f"{API_URL}/webhook/articles", json=payload, headers=headers)
                        if response.status_code == 202:
                            st.success(f"✅ Artículo '{title[:30]}...' enviado. Procesando...")
                            time.sleep(3) # Esperar un poco para que el LLM procese
                            st.rerun()
                        else:
                            st.error(f"Error del servidor: {response.status_code} - {response.text}")
                    except Exception as e:
                        st.error(f"Error de conexión con el backend: {e}")

# --- ÁREA PRINCIPAL: Visualización de Datos ---
st.header("📊 Resultados del Pipeline")

try:
    # Conectar a la base de datos SQLite
    conn = sqlite3.connect("pipeline.db")
    
    # Leer los datos
    df = pd.read_sql_query("SELECT * FROM articles_processed ORDER BY processed_at DESC", conn)
    conn.close()
    
    if df.empty:
        st.info("Aún no hay artículos procesados. Usa el panel izquierdo para enviar una URL.")
    else:
        # Mostrar métricas principales
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Artículos", len(df))
        col2.metric("Sentimiento Predominante", df['sentimiento'].mode()[0] if not df.empty else "N/A")
        col3.metric("Proveedor Principal", df['provider'].mode()[0] if not df.empty else "N/A")
        
        st.divider()
        
        # Mostrar tabla de datos
        st.subheader("📋 Artículos Recientes")
        
        df_display = df[['id', 'title', 'provider', 'sentimiento', 'resumen_seo', 'processed_at']].copy()
        df_display.columns = ['ID', 'Título', 'Proveedor', 'Sentimiento', 'Resumen SEO', 'Fecha de Procesamiento']
        
        st.dataframe(df_display, use_container_width=True)
        
        # Detalle de entidades
        st.subheader("🔍 Detalle de Entidades Extraídas")
        selected_id = st.selectbox("Selecciona un artículo para ver sus entidades:", df['id'].tolist())
        if selected_id:
            selected_row = df[df['id'] == selected_id].iloc[0]
            st.json(selected_row['entidades'])

except Exception as e:
    st.error(f"Error al leer la base de datos: {e}")