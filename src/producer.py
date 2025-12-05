#!/usr/bin/env python3
"""
# ========================================================================================
# 🚀 KAFKA PRODUCER - GENERADOR DE DATOS MULTI-STREAM PARA ETL
# ========================================================================================
# 
# PROPÓSITO EDUCATIVO:
# Este producer simula tres flujos de datos realistas que encontrarán en el mundo real:
# 1. 🏙️  Smart City Sensors: Datos ambientales de ciudades inteligentes
# 2. 🛒 E-commerce Events: Interacciones de usuarios en plataformas de venta
# 3. 📱 Mobile App Analytics: Métricas de rendimiento y uso de aplicaciones móviles
#
# CONCEPTOS CLAVE DE KAFKA QUE APRENDERÁN:
# - Producer: Aplicación que ENVÍA datos a Kafka
# - Topics: Categorías donde se organizan los mensajes
# - Partitions: División de topics para paralelismo
# - Serialization: Conversión de objetos Python a bytes para transmisión
# - Batching: Agrupación de mensajes para eficiencia
# - Acknowledgments: Confirmaciones de entrega
#
# CONCEPTOS DE ETL QUE APRENDERÁN:
# - Streaming vs Batch: Procesamiento en tiempo real vs por lotes
# - Data Generation: Simulación de fuentes de datos realistas
# - Schema Design: Estructura consistente de mensajes
# - Rate Control: Control de volumen de datos
#
# PATRONES DE DISEÑO:
# - Strategy Pattern: Diferentes generadores de datos
# - Factory Pattern: Creación de producers configurables
# - Observer Pattern: Callbacks para eventos de entrega
# - Command Pattern: Configuración por argumentos
#
# Author: Data Science Lab
# Course: Trends in Data Science - ETL with Kafka
# Level: Intermediate
# ========================================================================================
"""

import json
import time
import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List
from dataclasses import dataclass
import argparse
import logging
from kafka import KafkaProducer
from kafka.errors import KafkaError

