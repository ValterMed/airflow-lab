# ========================================================================================
# 📊 DOCKERFILE - STREAMLIT DASHBOARD FOR ECOMMERCE ANALYTICS
# ========================================================================================
# Este Dockerfile construye una imagen para el dashboard de visualización
# de eventos de e-commerce usando Streamlit
# ========================================================================================

FROM python:3.11-slim

# Metadata
LABEL maintainer="Data Science Lab"
LABEL description="E-commerce Analytics Dashboard with Streamlit"

# Configurar working directory
WORKDIR /app

# Instalar dependencias del sistema si son necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY app.py .

# Exponer puerto de Streamlit
EXPOSE 8501

# Health check para docker-compose
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Comando para ejecutar Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
