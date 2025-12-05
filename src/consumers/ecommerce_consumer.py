#!/usr/bin/env python3
"""
🛒 E-COMMERCE EVENT CONSUMER - KAFKA → MONGODB
Store complete user journeys for analytics and ML
"""

from kafka import KafkaConsumer
from pymongo import MongoClient, errors
import json
import logging
import os
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def connect_mongodb():
    """Connect to MongoDB"""
    try:
        # Get MongoDB URI from environment or use default
        mongo_uri = os.getenv('MONGODB_URI', 'mongodb://admin:mongopass@localhost:27017/')
        mongo_db = os.getenv('MONGODB_DB', 'kafka_events_db')

        client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=5000
        )
        client.admin.command('ping')
        logger.info("✅ Connected to MongoDB")

        db = client[mongo_db]
        collection = db['ecommerce']

        return collection

    except errors.ConnectionFailure as e:
        logger.error(f"❌ MongoDB connection error: {e}")
        raise


def process_ecommerce_event(collection, event):
    """
    Process and store e-commerce event
    
    ESTUDIANTES: Event Sourcing Pattern
    - Cada evento es inmutable (no se modifica)
    - Se puede reconstruir el estado completo desde eventos
    - Útil para: auditoría, debugging, ML training data
    """
    try:
        # Validate required fields
        required_fields = ['event_id', 'user_id', 'event_type', 'timestamp']
        if not all(field in event for field in required_fields):
            logger.warning(f"⚠️ Incomplete event: {event}")
            return False
        
        # Enrich document
        document = event.copy()
        document['inserted_at'] = datetime.utcnow().isoformat()
        document['processed'] = True
        
        # Insert (no upsert - events are immutable)
        result = collection.insert_one(document)
        
        # Log different event types differently
        event_type = event['event_type']
        user_id = event['user_id']
        
        if event_type == 'purchase':
            amount = event.get('total_amount', 0)
            product = event.get('product_name', 'Unknown')
            logger.info(f"💰 PURCHASE | User: {user_id} | Product: {product} | ${amount}")
        elif event_type == 'add_to_cart':
            product = event.get('product_name', 'Unknown')
            logger.info(f"🛒 ADD_TO_CART | User: {user_id} | Product: {product}")
        elif event_type == 'product_view':
            product = event.get('product_name', 'Unknown')
            logger.info(f"👁️ VIEW | User: {user_id} | Product: {product}")
        else:
            logger.info(f"📊 {event_type.upper()} | User: {user_id}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error processing event: {e}")
        return False


def main():
    """Main consumer"""
    logger.info("🚀 Starting E-commerce Event Consumer → MongoDB")

    # Get Kafka configuration from environment
    kafka_broker = os.getenv('KAFKA_BROKER', 'localhost:9092')
    kafka_topic = os.getenv('KAFKA_TOPIC', 'ecommerce.events')
    kafka_group = os.getenv('KAFKA_GROUP_ID', 'mongodb-ecommerce-consumer')

    collection = connect_mongodb()

    consumer = KafkaConsumer(
        kafka_topic,
        bootstrap_servers=[kafka_broker],
        group_id=kafka_group,
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=True
    )

    logger.info(f"📡 Connected to Kafka topic: {kafka_topic} at {kafka_broker}")
    logger.info("🛑 Press Ctrl+C to stop\n")
    
    processed_count = 0
    purchases = 0
    total_revenue = 0
    
    try:
        for message in consumer:
            event = message.value

            success = process_ecommerce_event(collection, event)

            if success:
                processed_count += 1

                # Track revenue
                if event.get('event_type') == 'purchase':
                    purchases += 1
                    total_revenue += event.get('total_amount', 0)

            # Stats every 20 events
            if processed_count % 20 == 0:
                logger.info(f"📊 Stats: {processed_count} events | {purchases} purchases | ${total_revenue:.2f} revenue")
    
    except KeyboardInterrupt:
        logger.info(f"\n🛑 Consumer stopped by user")
    
    finally:
        consumer.close()
        logger.info(f"✅ Session summary:")
        logger.info(f"   - Events processed: {processed_count}")
        logger.info(f"   - Purchases: {purchases}")
        logger.info(f"   - Total revenue: ${total_revenue:.2f}")


if __name__ == "__main__":
    main()

