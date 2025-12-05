# ⚡ Quick Start - Lab 3: Kafka + MongoDB

## 🚀 Inicio Rápido (5 minutos)

### Paso 1: Iniciar servicios
```bash
cd laboratories/3-kafka-mongodb-persistence
docker-compose up -d
```

**Espera 30 segundos** para que los servicios inicialicen.

### Paso 2: Instalar dependencias Python
```bash
pip install -r requirements.txt
```

### Paso 3: Verificar servicios
```bash
# Verificar que todos los contenedores están corriendo
docker-compose ps
# Deberías ver 5 servicios "Up": kafka, zookeeper, mongodb, mongo-express, kafka-ui

# Verificar MongoDB
docker exec kafka-lab-mongodb mongosh -u admin -p mongopass --eval "db.version()"
```

**📝 Nota sobre Kafka Topics**: Se crean automáticamente cuando ejecutes el producer. No requiere pasos adicionales.

### Paso 4: Generar datos con Producer

**Opción A - Modo Interactivo (Recomendado para principiantes)**
```bash
cd src
python producer.py
# Se abrirá un menú interactivo:
# 1. smart_city - IoT sensors
# 2. ecommerce - E-commerce events
# 3. mobile - Mobile analytics
# 4. all - All streams
# Selecciona opción y sigue las instrucciones
```

**Opción B - Modo Directo (Para usuarios avanzados)**
```bash
cd src
python producer.py --stream smart_city --duration 5 --rate 3
```

**Nota**: El producer está incluido en este lab (copiado del Lab 2 para tu comodidad).

### Paso 5: Consumir y persistir en MongoDB
```bash
# Terminal 2 - Consumer (nueva terminal)
cd src/consumers
python sensor_mongo_consumer.py
```

Deberías ver logs como:
```
✅ Conectado exitosamente a MongoDB
📡 Conectado a Kafka topic: smart-city-sensors
📥 Insertado: temperature | Ciudad de México | Valor: 24.5
```

### Paso 6: Ejecutar queries
```bash
# Terminal 3 - Queries (nueva terminal)
cd src/queries
python run_sensor_queries.py
```

---

## 🎯 Ejercicios Completos

### Ejercicio 1: Sensores IoT (30 min)
```bash
# 1. Producer (Terminal 1)
cd laboratories/3-kafka-mongodb-persistence/src
python producer.py --stream smart_city --duration 5 --rate 3

# 2. Consumer (Terminal 2 - nueva terminal)
cd laboratories/3-kafka-mongodb-persistence/src/consumers
python sensor_mongo_consumer.py

# 3. Queries (Terminal 3 - nueva terminal)
cd laboratories/3-kafka-mongodb-persistence/src/queries
python run_sensor_queries.py

# 4. Ver en web
open http://localhost:8081  # Mongo Express (admin/mongopass)
```

### Ejercicio 2: E-commerce (30 min)
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

### Ejercicio 3: Mobile Analytics (30 min)
```bash
# Desde: laboratories/3-kafka-mongodb-persistence/src

# Terminal 1: Producer
python producer.py --duration 5 --rate 2 --stream mobile

# Terminal 2: Consumer
python consumers/mobile_consumer.py

# Terminal 3: Queries
python queries/mobile_queries.py
```

### Ejercicio 4: Queries Avanzados (45 min)
```bash
# Todos los ejercicios anteriores deben estar completos

# 1. Queries avanzados
cd laboratories/3-kafka-mongodb-persistence/src/demos
python advanced_queries.py

# 2. Optimización con índices
python index_optimization.py
```

---

## 🌐 UIs Disponibles

| URL | Servicio | Credenciales |
|-----|----------|-------------|
| http://localhost:8080 | Kafka UI | (no requiere) |
| http://localhost:8081 | Mongo Express | admin / mongopass |

---

## 🧹 Detener servicios

```bash
# Detener sin borrar datos
docker-compose stop

# Detener y eliminar TODO (incluyendo datos)
docker-compose down -v
```

---

## 🐛 Problemas Comunes

### No se insertan datos
```bash
# Verificar que producer está generando datos
cd laboratories/3-kafka-mongodb-persistence/src
python producer.py --stream smart_city --duration 2 --rate 5

# Verificar logs del consumer
# Deberías ver: "📥 Insertado: ..."
```

### Error de conexión a MongoDB
```bash
# Esperar más tiempo
sleep 30

# Verificar logs
docker logs kafka-lab-mongodb
```

### Error de conexión a Kafka
```bash
# Kafka tarda en inicializar
sleep 60

# Verificar logs
docker logs kafka-lab-broker
```

---

**Para más detalles, consulta SETUP-GUIDE.md o STUDENT-EXERCISES.md** 🚀
