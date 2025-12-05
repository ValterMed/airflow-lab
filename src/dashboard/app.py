#!/usr/bin/env python3
"""
# ========================================================================================
# 📊 ECOMMERCE ANALYTICS DASHBOARD - STREAMLIT
# ========================================================================================
#
# PROPÓSITO:
# Dashboard interactivo para visualizar métricas y análisis de eventos de e-commerce
# almacenados en MongoDB desde Kafka.
#
# CARACTERÍSTICAS:
# 1. Métricas básicas: Conteo por tipo de evento
# 2. Análisis de segmentación de usuarios:
#    - Frecuencia de eventos
#    - Categorías de productos vistos
#    - Navegador utilizado
#    - Rangos de horario de compra
#
# TECNOLOGÍAS:
# - Streamlit: Framework para dashboards interactivos
# - Plotly: Gráficas interactivas
# - PyMongo: Conexión a MongoDB
# - Pandas: Manipulación de datos
# ========================================================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pymongo import MongoClient, errors
from datetime import datetime, timedelta
import os
from collections import Counter

# ========================================================================================
# 🎨 CONFIGURACIÓN DE PÁGINA
# ========================================================================================
st.set_page_config(
    page_title="E-commerce Analytics Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================================================================================
# 🔌 CONEXIÓN A MONGODB
# ========================================================================================
@st.cache_resource
def get_mongodb_connection():
    """
    Establece conexión con MongoDB.
    Usa cache para mantener la conexión entre reruns de Streamlit.
    """
    try:
        # Obtener configuración desde variables de entorno
        mongo_uri = os.getenv('MONGODB_URI', 'mongodb://admin:mongopass@mongodb:27017/')
        mongo_db = os.getenv('MONGODB_DB', 'kafka_events_db')

        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')

        db = client[mongo_db]
        collection = db['ecommerce']

        st.sidebar.success("✅ Connected to MongoDB")
        return collection

    except errors.ConnectionFailure as e:
        st.sidebar.error(f"❌ MongoDB connection failed: {e}")
        return None


# ========================================================================================
# 📊 OBTENCIÓN DE DATOS
# ========================================================================================
@st.cache_data(ttl=30)  # Cache por 30 segundos
def fetch_events(_collection, limit=10000):
    """
    Obtiene eventos de e-commerce desde MongoDB.

    Args:
        _collection: MongoDB collection (prefijo _ para evitar hashing)
        limit: Número máximo de eventos a cargar
    """
    if _collection is None:
        return pd.DataFrame()

    try:
        # Obtener eventos más recientes
        cursor = _collection.find().sort('timestamp', -1).limit(limit)
        events = list(cursor)

        if not events:
            return pd.DataFrame()

        df = pd.DataFrame(events)

        # Convertir timestamp a datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            df['date'] = df['timestamp'].dt.date

        return df

    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()


# ========================================================================================
# 📈 MÉTRICAS BÁSICAS
# ========================================================================================
def display_basic_metrics(df):
    """
    Muestra métricas básicas: conteo por tipo de evento
    """
    st.header("📊 Métricas Básicas")

    if df.empty:
        st.warning("No hay datos disponibles")
        return

    # Métricas en columnas
    col1, col2, col3, col4 = st.columns(4)

    total_events = len(df)
    unique_users = df['user_id'].nunique() if 'user_id' in df.columns else 0
    unique_sessions = df['session_id'].nunique() if 'session_id' in df.columns else 0

    # Calcular revenue total si hay compras
    total_revenue = 0
    if 'total_amount' in df.columns:
        purchases = df[df['event_type'] == 'purchase']
        total_revenue = purchases['total_amount'].sum()

    col1.metric("Total Eventos", f"{total_events:,}")
    col2.metric("Usuarios Únicos", f"{unique_users:,}")
    col3.metric("Sesiones", f"{unique_sessions:,}")
    col4.metric("Revenue Total", f"${total_revenue:,.2f}")

    # Gráfica de conteo por tipo de evento
    st.subheader("Distribución de Eventos por Tipo")

    event_counts = df['event_type'].value_counts().reset_index()
    event_counts.columns = ['event_type', 'count']

    fig = px.bar(
        event_counts,
        x='event_type',
        y='count',
        title='Conteo de Eventos por Tipo',
        labels={'event_type': 'Tipo de Evento', 'count': 'Cantidad'},
        color='count',
        color_continuous_scale='Blues'
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Tabla con detalles
    st.subheader("Detalle por Tipo de Evento")
    st.dataframe(event_counts, use_container_width=True)


# ========================================================================================
# 👥 ANÁLISIS DE SEGMENTACIÓN DE USUARIOS
# ========================================================================================
def display_user_segmentation(df):
    """
    Análisis de segmentación de usuarios basado en:
    - Frecuencia de eventos
    - Categorías de productos vistos
    - Navegador utilizado
    - Rangos de horario de compra
    """
    st.header("👥 Análisis de Segmentación de Usuarios")

    if df.empty:
        st.warning("No hay datos disponibles")
        return

    # ================================================================================
    # 1. SEGMENTACIÓN POR FRECUENCIA DE EVENTOS
    # ================================================================================
    st.subheader("1️⃣ Segmentación por Frecuencia de Eventos")

    user_frequency = df.groupby('user_id').size().reset_index(name='event_count')

    # Clasificar usuarios por frecuencia
    def classify_frequency(count):
        if count >= 20:
            return 'Alto (20+)'
        elif count >= 10:
            return 'Medio (10-19)'
        else:
            return 'Bajo (1-9)'

    user_frequency['segment'] = user_frequency['event_count'].apply(classify_frequency)

    segment_counts = user_frequency['segment'].value_counts().reset_index()
    segment_counts.columns = ['segment', 'users']

    col1, col2 = st.columns(2)

    with col1:
        fig = px.pie(
            segment_counts,
            values='users',
            names='segment',
            title='Distribución de Usuarios por Frecuencia',
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.histogram(
            user_frequency,
            x='event_count',
            nbins=30,
            title='Histograma de Frecuencia de Eventos por Usuario',
            labels={'event_count': 'Número de Eventos'}
        )
        st.plotly_chart(fig, use_container_width=True)

    # ================================================================================
    # 2. SEGMENTACIÓN POR CATEGORÍA DE PRODUCTOS VISTOS
    # ================================================================================
    st.subheader("2️⃣ Segmentación por Categoría de Productos")

    if 'product_category' in df.columns:
        # Eventos con productos
        product_events = df[df['product_category'].notna()]

        if not product_events.empty:
            # Top categorías por usuario
            user_categories = product_events.groupby(['user_id', 'product_category']).size().reset_index(name='views')
            top_category_per_user = user_categories.loc[user_categories.groupby('user_id')['views'].idxmax()]

            category_distribution = top_category_per_user['product_category'].value_counts().reset_index()
            category_distribution.columns = ['category', 'users']

            col1, col2 = st.columns(2)

            with col1:
                fig = px.bar(
                    category_distribution,
                    x='category',
                    y='users',
                    title='Usuarios por Categoría Principal de Interés',
                    labels={'category': 'Categoría', 'users': 'Usuarios'},
                    color='users',
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Sunburst de categorías por evento
                category_event_counts = product_events.groupby(['product_category', 'event_type']).size().reset_index(name='count')

                fig = px.sunburst(
                    category_event_counts,
                    path=['product_category', 'event_type'],
                    values='count',
                    title='Interacciones por Categoría y Tipo de Evento'
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay eventos con categorías de productos disponibles")
    else:
        st.info("Campo 'product_category' no disponible en los datos")

    # ================================================================================
    # 3. SEGMENTACIÓN POR NAVEGADOR
    # ================================================================================
    st.subheader("3️⃣ Segmentación por Navegador")

    if 'user_agent' in df.columns:
        # Extraer tipo de dispositivo del user agent
        def extract_device_type(user_agent):
            if pd.isna(user_agent):
                return 'Unknown'
            ua = str(user_agent).lower()
            if 'iphone' in ua or 'ipad' in ua:
                return 'iOS'
            elif 'android' in ua:
                return 'Android'
            elif 'windows' in ua:
                return 'Windows'
            elif 'mac' in ua or 'macintosh' in ua:
                return 'macOS'
            else:
                return 'Other'

        df['device_type'] = df['user_agent'].apply(extract_device_type)

        device_counts = df['device_type'].value_counts().reset_index()
        device_counts.columns = ['device', 'events']

        col1, col2 = st.columns(2)

        with col1:
            fig = px.pie(
                device_counts,
                values='events',
                names='device',
                title='Distribución de Eventos por Tipo de Dispositivo',
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Eventos por dispositivo y tipo
            device_event_type = df.groupby(['device_type', 'event_type']).size().reset_index(name='count')

            fig = px.bar(
                device_event_type,
                x='device_type',
                y='count',
                color='event_type',
                title='Tipos de Eventos por Dispositivo',
                labels={'device_type': 'Dispositivo', 'count': 'Eventos'},
                barmode='stack'
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Campo 'user_agent' no disponible en los datos")

    # ================================================================================
    # 4. SEGMENTACIÓN POR HORARIO DE COMPRA
    # ================================================================================
    st.subheader("4️⃣ Segmentación por Horario de Actividad")

    if 'hour' in df.columns:
        # Definir rangos horarios
        def classify_time_range(hour):
            if 6 <= hour < 12:
                return 'Mañana (6-12)'
            elif 12 <= hour < 18:
                return 'Tarde (12-18)'
            elif 18 <= hour < 24:
                return 'Noche (18-24)'
            else:
                return 'Madrugada (0-6)'

        df['time_range'] = df['hour'].apply(classify_time_range)

        col1, col2 = st.columns(2)

        with col1:
            # Distribución por rango horario
            time_range_counts = df['time_range'].value_counts().reset_index()
            time_range_counts.columns = ['time_range', 'events']

            # Ordenar correctamente
            order = ['Madrugada (0-6)', 'Mañana (6-12)', 'Tarde (12-18)', 'Noche (18-24)']
            time_range_counts['time_range'] = pd.Categorical(time_range_counts['time_range'], categories=order, ordered=True)
            time_range_counts = time_range_counts.sort_values('time_range')

            fig = px.bar(
                time_range_counts,
                x='time_range',
                y='events',
                title='Eventos por Rango Horario',
                labels={'time_range': 'Rango Horario', 'events': 'Eventos'},
                color='events',
                color_continuous_scale='thermal'
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Heatmap de eventos por hora
            hourly_events = df.groupby('hour').size().reset_index(name='count')

            fig = go.Figure(data=go.Scatter(
                x=hourly_events['hour'],
                y=hourly_events['count'],
                mode='lines+markers',
                line=dict(color='royalblue', width=3),
                marker=dict(size=8)
            ))
            fig.update_layout(
                title='Actividad por Hora del Día',
                xaxis_title='Hora',
                yaxis_title='Número de Eventos',
                xaxis=dict(tickmode='linear', tick0=0, dtick=1)
            )
            st.plotly_chart(fig, use_container_width=True)

        # Análisis de compras por horario
        if 'purchase' in df['event_type'].values:
            purchases = df[df['event_type'] == 'purchase']
            purchase_hours = purchases['hour'].value_counts().sort_index().reset_index()
            purchase_hours.columns = ['hour', 'purchases']

            fig = px.bar(
                purchase_hours,
                x='hour',
                y='purchases',
                title='Compras por Hora del Día',
                labels={'hour': 'Hora', 'purchases': 'Compras'},
                color='purchases',
                color_continuous_scale='Greens'
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Información de hora no disponible en los datos")


# ========================================================================================
# 🎯 MAIN APP
# ========================================================================================
def main():
    """Función principal de la aplicación"""

    # Título
    st.title("🛒 E-commerce Analytics Dashboard")
    st.markdown("---")

    # Sidebar
    st.sidebar.title("⚙️ Configuración")

    # Conexión a MongoDB
    collection = get_mongodb_connection()

    if collection is None:
        st.error("❌ No se pudo conectar a MongoDB. Verifica la configuración.")
        st.stop()

    # Controles
    st.sidebar.subheader("Opciones de Datos")

    limit = st.sidebar.slider(
        "Límite de eventos a cargar",
        min_value=100,
        max_value=50000,
        value=10000,
        step=100
    )

    auto_refresh = st.sidebar.checkbox("Auto-actualizar", value=False)

    if auto_refresh:
        refresh_interval = st.sidebar.slider(
            "Intervalo de actualización (segundos)",
            min_value=10,
            max_value=300,
            value=30,
            step=10
        )
        # Forzar rerun después del intervalo
        import time
        time.sleep(refresh_interval)
        st.rerun()

    # Botón manual de refresh
    if st.sidebar.button("🔄 Actualizar Datos"):
        st.cache_data.clear()
        st.rerun()

    # Información
    st.sidebar.markdown("---")
    st.sidebar.info(
        "📊 **Dashboard Info**\n\n"
        "Este dashboard muestra métricas y análisis en tiempo real "
        "de eventos de e-commerce capturados desde Kafka y almacenados en MongoDB."
    )

    # Cargar datos
    with st.spinner("Cargando datos desde MongoDB..."):
        df = fetch_events(collection, limit)

    if df.empty:
        st.warning("⚠️ No hay datos disponibles. Asegúrate de que el producer y consumer estén ejecutándose.")
        st.stop()

    # Mostrar información de datos
    st.sidebar.success(f"✅ {len(df)} eventos cargados")
    if 'timestamp' in df.columns:
        latest = df['timestamp'].max()
        st.sidebar.info(f"🕐 Último evento: {latest}")

    # Tabs para organizar el dashboard
    tab1, tab2, tab3 = st.tabs(["📊 Métricas Básicas", "👥 Segmentación de Usuarios", "📋 Datos Raw"])

    with tab1:
        display_basic_metrics(df)

    with tab2:
        display_user_segmentation(df)

    with tab3:
        st.header("📋 Datos Raw")
        st.dataframe(df, use_container_width=True)

        # Opción de descarga
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Descargar CSV",
            data=csv,
            file_name=f"ecommerce_events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )


if __name__ == "__main__":
    main()
