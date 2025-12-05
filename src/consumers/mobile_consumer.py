#!/usr/bin/env python3
"""
📱 MOBILE ANALYTICS CONSUMER - KAFKA → MONGODB
Track crashes, performance, and user sessions
"""

from kafka import KafkaConsumer
from pymongo import MongoClient, errors
import json
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def connect_mongodb():
    """Connect to MongoDB"""
    try:
        client = MongoClient(
            'mongodb://admin:mongopass@localhost:27017/',
            serverSelectionTimeoutMS=5000
        )
        client.admin.command('ping')
        logger.info("✅ Connected to MongoDB")
        
        db = client['kafka_events_db']
        collection = db['mobile_events']
        
        return collection
        
    except errors.ConnectionFailure as e:
        logger.error(f"❌ MongoDB connection error: {e}")
        raise


def process_mobile_event(collection, event):
    """Process mobile analytics event"""
    try:
        required_fields = ['event_id', 'user_id', 'event_type', 'timestamp']
        if not all(field in event for field in required_fields):
            return False
        
        document = event.copy()
        document['inserted_at'] = datetime.utcnow().isoformat()
        
        # Priority flag for crashes
        if event.get('event_type') == 'crash':
            document['priority'] = 'HIGH'
            document['requires_review'] = True
        
        result = collection.insert_one(document)
        
        # Log with context
        event_type = event['event_type']
        user_id = event['user_id']
        
        if event_type == 'crash':
            crash_reason = event.get('crash_reason', 'Unknown')
            device = event.get('device_model', 'Unknown')
            logger.error(f"🚨 CRASH | User: {user_id} | Reason: {crash_reason} | Device: {device}")
        elif event_type == 'performance':
            load_time = event.get('load_time_ms', 0)
            logger.info(f"⚡ PERFORMANCE | User: {user_id} | Load time: {load_time}ms")
        elif event_type == 'session_start':
            logger.info(f"🟢 SESSION_START | User: {user_id}")
        elif event_type == 'session_end':
            duration = event.get('session_duration_sec', 0)
            logger.info(f"🔴 SESSION_END | User: {user_id} | Duration: {duration}s")
        else:
            logger.info(f"📱 {event_type.upper()} | User: {user_id}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False


def main():
    """Main consumer"""
    logger.info("🚀 Starting Mobile Analytics Consumer → MongoDB")
    
    collection = connect_mongodb()
    
    consumer = KafkaConsumer(
        'mobile-analytics',
        bootstrap_servers=['localhost:9092'],
        group_id='mongodb-mobile-consumer',
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=True
    )
    
    logger.info("📡 Connected to Kafka topic: mobile-analytics")
    logger.info("🛑 Press Ctrl+C to stop\n")
    
    stats = {
        'processed': 0,
        'crashes': 0,
        'sessions': 0,
        'performance_events': 0
    }
    
    try:
        for message in consumer:
            event = message.value
            
            if event.get('stream') == 'mobile':
                success = process_mobile_event(collection, event)
                
                if success:
                    stats['processed'] += 1
                    event_type = event.get('event_type')
                    
                    if event_type == 'crash':
                        stats['crashes'] += 1
                    elif event_type == 'session_start':
                        stats['sessions'] += 1
                    elif event_type == 'performance':
                        stats['performance_events'] += 1
                
                if stats['processed'] % 15 == 0:
                    logger.info(f"📊 Stats: {stats['processed']} events | {stats['crashes']} crashes | {stats['sessions']} sessions")
    
    except KeyboardInterrupt:
        logger.info(f"\n🛑 Consumer stopped")
    
    finally:
        consumer.close()
        logger.info(f"✅ Summary: {stats}")


if __name__ == "__main__":
    main()

