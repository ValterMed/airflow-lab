# 🏗️ Architecture - Kafka + MongoDB Lab

## 📐 Arquitectura General

```
┌─────────────────────────────────────────────────────────────────┐
│                     LAB 2: KAFKA PRODUCERS                      │
│                   (Reutilizamos del lab anterior)               │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐      │
│  │smart_city    │  │ecommerce     │  │mobile_analytics │      │
│  │producer      │  │producer      │  │producer         │      │
│  └──────┬───────┘  └──────┬───────┘  └────────┬────────┘      │
└─────────┼──────────────────┼───────────────────┼───────────────┘
          │                  │                   │
          ▼                  ▼                   ▼
    ┌─────────────────────────────────────────────────┐
    │              KAFKA CLUSTER                      │
    │  Topic: smart-city-sensors                      │
    │  Topic: ecommerce-events                        │
    │  Topic: mobile-analytics                        │
    └───────────┬──────────────────────────────────────┘
                │
                ▼
    ┌─────────────────────────────────────────────────┐
    │         LAB 3: PYTHON CONSUMERS                 │
    │                                                 │
    │  ┌───────────────────────────────────────┐     │
    │  │  src/consumers/                       │     │
    │  │  - sensor_consumer.py                 │     │
    │  │  - ecommerce_consumer.py              │     │
    │  │  - mobile_consumer.py                 │     │
    │  │                                       │     │
    │  │  (Usan: utils/kafka_client.py)       │     │
    │  │  (Usan: utils/mongodb_client.py)     │     │
    │  └───────────┬───────────────────────────┘     │
    └──────────────┼─────────────────────────────────┘
                   │
                   ▼
    ┌─────────────────────────────────────────────────┐
    │              MONGODB                            │
    │  Database: kafka_events_db                      │
    │    Collection: sensors                          │
    │    Collection: ecommerce                        │
    │    Collection: mobile_events                    │
    └───────────┬──────────────────────────────────────┘
                │
                ├─────────────┬─────────────┬──────────
                │             │             │
                ▼             ▼             ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │  QUERIES     │ │   EXPORTS    │ │    DEMOS     │
    │              │ │              │ │              │
    │ - Analytics  │ │ - CSV Export │ │ - Advanced   │
    │ - Reports    │ │ - Pandas     │ │ - Indexes    │
    └──────────────┘ └──────────────┘ └──────────────┘
```

---

## 🗂️ Estructura del Código (Modular)

### 📦 Principios de Diseño

1. **Separación de Responsabilidades** (SRP)
   - `consumers/` = Solo lectura de Kafka y escritura a MongoDB
   - `queries/` = Solo lectura y análisis de MongoDB
   - `utils/` = Código reutilizable sin lógica de negocio
   - `exports/` = Transformaciones y exports
   - `demos/` = Ejemplos avanzados educativos