# ========================================================================================
# 📊 CONFIGURACIÓN DE LOGGING - OBSERVABILIDAD EN SISTEMAS DISTRIBUIDOS
# ========================================================================================
# CONCEPTO: En sistemas de streaming, el logging es CRÍTICO para:
# - Debuggear problemas en producción
# - Monitorear rendimiento y throughput 
# - Auditar qué datos se enviaron y cuándo
# - Detectar errores de conectividad
#
# PATRÓN PROFESIONAL: Dual logging (archivo + consola)
# - FileHandler: Logs persistentes para análisis posterior
# - StreamHandler: Logs en tiempo real durante desarrollo
# ========================================================================================
logging.basicConfig(
    level=logging.INFO,  # Nivel de detalle: DEBUG < INFO < WARNING < ERROR < CRITICAL
    format='%(asctime)s - %(levelname)s - %(message)s',  # Timestamp + nivel + mensaje
    handlers=[
        # ARCHIVO: Para análisis histórico y troubleshooting
        logging.FileHandler('../data/producer.log'),
        # CONSOLA: Para feedback inmediato durante desarrollo
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)  # Logger específico para este módulo


# ========================================================================================
# ⚙️ CONFIGURACIÓN DEL PRODUCER - PARÁMETROS DE RENDIMIENTO
# ========================================================================================
@dataclass
class ProducerConfig:
    """
    Configuración del Kafka Producer con parámetros optimizados para aprendizaje.
    
    ESTUDIANTES: Estos parámetros afectan directamente el rendimiento y comportamiento
    del producer. Experimenten cambiando valores para ver el impacto.
    """
    # CONEXIÓN: Dirección del cluster Kafka
    # FORMATO: "host1:port1,host2:port2" para múltiples brokers
    bootstrap_servers: str = "localhost:9092"
    
    # BATCHING: Tamaño máximo de lote en bytes (16KB por defecto)
    # CONCEPTO: Mensajes se agrupan en lotes para eficiencia de red
    # TRADE-OFF: Lotes más grandes = mayor throughput pero más latencia
    batch_size: int = 16384  # 16KB = 16 * 1024 bytes
    
    # LATENCIA: Tiempo máximo de espera antes de enviar lote (10ms)
    # CONCEPTO: Balance entre latencia y throughput
    # VALOR ALTO = mayor throughput, VALOR BAJO = menor latencia
    linger_ms: int = 10
    
    # MEMORIA: Buffer total disponible para el producer (32MB)
    # CONCEPTO: Memoria para almacenar mensajes antes de enviarlos
    # SI SE LLENA: El producer bloquea o da error según configuración
    buffer_memory: int = 33554432  # 32MB = 32 * 1024 * 1024 bytes
    
    # COMPRESIÓN: Algoritmo para reducir tamaño de mensajes
    # OPCIONES: 'none', 'gzip', 'snappy', 'lz4', 'zstd'
    # GZIP: Compresión built-in de Python, no requiere librerías adicionales
    compression_type: str = "gzip"


# ========================================================================================
# 🏙️ GENERADOR DE DATOS DE SENSORES DE CIUDAD INTELIGENTE
# ========================================================================================
# CONCEPTO: Simulación de IoT (Internet of Things) en ciudades inteligentes
# CASOS DE USO REALES:
# - Monitoreo ambiental para salud pública
# - Optimización de tráfico y transporte público
# - Gestión inteligente de energía
# - Detección temprana de problemas urbanos
# ========================================================================================
class SmartCitySensorGenerator:
    """
    Genera datos realistas de sensores urbanos distribuidos por ciudades mexicanas.
    
    ESTUDIANTES: Este es un ejemplo de cómo las empresas como Google, IBM Smart Cities,
    o Cisco simulan y procesan datos de sensores urbanos en tiempo real.
    """
    
    def __init__(self):
        # ================================================================================
        # 🗺️ CIUDADES MEXICANAS CON COORDENADAS REALES
        # ================================================================================
        # CONCEPTO: Datos geolocalizados son fundamentales en IoT urbano
        # APLICACIONES: Correlacionar datos ambientales con ubicación geográfica
        self.cities = [
            # Mérida: Capital de Yucatán, conocida por calor extremo
            {"name": "Mérida", "lat": 20.9674, "lon": -89.5926},
            # CDMX: Megalópolis con problemas de contaminación y tráfico
            {"name": "Ciudad de México", "lat": 19.4326, "lon": -99.1332},
            # Guadalajara: Ciudad tecnológica, "Silicon Valley mexicano"
            {"name": "Guadalajara", "lat": 20.6597, "lon": -103.3496},
            # Monterrey: Centro industrial, monitoreo de calidad del aire crucial
            {"name": "Monterrey", "lat": 25.6866, "lon": -100.3161},
            # Cancún: Destino turístico, monitoreo ambiental para sustentabilidad
            {"name": "Cancún", "lat": 21.1619, "lon": -86.8515}
        ]
        
        # ================================================================================
        # 📊 TIPOS DE SENSORES URBANOS MODERNOS
        # ================================================================================
        # ESTUDIANTES: Cada tipo simula sensores reales desplegados en ciudades inteligentes
        self.sensor_types = [
            "temperature",           # Sensores de temperatura ambiente
            "humidity",              # Sensores de humedad relativa
            "air_quality",          # Estaciones de calidad del aire (PM2.5, CO2)
            "noise_level",          # Sonómetros para contaminación acústica
            "traffic_density",      # Cámaras y sensores de flujo vehicular
            "parking_occupancy",    # Sensores en espacios de estacionamiento
            "energy_consumption"    # Medidores inteligentes de energía
        ]
    
    def generate_sensor_event(self) -> Dict[str, Any]:
        """
        Genera un evento individual de sensor con datos realistas.
        
        ESTUDIANTES: Esta función simula una lectura de sensor IoT real.
        Observen cómo se combinan datos aleatorios pero realistas.
        """
        # SELECCIÓN ALEATORIA: Simula sensores distribuidos geográficamente
        city = random.choice(self.cities)
        sensor_type = random.choice(self.sensor_types)
        
        # ============================================================================
        # 🎲 GENERADORES DE VALORES REALISTAS POR TIPO DE SENSOR
        # ============================================================================
        # CONCEPTO: Cada sensor tiene rangos de valores físicamente posibles
        # ESTUDIANTES: Estos rangos están basados en datos reales de México
        value_generators = {
            # Temperatura: Rango típico de ciudades mexicanas
            "temperature": lambda: random.uniform(18.5, 42.3),  # °Celsius (extremos reales)
            
            # Humedad relativa: México tiene climas diversos
            "humidity": lambda: random.uniform(30, 85),  # % (seco a muy húmedo)
            
            # Índice de calidad del aire: 0=Bueno, 500=Peligroso
            "air_quality": lambda: random.uniform(0, 500),  # AQI (Air Quality Index)
            
            # Nivel de ruido: Desde residencial hasta industrial
            "noise_level": lambda: random.uniform(30, 85),  # dB (decibeles)
            
            # Densidad de tráfico: Porcentaje de capacidad vial
            "traffic_density": lambda: random.uniform(0, 100),  # % ocupación
            
            # Ocupación de estacionamientos: Sensores en espacios de parking
            "parking_occupancy": lambda: random.uniform(0, 100),  # % ocupado
            
            # Consumo energético: Medidores inteligentes de edificios
            "energy_consumption": lambda: random.uniform(50, 500)  # kWh por hora
        }
        
        # ============================================================================
        # 📋 ESTRUCTURA DEL MENSAJE - ESQUEMA JSON CONSISTENTE
        # ============================================================================
        # CONCEPTO: Estructura estándar permite procesamiento eficiente downstream
        # ESTUDIANTES: En producción, esto se valida con JSON Schema o Avro
        return {
            # IDENTIFICACIÓN ÚNICA: UUID evita duplicados
            "event_id": str(uuid.uuid4()),
            
            # TIMESTAMP: Momento exacto de la lectura (ISO 8601 format)
            "timestamp": datetime.now().isoformat(),
            
            # CLASIFICACIÓN: Tipo de sensor y ubicación
            "sensor_type": sensor_type,
            "city": city["name"],
            "coordinates": {"lat": city["lat"], "lon": city["lon"]},
            
            # DATOS DEL SENSOR: Valor medido con precisión de 2 decimales
            "value": round(value_generators[sensor_type](), 2),
            "unit": self._get_unit(sensor_type),  # Unidad de medida
            
            # METADATOS: Información adicional para debugging y análisis
            "sensor_id": f"sensor_{random.randint(1000, 9999)}",
            # 75% probabilidad de estar activo (simulación realista)
            "status": random.choice(["active", "active", "active", "maintenance"]),
            "data_source": "smart_city_sensors"  # Identificador del stream
        }
    
    def _get_unit(self, sensor_type: str) -> str:
        """Get appropriate unit for sensor type"""
        units = {
            "temperature": "°C",
            "humidity": "%",
            "air_quality": "AQI",
            "noise_level": "dB",
            "traffic_density": "%",
            "parking_occupancy": "%",
            "energy_consumption": "kWh"
        }
        return units.get(sensor_type, "unit")


class EcommerceEventGenerator:
    """Generates realistic e-commerce user interaction events"""
    
    def __init__(self):
        self.user_ids = [f"user_{i:05d}" for i in range(1, 10001)]
        self.products = [
            {"id": "prod_001", "name": "Wireless Headphones", "category": "Electronics", "price": 2499.99},
            {"id": "prod_002", "name": "Smart Watch", "category": "Electronics", "price": 4999.99},
            {"id": "prod_003", "name": "Coffee Maker", "category": "Appliances", "price": 1299.99},
            {"id": "prod_004", "name": "Running Shoes", "category": "Sports", "price": 1899.99},
            {"id": "prod_005", "name": "Backpack", "category": "Accessories", "price": 899.99},
            {"id": "prod_006", "name": "Laptop", "category": "Electronics", "price": 15999.99},
            {"id": "prod_007", "name": "Yoga Mat", "category": "Sports", "price": 599.99},
            {"id": "prod_008", "name": "Book", "category": "Education", "price": 299.99}
        ]
        
        self.event_types = [
            "page_view", "product_view", "add_to_cart", 
            "remove_from_cart", "purchase", "search", "login", "logout"
        ]
    
    def generate_ecommerce_event(self) -> Dict[str, Any]:
        """Generate a single e-commerce event"""
        user_id = random.choice(self.user_ids)
        event_type = random.choice(self.event_types)
        product = random.choice(self.products)
        
        base_event = {
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "session_id": f"session_{random.randint(100000, 999999)}",
            "event_type": event_type,
            "user_agent": random.choice([
                "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6)",
                "Mozilla/5.0 (Android 11; Mobile)",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
            ]),
            "ip_address": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            "data_source": "ecommerce_events"
        }
        
        # Add event-specific data
        if event_type in ["product_view", "add_to_cart", "remove_from_cart", "purchase"]:
            base_event.update({
                "product_id": product["id"],
                "product_name": product["name"],
                "product_category": product["category"],
                "product_price": product["price"]
            })
            
            if event_type == "purchase":
                base_event["quantity"] = random.randint(1, 5)
                base_event["total_amount"] = base_event["quantity"] * product["price"]
        
        elif event_type == "search":
            base_event["search_query"] = random.choice([
                "wireless headphones", "laptop", "running shoes", 
                "coffee maker", "smart watch", "backpack"
            ])
        
        return base_event


class MobileAnalyticsGenerator:
    """Generates realistic mobile app analytics events"""
    
    def __init__(self):
        self.app_versions = ["1.2.3", "1.2.4", "1.3.0", "1.3.1"]
        self.screen_names = [
            "home", "profile", "settings", "catalog", "cart", 
            "checkout", "search", "product_detail", "login"
        ]
        self.device_types = ["iPhone", "Android", "iPad", "Android_Tablet"]
        self.os_versions = ["iOS 15.6", "iOS 16.1", "Android 12", "Android 13"]
    
    def generate_analytics_event(self) -> Dict[str, Any]:
        """Generate a mobile analytics event"""
        device_type = random.choice(self.device_types)
        
        return {
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "user_id": f"mobile_user_{random.randint(10000, 99999)}",
            "session_id": f"mobile_session_{random.randint(100000, 999999)}",
            "event_type": random.choice([
                "screen_view", "button_click", "app_launch", "app_close", 
                "crash", "performance_metric", "user_action"
            ]),
            "screen_name": random.choice(self.screen_names),
            "app_version": random.choice(self.app_versions),
            "device_info": {
                "type": device_type,
                "os": random.choice(self.os_versions),
                "model": random.choice([
                    "iPhone 13", "iPhone 14", "Samsung Galaxy S22", 
                    "Google Pixel 7", "iPad Air", "Samsung Tab S8"
                ])
            },
            "performance_metrics": {
                "load_time_ms": random.randint(200, 3000),
                "memory_usage_mb": random.randint(50, 500),
                "battery_level": random.randint(10, 100)
            },
            "location": {
                "country": "Mexico",
                "city": random.choice(["Mérida", "CDMX", "Guadalajara", "Monterrey"])
            },
            "data_source": "mobile_analytics"
        }


# ========================================================================================
# 🚀 CLASE PRINCIPAL - MULTI-STREAM KAFKA PRODUCER
# ========================================================================================
# CONCEPTO: Un producer que maneja múltiples flujos de datos simultáneamente
# PATRÓN: Strategy pattern para diferentes tipos de datos
# CASO DE USO: Empresas reales usan esto para centralizar la ingesta de datos
# ========================================================================================
class MultiStreamKafkaProducer:
    """
    Producer principal que coordina múltiples flujos de datos hacia Kafka.
    
    ESTUDIANTES: Esta clase implementa el patrón Strategy para manejar diferentes
    tipos de datos (sensores, e-commerce, móvil) con una interfaz unificada.
    
    CONCEPTOS CLAVE:
    - Multiplexing: Un solo producer maneja múltiples streams
    - Round-robin: Alterna entre diferentes tipos de datos
    - Rate limiting: Controla la velocidad de generación
    - Monitoring: Rastrea estadísticas de producción
    """
    
    def __init__(self, config: ProducerConfig):
        # CONFIGURACIÓN: Parámetros de rendimiento del producer
        self.config = config
        
        # KAFKA CLIENT: Conexión real al cluster
        # ESTUDIANTES: Este es el objeto que envía datos a Kafka
        self.producer = self._create_producer()
        
        # ============================================================================
        # 🏭 FACTORÍAS DE DATOS - PATRÓN STRATEGY
        # ============================================================================
        # CONCEPTO: Cada generador es una estrategia diferente para crear datos
        # VENTAJA: Fácil agregar nuevos tipos sin modificar código principal
        self.sensor_generator = SmartCitySensorGenerator()     # IoT urbano
        self.ecommerce_generator = EcommerceEventGenerator()   # E-commerce
        self.mobile_generator = MobileAnalyticsGenerator()     # Analytics móviles
        
        # ============================================================================
        # 📊 MAPEO TOPIC → GENERADOR
        # ============================================================================
        # CONCEPTO: Cada topic de Kafka tiene su generador específico
        # ESTUDIANTES: Así se separan diferentes tipos de datos en Kafka
        self.topics = {
            # Topic para datos de sensores urbanos
            "smart-city-sensors": self.sensor_generator.generate_sensor_event,
            # Topic para eventos de comercio electrónico
            "ecommerce.events": self.ecommerce_generator.generate_ecommerce_event,
            # Topic para analytics de aplicaciones móviles
            "mobile-analytics": self.mobile_generator.generate_analytics_event
        }
        
        # ============================================================================
        # 📈 MONITOREO Y ESTADÍSTICAS
        # ============================================================================
        # CONCEPTO: Fundamental para observabilidad en sistemas de producción
        self.stats = {topic: 0 for topic in self.topics}  # Contador por topic
        self.start_time = time.time()  # Para calcular throughput
    
    def _create_producer(self) -> KafkaProducer:
        """
        Crea y configura el cliente Kafka Producer con parámetros optimizados.
        
        ESTUDIANTES: Esta función es CRÍTICA - aquí se establecen todas las
        garantías de entrega, serialización y rendimiento del sistema.
        """
        try:
            producer = KafkaProducer(
                # ====================================================================
                # 🌐 CONEXIÓN AL CLUSTER
                # ====================================================================
                bootstrap_servers=self.config.bootstrap_servers,
                
                # ====================================================================
                # 📄 SERIALIZACIÓN - CONVERSIÓN DE OBJETOS A BYTES
                # ====================================================================
                # VALUE SERIALIZER: Convierte diccionarios Python → JSON → bytes
                # CONCEPTO: Kafka solo transmite bytes, no objetos Python
                value_serializer=lambda x: json.dumps(x, ensure_ascii=False).encode('utf-8'),
                
                # KEY SERIALIZER: Convierte strings → bytes (para partition keys)
                # CONCEPTO: Keys determinan a qué partition va cada mensaje
                key_serializer=lambda x: x.encode('utf-8') if x else None,
                
                # ====================================================================
                # ⚡ OPTIMIZACIÓN DE RENDIMIENTO
                # ====================================================================
                batch_size=self.config.batch_size,           # Tamaño de lote
                linger_ms=self.config.linger_ms,             # Tiempo de espera
                buffer_memory=self.config.buffer_memory,     # Memoria buffer
                compression_type=self.config.compression_type, # Compresión
                
                # ====================================================================
                # 🛡️ GARANTÍAS DE ENTREGA Y CONFIABILIDAD
                # ====================================================================
                # RETRIES: Intentos automáticos si falla el envío
                # CONCEPTO: Resiliencia ante problemas de red temporales
                retries=3,
                
                # ACKNOWLEDGMENTS: Nivel de confirmación requerido
                # 'all' = Espera confirmación de TODOS los replicas
                # OPCIONES: 0 (sin esperar), 1 (solo líder), 'all' (todos)
                # ESTUDIANTES: 'all' = máxima durabilidad, menor rendimiento
                acks='all'  
            )
            
            logger.info(f"✅ Connected to Kafka at {self.config.bootstrap_servers}")
            return producer
            
        except KafkaError as e:
            logger.error(f"❌ Failed to create Kafka producer: {e}")
            # PATRÓN: Re-raise para que el error se propague correctamente
            raise
    
    def send_event(self, topic: str, event: Dict[str, Any]) -> None:
        """
        Envía un evento individual a un topic específico de Kafka.
        
        ESTUDIANTES: Esta función implementa el patrón asíncrono de Kafka.
        Los mensajes se envían sin bloquear el hilo principal.
        """
        try:
            # ====================================================================
            # 🗝️ SELECCIÓN DE PARTITION KEY - DISTRIBUCIÓN DE CARGA
            # ====================================================================
            # CONCEPTO: El key determina a qué partition va el mensaje
            # ESTRATEGIA: user_id/sensor_id asegura que mensajes del mismo
            # usuario/sensor siempre vayan a la misma partition (ordenamiento)
            key = event.get('user_id') or event.get('sensor_id') or event.get('event_id')
            
            # ====================================================================
            # 📤 ENVÍO ASÍNCRONO A KAFKA
            # ====================================================================
            # CONCEPTO: send() retorna inmediatamente un "Future" (promesa)
            # NO bloquea el hilo - el envío real sucede en background
            future = self.producer.send(
                topic,      # Topic destino 
                value=event,  # Datos del mensaje (será serializado a JSON)
                key=key     # Key para determinar partition
            )
            
            # ====================================================================
            # 📞 CALLBACKS - PATRÓN ASÍNCRONO AVANZADO
            # ====================================================================
            # CONCEPTO: Callbacks se ejecutan cuando el mensaje se confirma o falla
            # VENTAJA: No bloqueamos el envío pero podemos reaccionar al resultado
            
            # Callback para envío exitoso - ejecuta cuando Kafka confirma recepción
            future.add_callback(self._on_send_success)
            
            # Callback para error - ejecuta si el envío falla
            future.add_errback(self._on_send_error)
            
            # ====================================================================
            # 📊 ACTUALIZAR ESTADÍSTICAS
            # ====================================================================
            # Incrementar contador INMEDIATAMENTE (antes de confirmación)
            # CONCEPTO: Stats de "intentos" vs "confirmados"
            self.stats[topic] += 1
            
        except Exception as e:
            # MANEJO DE ERRORES: Log y continúa (no rompe el flujo)
            logger.error(f"Failed to send event to {topic}: {e}")
    
    def _on_send_success(self, record_metadata):
        """Callback for successful message delivery"""
        logger.debug(f"Message delivered to {record_metadata.topic} partition {record_metadata.partition}")
    
    def _on_send_error(self, exception):
        """Callback for failed message delivery"""
        logger.error(f"Message delivery failed: {exception}")
    
    def run_simulation(self, duration_minutes: int = 60, events_per_second: int = 10):
        """Run the multi-stream data simulation (all streams simultaneously)"""
        logger.info(f"🚀 Starting {duration_minutes}-minute simulation at {events_per_second} events/sec")
        
        end_time = time.time() + (duration_minutes * 60)
        event_interval = 1.0 / events_per_second
        
        try:
            while time.time() < end_time:
                # Select random topic and generate event
                topic = random.choice(list(self.topics.keys()))
                event_generator = self.topics[topic]
                event = event_generator()
                
                # Send event
                self.send_event(topic, event)
                
                # Log progress every 100 events
                total_events = sum(self.stats.values())
                if total_events % 100 == 0:
                    self._log_statistics()
                
                # Sleep to maintain desired rate
                time.sleep(event_interval)
                
        except KeyboardInterrupt:
            logger.info("🛑 Simulation stopped by user")
        finally:
            self._cleanup()
    
    def run_single_stream(self, stream_name: str, duration_minutes: int = 5, events_per_second: int = 3):
        """
        Run a single stream simulation
        
        Args:
            stream_name: Which stream to generate (smart_city, ecommerce, or mobile)
            duration_minutes: How long to run the simulation
            events_per_second: Target rate for the stream
        """
        # Map stream names to topic names
        stream_to_topic = {
            'smart_city': 'smart-city-sensors',
            'ecommerce': 'ecommerce.events',
            'mobile': 'mobile-analytics'
        }
        
        topic = stream_to_topic.get(stream_name)
        if topic not in self.topics:
            logger.error(f"❌ Unknown stream: {stream_name}")
            logger.error(f"Available streams: {list(stream_to_topic.keys())}")
            return
        
        event_generator = self.topics[topic]
        end_time = time.time() + (duration_minutes * 60)
        event_interval = 1.0 / events_per_second
        
        logger.info(f"🚀 Starting {stream_name} ({topic}) for {duration_minutes} minutes at {events_per_second} events/sec")
        
        try:
            while time.time() < end_time:
                # Generate and send event for selected stream only
                event = event_generator()
                self.send_event(topic, event)
                
                # Log progress every 100 events
                total_events = sum(self.stats.values())
                if total_events % 100 == 0:
                    self._log_statistics()
                
                # Sleep to maintain desired rate
                time.sleep(event_interval)
                
        except KeyboardInterrupt:
            logger.info("🛑 Simulation stopped by user")
        finally:
            self._cleanup()
    
    def _log_statistics(self):
        """Log current production statistics"""
        elapsed_time = time.time() - self.start_time
        total_events = sum(self.stats.values())
        rate = total_events / elapsed_time if elapsed_time > 0 else 0
        
        logger.info(f"📊 Produced {total_events} events in {elapsed_time:.1f}s ({rate:.1f} events/sec)")
        for topic, count in self.stats.items():
            logger.info(f"   📈 {topic}: {count} events")
    
    def _cleanup(self):
        """Clean up resources"""
        logger.info("🧹 Cleaning up producer resources...")
        self.producer.flush()  # Ensure all messages are sent
        self.producer.close()
        self._log_statistics()
        logger.info("✅ Producer shutdown complete")


def show_interactive_menu():
    """Show interactive menu when no stream argument provided"""
    print("\n" + "="*70)
    print("🎯 KAFKA PRODUCER - Interactive Mode")
    print("="*70)
    print("\nAvailable data streams:")
    print("  1. smart_city    - IoT sensors (temperature, air quality, traffic)")
    print("  2. ecommerce     - E-commerce events (views, purchases, cart)")
    print("  3. mobile        - Mobile analytics (crashes, sessions, performance)")
    print("  4. all           - All streams simultaneously")
    print("\n" + "-"*70)
    
    # Get stream choice
    while True:
        choice = input("\nSelect stream (1-4) or 'q' to quit: ").strip()
        if choice == 'q':
            print("👋 Exiting...")
            sys.exit(0)
        if choice in ['1', '2', '3', '4']:
            stream_map = {
                '1': 'smart_city', 
                '2': 'ecommerce', 
                '3': 'mobile',
                '4': 'all'
            }
            stream = stream_map[choice]
            break
        print("❌ Invalid choice. Please enter 1-4 or 'q'")
    
    # Get duration
    while True:
        duration_input = input("\nDuration in minutes (default: 5): ").strip()
        if duration_input == '':
            duration = 5
            break
        try:
            duration = int(duration_input)
            if duration > 0:
                break
            print("❌ Duration must be positive")
        except ValueError:
            print("❌ Please enter a valid number")
    
    # Get rate
    while True:
        rate_input = input("Events per second (default: 3): ").strip()
        if rate_input == '':
            rate = 3
            break
        try:
            rate = int(rate_input)
            if rate > 0:
                break
            print("❌ Rate must be positive")
        except ValueError:
            print("❌ Please enter a valid number")
    
    print("\n" + "="*70)
    print(f"✅ Configuration:")
    print(f"   Stream: {stream}")
    print(f"   Duration: {duration} minute(s)")
    print(f"   Rate: {rate} events/sec")
    print("="*70 + "\n")
    
    return stream, duration, rate


def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(
        description="Multi-Stream Kafka Producer for ETL Lab",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Smart city sensors for 5 minutes at 3 events/sec
  python producer.py --stream smart_city --duration 5 --rate 3
  
  # E-commerce events for 10 minutes at 5 events/sec
  python producer.py --stream ecommerce --duration 10 --rate 5
  
  # Mobile analytics for 2 minutes at 2 events/sec
  python producer.py --stream mobile --duration 2 --rate 2
  
  # All streams simultaneously (original behavior)
  python producer.py --stream all --duration 5 --rate 3
  
  # Interactive mode (no arguments - recommended for beginners)
  python producer.py
"""
    )
    
    parser.add_argument(
        "--stream",
        type=str,
        choices=['smart_city', 'ecommerce', 'mobile', 'all'],
        help="Type of data stream to generate (if omitted, shows interactive menu)"
    )
    
    parser.add_argument(
        "--duration", 
        type=int, 
        default=5, 
        help="Simulation duration in minutes (default: 5)"
    )
    
    parser.add_argument(
        "--rate", 
        type=int, 
        default=3, 
        help="Events per second (default: 3)"
    )
    
    parser.add_argument(
        "--kafka-server", 
        default="localhost:9092", 
        help="Kafka bootstrap server (default: localhost:9092)"
    )
    
    args = parser.parse_args()
    
    # If no stream provided, show interactive menu
    if args.stream is None:
        stream, duration, rate = show_interactive_menu()
        kafka_server = args.kafka_server
    else:
        stream = args.stream
        duration = args.duration
        rate = args.rate
        kafka_server = args.kafka_server
    
    # Configure producer
    config = ProducerConfig(bootstrap_servers=kafka_server)
    
    # Create and run producer
    producer = MultiStreamKafkaProducer(config)
    
    logger.info("🎯 Kafka Producer Starting...")
    logger.info(f"📍 Kafka Server: {kafka_server}")
    logger.info(f"📡 Stream: {stream}")
    logger.info(f"⏱️  Duration: {duration} minutes")
    logger.info(f"🚀 Event Rate: {rate} events/second")
    
    if stream == 'all':
        logger.info("📊 Topics: smart-city-sensors, ecommerce.events, mobile-analytics")
        producer.run_simulation(duration_minutes=duration, events_per_second=rate)
    else:
        # Run only the selected stream
        logger.info(f"📊 Topic: {stream}")
        producer.run_single_stream(stream, duration_minutes=duration, events_per_second=rate)


if __name__ == "__main__":
    main()
