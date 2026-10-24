import streamlit as st
import requests
import sqlite3
import pandas as pd
import time

# Configuración de la página
st.set_page_config(page_title="NERticleS Dashboard", page_icon="📰", layout="wide")

# Título
st.title("📰 NERticleS - Dashboard de Análisis Inteligente")
st.markdown("Panel de control para el pipeline de análisis de artículos con LLMs.")

# Configuración de la API
API_URL = "http://localhost:8000/api/v1"

# --- BARRA LATERAL: Autenticación y Envío ---
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

# --- BARRA LATERAL: Enviar Artículo ---
st.sidebar.header("📥 Enviar Nuevo Artículo")
with st.sidebar.form("article_form"):
    art_id = st.text_input("ID del artículo", value=f"art-{int(time.time())}")
    art_title = st.text_input("Título", value="Noticia de prueba")
    art_url = st.text_input("URL", value="https://ejemplo.com")
    art_content = st.text_area("Contenido", height=150, value="<p>Este es un artículo de prueba con más de cincuenta palabras para que el pipeline lo procese correctamente. La economía de Colombia creció un 2.5% en el último trimestre, impulsada por el sector agrícola y la recuperación del consumo interno. Según el DANE, este resultado superó las expectativas de los analistas, quienes esperaban un crecimiento moderado debido a la inflación persistente.</p>")
    
    submitted = st.form_submit_button("Enviar al Pipeline")
    
    if submitted:
        if st.session_state.token is None:
            st.error("Debes hacer login primero.")
        else:
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            payload = {
                "id": art_id,
                "url": art_url,
                "title": art_title,
                "content": art_content
            }
            try:
                response = requests.post(f"{API_URL}/webhook/articles", json=payload, headers=headers)
                if response.status_code == 202:
                    st.success(f"✅ Artículo enviado. Procesando en background...")
                    time.sleep(2) # Esperar un poco para que el LLM procese
                    st.rerun() # Recargar para ver los nuevos datos
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Error de conexión: {e}")

# --- ÁREA PRINCIPAL: Visualización de Datos ---
st.header("📊 Resultados del Pipeline")

try:
    # Conectar a la base de datos SQLite
    conn = sqlite3.connect("pipeline.db")
    
    # Leer los datos
    df = pd.read_sql_query("SELECT * FROM articles_processed ORDER BY processed_at DESC", conn)
    conn.close()
    
    if df.empty:
        st.info("Aún no hay artículos procesados. Usa el panel izquierdo para enviar uno.")
    else:
        # Mostrar métricas principales
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Artículos", len(df))
        col2.metric("Sentimiento Predominante", df['sentimiento'].mode()[0] if not df.empty else "N/A")
        col3.metric("Proveedor Principal", df['provider'].mode()[0] if not df.empty else "N/A")
        
        st.divider()
        
        # Mostrar tabla de datos
        st.subheader("📋 Artículos Recientes")
        
        # Renombrar columnas para que se vean más bonitas
        df_display = df[['id', 'title', 'provider', 'sentimiento', 'resumen_seo', 'processed_at']].copy()
        df_display.columns = ['ID', 'Título', 'Proveedor', 'Sentimiento', 'Resumen SEO', 'Fecha de Procesamiento']
        
        st.dataframe(df_display, use_container_width=True)
        
        # Detalle de entidades (opcional)
        st.subheader("🔍 Detalle de Entidades Extraídas")
        selected_id = st.selectbox("Selecciona un artículo para ver sus entidades:", df['id'].tolist())
        if selected_id:
            selected_row = df[df['id'] == selected_id].iloc[0]
            st.json(selected_row['entidades'])

except Exception as e:
    st.error(f"Error al leer la base de datos: {e}")