2. **DRY (Don't Repeat Yourself)**
   - Conexiones MongoDB centralizadas en `utils/mongodb_client.py`
   - Configuración Kafka en `utils/kafka_client.py`
   - Imports compartidos en `__init__.py`

3. **Facilidad de Testing**
   - Cada módulo es independiente
   - Utils se pueden mockear fácilmente
   - Queries no tienen side effects

---

## 🔧 Componentes Detallados

### 1️⃣ Consumers (`src/consumers/`)

**Responsabilidad**: Kafka → MongoDB data pipeline

```python
# Flujo típico de un consumer:
1. Conectar a Kafka (usando utils/kafka_client.py)
2. Conectar a MongoDB (usando utils/mongodb_client.py)  
3. Loop infinito:
   - Leer mensaje de Kafka
   - Validar datos
   - Enriquecer con metadata
   - Insertar en MongoDB
   - Log de progreso
4. Graceful shutdown (Ctrl+C)
```

**Archivos**:
- `sensor_consumer.py` - Smart city IoT data
- `ecommerce_consumer.py` - E-commerce events (event sourcing pattern)
- `mobile_consumer.py` - Mobile app analytics

---

### 2️⃣ Queries (`src/queries/`)

**Responsabilidad**: Análisis de datos en MongoDB

```python
# Flujo típico de queries:
1. Conectar a MongoDB
2. Ejecutar múltiples queries analíticos
3. Imprimir resultados formateados
4. Cerrar conexión
```

**Tipos de queries implementados**:
- Simple filters (`find()`)
- Aggregation pipelines (`aggregate()`)
- Statistical analysis (avg, min, max, stddev)
- Time-series analysis
- Geospatial queries
- Text search

**Archivos**:
- `sensor_queries.py` - ~10 queries urbanos
- `ecommerce_queries.py` - ~10 queries de conversión
- `mobile_queries.py` - ~10 queries de performance

---

### 3️⃣ Utils (`src/utils/`)

**Responsabilidad**: Código reutilizable

#### `mongodb_client.py`
```python
class MongoDBClient:
    """
    Gestiona conexiones a MongoDB con:
    - Connection pooling automático
    - Context manager support (with statement)
    - Error handling robusto
    - Health checks
    """
    
    # Métodos principales:
    - connect()              # Establecer conexión
    - get_collection(name)   # Obtener colección
    - close()                # Cerrar conexión limpiamente
    - __enter__/__exit__     # Context manager
```

#### `kafka_client.py`
```python
def create_kafka_consumer(topic, ...):
    """
    Factory function para Kafka consumers con:
    - Configuración estandarizada
    - JSON deserialización automática
    - Consumer groups configurables
    - Logging consistente
    """
```

---

### 4️⃣ Exports (`src/exports/`)

**Responsabilidad**: Exportar datos a otros formatos

```python
# Flujo típico:
1. Conectar a MongoDB
2. Query datos (con filters opcionales)
3. Convertir a DataFrame (pandas)
4. Exportar a formato (CSV, Parquet, etc.)
5. Logging de estadísticas
```

**Casos de uso**:
- Análisis en Excel/Google Sheets
- ML pipelines con pandas
- Compartir datos con stakeholders
- Backup de datos

---

### 5️⃣ Demos (`src/demos/`)

**Responsabilidad**: Demostraciones educativas avanzadas

#### `advanced_queries.py`
Features demostrados:
- Aggregation pipeline complejo
- Time-series analysis
- Geospatial queries
- Text search indexes
- Query performance analysis (`.explain()`)
- Cohort analysis
- Data quality checks

#### `index_optimization.py`
Demuestra:
- Performance sin índices (COLLSCAN)
- Creación de índices
- Performance con índices (IXSCAN)
- Comparación de speedup
- Index storage analysis
- Compound indexes

---

## 🔄 Flujos de Datos

### Flujo 1: Ingesta de Datos
```
Producer (Lab 2) 
  ↓
Kafka Topic
  ↓
Consumer (Lab 3)
  ├─ Validate
  ├─ Enrich
  └─ Insert
  ↓
MongoDB
```

### Flujo 2: Análisis de Datos
```
MongoDB
  ↓
Query Script
  ├─ Aggregate
  ├─ Filter
  └─ Calculate
  ↓
Console Output
```

### Flujo 3: Export para ML
```
MongoDB
  ↓
Export Script
  ├─ Query
  ├─ DataFrame
  └─ Transform
  ↓
CSV File
  ↓
pandas/sklearn
```

---

## 🎯 Patrones de Diseño Implementados

### 1. Factory Pattern
```python
# utils/kafka_client.py
consumer = create_kafka_consumer(topic='smart-city-sensors')
```

### 2. Context Manager Pattern
```python
# utils/mongodb_client.py
with MongoDBClient() as mongo:
    collection = mongo.get_collection('sensors')
    # Cleanup automático al salir
```

### 3. Single Responsibility Principle
Cada archivo tiene una responsabilidad clara:
- `sensor_consumer.py` = Solo sensores
- `sensor_queries.py` = Solo queries de sensores
- Fácil de entender, mantener y testear

### 4. DRY (Don't Repeat Yourself)
```python
# Antes (repetido en 3 archivos):
client = MongoClient('mongodb://admin:mongopass@localhost:27017/')
# ...

# Ahora (centralizado):
from utils.mongodb_client import MongoDBClient
mongo = MongoDBClient()
```

---

## 📊 Escalabilidad

### Horizontal Scaling (Kafka)
```
Producer → Kafka (3 partitions) → 3 Consumers (parallel)
```

### Vertical Scaling (MongoDB)
```
MongoDB Indexes → Faster queries
MongoDB Sharding → More data
```

### Load Balancing
```
Consumer Group → Kafka distributes partitions automatically
```

---

## 🔐 Seguridad

### Credenciales
```python
# ❌ Hardcoded (lab educativo)
username = 'admin'
password = 'mongopass'

# ✅ Producción (usar environment variables)
import os
username = os.getenv('MONGO_USER')
password = os.getenv('MONGO_PASS')
```

### Network Isolation
```
Docker Network: kafka-mongo-network
├─ Kafka (internal: kafka:29092)
├─ MongoDB (internal: mongodb:27017)
└─ Exposed only: localhost:9092, localhost:27017
```

---

## 🧪 Testing Strategy

### Unit Tests (recomendado para producción)
```python
# test_mongodb_client.py
def test_mongodb_connection():
    client = MongoDBClient()
    assert client.db is not None
    client.close()
```

### Integration Tests
```bash
# test_integration.sh
1. Start docker-compose
2. Run producer for 10 seconds
3. Run consumer for 15 seconds
4. Query MongoDB - assert count > 0
5. docker-compose down
```

---

## 📚 Para Aprender Más

- **MongoDB Aggregation**: https://docs.mongodb.com/manual/aggregation/
- **Kafka Consumers**: https://kafka.apache.org/documentation/#consumerapi
- **Python Context Managers**: https://docs.python.org/3/library/contextlib.html
- **Design Patterns**: "Design Patterns" by Gang of Four

---

**Esta arquitectura prepara a los estudiantes para sistemas reales de producción** 🚀
