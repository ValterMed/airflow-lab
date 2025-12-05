# 🛒 E-commerce Analytics Pipeline - Guía de Uso

## 📋 Descripción

Este proyecto implementa un pipeline completo de análisis de eventos de e-commerce utilizando:
- **Kafka**: Para streaming de eventos en tiempo real
- **MongoDB**: Para persistencia de eventos
- **Streamlit**: Para visualización y análisis interactivo

## 🏗️ Arquitectura

```
Producer (Python) → Kafka (ecommerce.events) → Consumer (Python) → MongoDB
                                                                        ↓
                                                            Dashboard (Streamlit)
```

## 🚀 Inicio Rápido

### 1. Levantar la Infraestructura

```bash
# Iniciar todos los servicios (Kafka, MongoDB, Consumer, Dashboard)
docker compose up -d

# Verificar que todos los servicios estén corriendo
docker compose ps
```

### 2. Generar Eventos de E-commerce

Tienes dos opciones para generar eventos:

#### Opción A: Producer Simple (un proceso)

```bash
# Navegar a la carpeta src
cd src

# Instalar dependecias
pip install -r requirements.txt

# Ejecutar el producer para generar eventos de ecommerce
# Duración: 5 minutos, Tasa: 5 eventos/segundo
python producer.py --stream ecommerce --duration 5 --rate 5
```

#### Opción B: Multi-Producer (múltiples procesos simultáneos)

```bash
# Navegar a la carpeta src
cd src

# Ejecutar múltiples producers simultáneamente
# 3 productores, cada uno durante 10 minutos a 5 eventos/sec
python multi_producer.py --producers 3 --duration 10 --rate 5
```

**Parámetros del Multi-Producer:**
- `--producers N`: Número de instancias de producer a ejecutar en paralelo
- `--duration M`: Duración en minutos de cada producer
- `--rate R`: Eventos por segundo por cada producer

### 3. Verificar que los Datos Fluyen

#### Kafka UI
- URL: http://localhost:8080
- Verifica que existe el tópico `ecommerce.events`
- Deberías ver mensajes llegando en tiempo real

#### Mongo Express
- URL: http://localhost:8081
- Usuario: `admin`
- Password: `mongopass`
- Base de datos: `kafka_events_db`
- Colección: `ecommerce`

### 4. Visualizar el Dashboard

- URL: http://localhost:8501
- El dashboard se actualiza automáticamente
- Incluye:
  - **Métricas Básicas**: Conteo de eventos por tipo, usuarios únicos, revenue
  - **Segmentación de Usuarios**:
    - Por frecuencia de eventos
    - Por categorías de productos
    - Por tipo de dispositivo/navegador
    - Por horarios de actividad

## 📊 Tipos de Eventos Generados

El producer genera los siguientes tipos de eventos de e-commerce:

1. **page_view**: Vista de página
2. **product_view**: Vista de producto
3. **add_to_cart**: Agregar al carrito
4. **remove_from_cart**: Remover del carrito
5. **purchase**: Compra completada
6. **search**: Búsqueda de productos
7. **login**: Inicio de sesión
8. **logout**: Cierre de sesión

## 🛠️ Comandos Útiles

### Docker Compose

```bash
# Ver logs de un servicio específico
docker compose logs -f ecommerce-consumer
docker compose logs -f ecommerce-dashboard

# Reiniciar un servicio
docker compose restart ecommerce-consumer

# Detener todos los servicios
docker compose down

# Detener y eliminar volúmenes (¡cuidado! borra todos los datos)
docker compose down -v
```

### MongoDB

```bash
# Conectarse a MongoDB desde la terminal
docker exec -it kafka-lab-mongodb mongosh -u admin -p mongopass

# Dentro de mongosh:
use kafka_events_db
db.ecommerce.countDocuments()
db.ecommerce.find().limit(5)
```

### Kafka

```bash
# Ver tópicos disponibles
docker exec -it kafka-lab-broker kafka-topics --list --bootstrap-server localhost:9092

# Ver mensajes del tópico (desde el principio)
docker exec -it kafka-lab-broker kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic ecommerce.events \
  --from-beginning \
  --max-messages 10
```

## 📈 Análisis Disponibles en el Dashboard

### 1. Métricas Básicas
- Total de eventos procesados
- Usuarios únicos
- Sesiones únicas
- Revenue total (de compras)
- Distribución de eventos por tipo

### 2. Segmentación de Usuarios

#### Por Frecuencia de Eventos
- **Alto**: 20+ eventos
- **Medio**: 10-19 eventos
- **Bajo**: 1-9 eventos

#### Por Categoría de Productos
- Electronics
- Appliances
- Sports
- Accessories
- Education

#### Por Dispositivo
- iOS (iPhone/iPad)
- Android
- Windows
- macOS

#### Por Horario de Actividad
- **Madrugada**: 0-6 horas
- **Mañana**: 6-12 horas
- **Tarde**: 12-18 horas
- **Noche**: 18-24 horas

## 🎯 Puertos y Servicios

| Puerto | Servicio | Descripción |
|--------|----------|-------------|
| 2181 | Zookeeper | Coordinación de Kafka |
| 9092 | Kafka | Broker de mensajes |
| 8080 | Kafka UI | Interfaz web de Kafka |
| 8501 | Dashboard | Dashboard de Streamlit |
| 27017 | MongoDB | Base de datos |
| 8081 | Mongo Express | Interfaz web de MongoDB |

## 🐛 Troubleshooting

### El consumer no está procesando eventos
```bash
# Verificar logs del consumer
docker compose logs -f ecommerce-consumer

# Reiniciar el consumer
docker compose restart ecommerce-consumer
```

### El dashboard no muestra datos
1. Verificar que el consumer esté corriendo y procesando eventos
2. Verificar en Mongo Express que la colección `ecommerce` tiene documentos
3. Refrescar el dashboard manualmente desde el sidebar

### Kafka no está disponible
```bash
# Verificar health de Kafka
docker compose ps

# Ver logs de Kafka
docker compose logs -f kafka

# Reiniciar servicios de Kafka
docker compose restart zookeeper kafka
```

## 📝 Notas Adicionales

- Los datos se persisten en volúmenes de Docker, por lo que sobreviven a reinicios
- Para empezar con datos frescos, usa `docker compose down -v`
- El dashboard tiene auto-refresh configurable desde el sidebar
- Los producers pueden ejecutarse fuera de Docker (en tu máquina local)
- Asegúrate de tener Python 3.11+ y las dependencias instaladas si ejecutas los producers localmente

## 🔗 Estructura del Proyecto

```
project_airflow/
├── src/
│   ├── producer.py              # Producer principal de eventos
│   ├── multi_producer.py        # Launcher de múltiples producers
│   ├── consumers/
│   │   └── ecommerce_consumer.py   # Consumer de eventos de ecommerce
│   └── dashboard/
│       ├── app.py               # Aplicación Streamlit
│       ├── Dockerfile           # Dockerfile del dashboard
│       └── requirements.txt     # Dependencias del dashboard
├── docker-compose.yml           # Orquestación de servicios
└── ECOMMERCE_SETUP.md          # Esta guía
```

## ✅ Checklist de Verificación

- [ ] Todos los servicios de docker-compose están corriendo
- [ ] Kafka UI muestra el tópico `ecommerce.events`
- [ ] El producer está generando eventos
- [ ] El consumer está procesando eventos (ver logs)
- [ ] Mongo Express muestra documentos en la colección `ecommerce`
- [ ] El dashboard en http://localhost:8501 muestra datos

---

### Author: Valeria Ramirez Hernandez