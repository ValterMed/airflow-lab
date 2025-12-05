# 🔧 Guía de Instalación - Dependencias del Proyecto

## ⚠️ Problema Común

Si ves este error:
```
ModuleNotFoundError: No module named 'kafka.vendor.six.moves'
```

Es porque tienes instalado `kafka-python` (obsoleto) en lugar de `kafka-python-ng` (mantenido).

## 🚀 Instalación Correcta

### Paso 1: Limpiar instalación previa de kafka-python

```bash
# Desinstalar kafka-python antiguo
pip uninstall kafka-python -y
```

### Paso 2: Instalar dependencias correctas

```bash
# Opción A: Instalar desde requirements.txt (RECOMENDADO)
pip install -r requirements.txt

# Opción B: Instalar solo las dependencias mínimas para el producer
pip install kafka-python-ng==2.2.2
```

### Paso 3: Verificar instalación

```bash
# Verificar que kafka-python-ng está instalado
pip list | grep kafka

# Deberías ver algo como:
# kafka-python-ng    2.2.2
```

## 📦 Dependencias del Proyecto

### Para Producers (producer.py y multi_producer.py)

```bash
pip install kafka-python-ng==2.2.2
```

### Para Consumer (ecommerce_consumer.py)

```bash
pip install kafka-python-ng==2.2.2 pymongo==4.5.0
```

### Para Dashboard (OPCIONAL - solo si ejecutas localmente)

```bash
pip install kafka-python-ng==2.2.2 pymongo==4.5.0 streamlit==1.28.0 pandas==2.1.1 plotly==5.17.0
```

## 🐍 Versiones de Python Soportadas

- Python 3.9+
- Python 3.10+
- Python 3.11+
- Python 3.12+ ✅ (requiere kafka-python-ng)

## 📋 Dependencias Completas

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| kafka-python-ng | 2.2.2 | Cliente de Kafka (fork mantenido) |
| pymongo | 4.5.0 | Driver de MongoDB |
| pandas | 2.1.1 | Análisis de datos (dashboard) |
| plotly | 5.17.0 | Gráficas interactivas (dashboard) |
| streamlit | 1.28.0 | Framework web (dashboard) |

## 🔍 Troubleshooting

### Problema: "ModuleNotFoundError: No module named 'kafka'"

**Solución:**
```bash
pip install kafka-python-ng==2.2.2
```

### Problema: "ModuleNotFoundError: No module named 'pymongo'"

**Solución:**
```bash
pip install pymongo==4.5.0
```

### Problema: Conflictos de versiones

**Solución:**
```bash
# Crear un entorno virtual limpio
python -m venv venv_ecommerce
source venv_ecommerce/bin/activate  # En Linux/Mac
# o
venv_ecommerce\Scripts\activate  # En Windows

# Instalar dependencias
pip install -r requirements.txt
```

## ✅ Verificación de Instalación

Ejecuta este comando para verificar que todo está instalado correctamente:

```bash
python -c "from kafka import KafkaProducer; print('✅ Kafka client OK')"
```

Si ves `✅ Kafka client OK`, estás listo para ejecutar los producers.

## 🚀 Siguiente Paso

Una vez instaladas las dependencias, regresa a [ECOMMERCE_SETUP.md](ECOMMERCE_SETUP.md) para continuar con la configuración del proyecto.
