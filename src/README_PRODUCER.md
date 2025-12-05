# 📡 Producer.py - Generador de Datos

## ¿Qué es este archivo?

Este es el **productor de datos fake** que genera eventos simulados y los envía a Kafka.

**📝 Nota**: Este archivo es una **copia del Lab 2** incluida aquí para tu comodidad. No necesitas cambiar de directorio durante los ejercicios.

---

## 🎯 Uso Rápido

### Opción 1: Modo Interactivo (Recomendado para principiantes)
```bash
python producer.py
```

Se abrirá un menú interactivo:
```
🎯 KAFKA PRODUCER - Interactive Mode
======================================================================

Available data streams:
  1. smart_city    - IoT sensors (temperature, air quality, traffic)
  2. ecommerce     - E-commerce events (views, purchases, cart)
  3. mobile        - Mobile analytics (crashes, sessions, performance)
  4. all           - All streams simultaneously

Select stream (1-4) or 'q' to quit: _
```

### Opción 2: Modo Directo (Línea de comandos)

#### Generar datos de sensores IoT
```bash
python producer.py --stream smart_city --duration 5 --rate 3
```

#### Generar datos de e-commerce
```bash
python producer.py --stream ecommerce --duration 5 --rate 3
```

#### Generar datos de mobile analytics
```bash
python producer.py --stream mobile --duration 5 --rate 2
```

#### Generar TODOS los streams simultáneamente
```bash
python producer.py --stream all --duration 5 --rate 3
```

---

## ⚙️ Parámetros

| Parámetro | Descripción | Default | Opciones | Ejemplo |
|-----------|-------------|---------|----------|---------|  
| `--stream` | Tipo de datos a generar | Menú interactivo | `smart_city`, `ecommerce`, `mobile`, `all` | `--stream smart_city` |
| `--duration` | Cuántos minutos generar datos | 5 | Cualquier entero positivo | `--duration 5` |
| `--rate` | Eventos por segundo | 3 | Cualquier entero positivo | `--rate 10` |
| `--kafka-server` | Servidor Kafka | localhost:9092 | host:port | `--kafka-server localhost:9092` |

**💡 Tip**: Si omites `--stream`, se mostrará un menú interactivo (ideal para principiantes).

---

## 📊 Tipos de Datos (streams)

### `smart_city` - Sensores Urbanos IoT
Genera datos de:
- **Temperatura** (°C)
- **Calidad del aire** (AQI)
- **Humedad** (%)
- **Ruido** (dB)
- **Tráfico** (densidad %)
- **Parking** (ocupación %)
- **Energía** (kWh)

**Topic Kafka**: `smart-city-sensors`

### `ecommerce` - Eventos de E-commerce
Genera eventos de:
- `product_view` - Usuario vio un producto
- `add_to_cart` - Agregó al carrito
- `remove_from_cart` - Removió del carrito
- `purchase` - Compró (con monto)
- `search` - Buscó productos
- `login` / `logout` - Sesiones

**Topic Kafka**: `ecommerce-events`

### `mobile` - Analytics Móviles
Genera eventos de:
- `session_start` / `session_end` - Sesiones de usuario
- `screen_view` - Navegación
- `user_action` - Clicks, swipes, etc.
- `crash` - Errores de la app
- `performance` - Métricas de rendimiento (load time, memoria)

**Topic Kafka**: `mobile-analytics`

---

## 💡 Tips de Uso

### Para principiantes: Usa el modo interactivo
```bash
# 1. Abre una terminal dedicada para el producer
# 2. Navega a src/
cd laboratories/3-kafka-mongodb-persistence/src

# 3. Ejecuta SIN argumentos
python producer.py

# 4. Selecciona el stream que necesites
# 5. Ingresa duración y rate (o presiona Enter para defaults)
# 6. Deja el producer corriendo
# 7. Ctrl+C para detener cuando termines
```

### Para usuarios avanzados: Modo directo
```bash
# Comando directo con todos los parámetros
cd laboratories/3-kafka-mongodb-persistence/src
python producer.py --stream smart_city --duration 5 --rate 3

# Deja corriendo y trabaja en otros terminales
# Ctrl+C para detener
```

### Ajustar volumen de datos
```bash
# Pocos datos (testing rápido)
python producer.py --stream smart_city --duration 1 --rate 2

# Datos moderados (ejercicios normales)
python producer.py --stream ecommerce --duration 5 --rate 3

# Muchos datos (testing de performance)
python producer.py --stream mobile --duration 10 --rate 10

# Todos los streams simultáneamente (demo completo)
python producer.py --stream all --duration 5 --rate 3
```

---

## 🔧 Cómo Funciona Internamente

El producer:
1. **Conecta a Kafka** (localhost:9092)
2. **Genera datos fake** usando la librería Faker
3. **Serializa a JSON** para enviar por Kafka
4. **Envía al topic** correspondiente según `--stream`
5. **Loguea cada envío** para que veas el progreso

### Ejemplo de datos generados

**Smart City**:
```json
{
  "sensor_id": "SENSOR-MX-TEMP-001",
  "sensor_type": "temperature",
  "city": "Ciudad de México",
  "value": 24.5,
  "timestamp": "2025-09-30T10:30:00.000Z",
  "stream": "smart_city"
}
```

**E-commerce**:
```json
{
  "event_id": "EVT-1696089600-12345",
  "user_id": "USER-001",
  "event_type": "purchase",
  "product_name": "Laptop Dell XPS 15",
  "amount": 25000,
  "city": "Guadalajara",
  "timestamp": "2025-09-30T10:30:00.000Z",
  "stream": "ecommerce"
}
```

**Mobile**:
```json
{
  "event_id": "MOBILE-1696089600-789",
  "user_id": "MUSER-042",
  "event_type": "crash",
  "crash_reason": "NullPointerException",
  "device_model": "iPhone 14 Pro",
  "platform": "iOS",
  "app_version": "2.5.0",
  "timestamp": "2025-09-30T10:30:00.000Z",
  "stream": "mobile"
}
```

---

## 🚨 Troubleshooting

### Error: "Connection refused" (Kafka)
```bash
# Verifica que Kafka esté corriendo
docker ps | grep kafka

# Si no está, inicia servicios
docker-compose up -d

# Espera 30 segundos
sleep 30
```

### Error: "No module named 'faker'"
```bash
# Instala dependencias
pip install -r ../requirements.txt
```

### El producer no genera datos
```bash
# Verifica que estés usando el parámetro correcto
python producer.py --stream smart_city  # ✅ Correcto
python producer.py --type smart_city    # ❌ Incorrecto (parámetro no existe)

# O usa el modo interactivo (más fácil)
python producer.py  # ✅ Correcto - muestra menú
```

### Quiero ver todas las opciones
```bash
python producer.py --help
```

---

## 📖 Código Fuente

El archivo `producer.py` está bien comentado. **Léelo** para entender:
- Cómo conectarse a Kafka
- Cómo generar datos fake realistas
- Cómo enviar mensajes a topics
- Patrones de error handling

**Ubicación**: `src/producer.py` (~779 líneas con comentarios educativos)

### Nuevas Funcionalidades (Lab 3)
- ✅ Menú interactivo cuando se ejecuta sin argumentos
- ✅ Argumento `--stream` para seleccionar tipo de datos
- ✅ Defaults optimizados (5 min, 3 eventos/sec)
- ✅ Opción `all` para generar todos los streams simultáneamente
- ✅ Mejor help con ejemplos claros

---

**Para más detalles sobre Kafka producers, consulta el Lab 2: ETL-kafka** 📚

