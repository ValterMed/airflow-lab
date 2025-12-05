# 🐍 Python Source Code - Kafka + MongoDB Lab

## 📦 Estructura Modular

```
src/
├── producer.py             # ⭐ Data generator (copiado del Lab 2)
│
├── consumers/              # Kafka → MongoDB consumers
│   ├── sensor_consumer.py     # IoT sensors
│   ├── ecommerce_consumer.py  # E-commerce events
│   └── mobile_consumer.py     # Mobile analytics
│
├── queries/                # MongoDB analytical queries
│   ├── sensor_queries.py      # Smart city analytics
│   ├── ecommerce_queries.py   # Conversion funnels
│   └── mobile_queries.py      # Crash analytics
│
├── utils/                  # Shared utilities
│   ├── mongodb_client.py      # MongoDB connection manager
│   └── kafka_client.py        # Kafka consumer factory
│
├── exports/                # Data export tools
│   └── export_to_csv.py       # MongoDB → CSV
│
├── demos/                  # Advanced demonstrations
│   ├── advanced_queries.py    # Complex aggregations
│   └── index_optimization.py  # Performance tuning
│
├── README.md               # This file
└── README_PRODUCER.md      # Guía del producer
```

**💡 Nota importante**: `producer.py` está incluido aquí (copiado del Lab 2) para tu comodidad. Así no necesitas cambiar de directorio durante los ejercicios.

---

## 🚀 Cómo Usar

### Ejercicio 1: Smart City Sensors

```bash
# Terminal 1: Producer (Lab 2)
cd ../../2-ETL-kafka
python src/producer.py --duration 5 --rate 3 --stream smart_city

# Terminal 2: Consumer
cd ../3-kafka-mongodb-persistence/src
python consumers/sensor_consumer.py

# Terminal 3: Queries
python queries/sensor_queries.py
```

### Ejercicio 2: E-commerce Analytics

```bash
# Desde: laboratories/3-kafka-mongodb-persistence/src

# Terminal 1: Producer
python producer.py --duration 5 --rate 3 --stream ecommerce

# Terminal 2: Consumer
python consumers/ecommerce_consumer.py

# Terminal 3: Queries
python queries/ecommerce_queries.py

# Terminal 4: Export
python exports/export_to_csv.py
```

### Ejercicio 3: Mobile App Analytics

```bash
# Desde: laboratories/3-kafka-mongodb-persistence/src

# Terminal 1: Producer
python producer.py --duration 5 --rate 2 --stream mobile

# Terminal 2: Consumer
python consumers/mobile_consumer.py

# Terminal 3: Queries
python queries/mobile_queries.py
```

### Ejercicio 4: Advanced Features

```bash
# Todos los ejercicios anteriores completos

# Advanced aggregation queries
python demos/advanced_queries.py

# Index optimization demo
python demos/index_optimization.py
```

---

## 🧩 Módulos Explicados

### 📥 `consumers/` - Kafka to MongoDB

**Propósito**: Leer eventos de Kafka y persistirlos en MongoDB

**Archivos**:
- `sensor_consumer.py` - Consume datos de sensores IoT
- `ecommerce_consumer.py` - Consume eventos de e-commerce (event sourcing)
- `mobile_consumer.py` - Consume analytics móviles (crashes, performance)

**Uso típico**:
```python
# Ejecutar en terminal separada mientras producer genera datos
python consumers/sensor_consumer.py
```

---

### 🔍 `queries/` - MongoDB Analytics

**Propósito**: Scripts analíticos para consultar datos en MongoDB

**Archivos**:
- `sensor_queries.py` - Análisis de calidad del aire, temperatura, patrones urbanos
- `ecommerce_queries.py` - Funnels de conversión, revenue, comportamiento de usuarios
- `mobile_queries.py` - Crash rates, performance, adopción de versiones

**Uso típico**:
```python
# Ejecutar después de que consumer haya insertado datos
python queries/ecommerce_queries.py
```

---

### 🛠️ `utils/` - Shared Utilities

**Propósito**: Código reutilizable para conexiones y configuraciones

**Módulos**:

#### `mongodb_client.py`
Clase `MongoDBClient` para gestionar conexiones:
```python
from utils.mongodb_client import MongoDBClient

# Context manager (recomendado)
with MongoDBClient() as mongo:
    collection = mongo.get_collection('sensors')
    data = list(collection.find().limit(10))

# O uso directo
mongo = MongoDBClient()
collection = mongo.get_collection('ecommerce')
mongo.close()
```

