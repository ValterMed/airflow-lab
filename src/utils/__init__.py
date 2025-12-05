"""
Utilities module for Kafka + MongoDB lab
"""

from .mongodb_client import MongoDBClient
from .kafka_client import create_kafka_consumer

__all__ = ['MongoDBClient', 'create_kafka_consumer']

