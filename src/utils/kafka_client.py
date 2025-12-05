#!/usr/bin/env python3
"""
Kafka Client - Configuración reutilizable de Kafka Consumer
"""

from kafka import KafkaConsumer
import json
import logging

logger = logging.getLogger(__name__)


def create_kafka_consumer(topic, 
                          bootstrap_servers='localhost:9092',
                          group_id=None,
                          auto_offset_reset='earliest'):
    """
    Crear un Kafka Consumer configurado
    
    Args:
        topic: Topic de Kafka a consumir
        bootstrap_servers: Servidor de Kafka
        group_id: ID del consumer group
        auto_offset_reset: Desde dónde leer (earliest/latest)
        
    Returns:
        KafkaConsumer configurado
    """
    if group_id is None:
        group_id = f'mongodb-{topic}-consumer'
    
    try:
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=[bootstrap_servers],
            group_id=group_id,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset=auto_offset_reset,
            enable_auto_commit=True
        )
        
        logger.info(f"📡 Kafka Consumer conectado: {topic} (group: {group_id})")
        return consumer
        
    except Exception as e:
        logger.error(f"❌ Error creando Kafka consumer: {e}")
        raise