#### `kafka_client.py`
Factory function para crear consumers:
```python
from utils.kafka_client import create_kafka_consumer

consumer = create_kafka_consumer(
    topic='smart-city-sensors',
    group_id='my-consumer-group',
    auto_offset_reset='earliest'
)
```

---

### 📤 `exports/` - Data Exports

**Propósito**: Exportar datos de MongoDB a otros formatos

**Archivos**:
- `export_to_csv.py` - Exporta colección de e-commerce a CSV para análisis con pandas/Excel

**Uso**:
```bash
python exports/export_to_csv.py
# Genera: ../data/exports/ecommerce_events_export_YYYYMMDD_HHMMSS.csv
```

---

### 🎓 `demos/` - Advanced Demonstrations

**Propósito**: Demos de features avanzados de MongoDB

**Archivos**:
- `advanced_queries.py` - 10 queries complejos con aggregation pipeline
- `index_optimization.py` - Comparación de performance con/sin índices

**Uso**:
```bash
# Ejecutar cuando ya haya bastantes datos en MongoDB
python demos/advanced_queries.py
python demos/index_optimization.py
```

---

## 💡 Patrones de Uso Comunes

### Pattern 1: Desarrollo Iterativo
```bash
# 1. Iniciar consumer en background
python consumers/sensor_consumer.py &

# 2. Generar datos de prueba
cd ../../2-ETL-kafka && python src/producer.py --duration 2 --rate 10 --stream smart_city

# 3. Verificar insertados
python queries/sensor_queries.py | head -20

# 4. Detener consumer
kill %1
```

### Pattern 2: Testing Rápido
```python
# Crear script de test custom
from utils.mongodb_client import MongoDBClient

with MongoDBClient() as mongo:
    sensors = mongo.get_collection('sensors')
    
    # Tu query custom aquí
    result = sensors.find_one()
    print(result)
```

### Pattern 3: Export para ML Pipeline
```bash
# 1. Exportar datos
python exports/export_to_csv.py

# 2. Procesar con pandas
python -c "
import pandas as pd
df = pd.read_csv('../data/exports/ecommerce_events_export_*.csv')
print(df.describe())
"
```

---

## 🔧 Personalización

### Cambiar credenciales de MongoDB

Editar en `utils/mongodb_client.py`:
```python
class MongoDBClient:
    def __init__(self, 
                 host='localhost',        # Cambiar aquí
                 port=27017,
                 username='admin',        # Cambiar aquí
                 password='mongopass',    # Cambiar aquí
                 ...
```

### Cambiar servidor de Kafka

Editar en `utils/kafka_client.py`:
```python
def create_kafka_consumer(topic, 
                          bootstrap_servers='localhost:9092',  # Cambiar aquí
                          ...
```

---

## 🐛 Debugging

### Ver logs detallados
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Luego ejecutar tu script
python consumers/sensor_consumer.py
```

### Verificar conexiones
```bash
# MongoDB
docker exec -it kafka-lab-mongodb mongosh -u admin -p mongopass

# Kafka
docker exec -it kafka-lab-broker kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic smart-city-sensors \
  --from-beginning
```

---

## 📚 Dependencias

Ver `requirements.txt` en raíz del laboratorio:
```
kafka-python==2.0.2
pymongo==4.6.1
pandas==2.1.4
```

Instalar:
```bash
cd ..
pip install -r requirements.txt
```

---

## 🎯 Tips para Estudiantes

1. **Ejecuta consumers en terminals separadas** - Así puedes ver logs en tiempo real
2. **Usa Mongo Express** (http://localhost:8081) para verificar visualmente los datos
3. **Empieza con queries simples** antes de advanced_queries.py
4. **Lee el código de utils/** - Aprenderás patrones reutilizables
5. **Modifica los scripts** - Es la mejor forma de aprender

---

## 📖 Para Más Información

- **STUDENT-EXERCISES.md** - Guía paso a paso de los ejercicios
- **SETUP-GUIDE.md** - Troubleshooting detallado
- **QUICK-START.md** - Inicio rápido en 5 minutos

---

**¿Preguntas? Consulta la documentación o pregunta al instructor** 🚀