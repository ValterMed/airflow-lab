#!/usr/bin/env python3
"""
🌆 SMART CITY SENSOR CONSUMER - KAFKA → MONGODB
Consume sensor events from Kafka and persist them in MongoDB
"""

from kafka import KafkaConsumer
from pymongo import MongoClient, errors
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def connect_mongodb():
    """Conectar a MongoDB con retry logic"""
    try:
        # ESTUDIANTES: Conexión a MongoDB usando las credenciales del docker-compose
        # mongodb://username:password@host:port/database
        client = MongoClient(
            'mongodb://admin:mongopass@localhost:27017/',
            serverSelectionTimeoutMS=5000
        )
        
        # Verificar conexión
        client.admin.command('ping')
        logger.info("✅ Conectado exitosamente a MongoDB")
        
        # Acceder a la base de datos del laboratorio
        db = client['kafka_events_db']
        
        # Acceder a la colección de sensores
        collection = db['sensors']
        
        return collection
        
    except errors.ConnectionFailure as e:
        logger.error(f"❌ Error conectando a MongoDB: {e}")
        raise


def process_sensor_event(collection, event):
    """
    Procesar y guardar un evento de sensor en MongoDB
    
    ESTUDIANTES: Observen cómo:
    1. Validamos los datos antes de insertar
    2. Agregamos metadata útil (processing_time)
    3. Manejamos errores gracefully
    4. Usamos upsert para evitar duplicados
    """
    try:
        # Validar que el evento tenga los campos mínimos
        required_fields = ['sensor_id', 'sensor_type', 'city', 'timestamp']
        if not all(field in event for field in required_fields):
            logger.warning(f"⚠️ Evento incompleto, faltan campos: {event}")
            return False
        
        # Enriquecer el documento con metadata
        document = event.copy()
        document['inserted_at'] = datetime.utcnow().isoformat()
        document['processed_by'] = 'sensor_consumer'
        
        # UPSERT: Si existe un documento con el mismo sensor_id + timestamp, actualiza
        # Si no existe, inserta nuevo
        result = collection.update_one(
            {'sensor_id': event['sensor_id'], 'timestamp': event['timestamp']},
            {'$set': document},
            upsert=True
        )
        
        if result.upserted_id:
            logger.info(f"📥 Insertado: {event['sensor_type']} | {event['city']} | Valor: {event.get('value', 'N/A')}")
        else:
            logger.info(f"🔄 Actualizado documento existente")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error procesando evento: {e}")
        return False


def main():
    """Consumer principal"""
    logger.info("🚀 Iniciando Smart City Sensor Consumer → MongoDB")
    
    # Conectar a MongoDB
    collection = connect_mongodb()
    
    # Configurar Kafka Consumer
    consumer = KafkaConsumer(
        'smart-city-sensors',
        bootstrap_servers=['localhost:9092'],
        group_id='mongodb-sensor-consumer',
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset='earliest',  # Leer desde el principio
        enable_auto_commit=True
    )
    
    logger.info("📡 Conectado a Kafka topic: smart-city-sensors")
    logger.info("🛑 Presiona Ctrl+C para detener\n")
    
    processed_count = 0
    error_count = 0
    
    try:
        for message in consumer:
            event = message.value
            
            # Procesar todos los eventos del topic smart-city-sensors
            # El topic ya filtra por tipo de datos, no necesitamos filtro adicional
            success = process_sensor_event(collection, event)
            
            if success:
                processed_count += 1
            else:
                error_count += 1
            
            # Log cada 10 eventos procesados
            if processed_count % 10 == 0:
                logger.info(f"📊 Estadísticas: {processed_count} procesados | {error_count} errores")
    
    except KeyboardInterrupt:
        logger.info(f"\n🛑 Consumer detenido por usuario")
    
    finally:
        consumer.close()
        logger.info(f"✅ Sesión finalizada:")
        logger.info(f"   - Eventos procesados: {processed_count}")
        logger.info(f"   - Errores: {error_count}")


if __name__ == "__main__":
    main()

