#!/usr/bin/env python3
"""
MongoDB Client - Conexión reutilizable a MongoDB
"""

from pymongo import MongoClient, errors
import logging

logger = logging.getLogger(__name__)


class MongoDBClient:
    """
    Cliente MongoDB con gestión de conexiones y métodos comunes
    """
    
    def __init__(self, 
                 host='localhost', 
                 port=27017, 
                 username='admin', 
                 password='mongopass',
                 database='kafka_events_db',
                 timeout=5000):
        """
        Inicializar cliente MongoDB
        
        Args:
            host: Hostname de MongoDB
            port: Puerto de MongoDB
            username: Usuario
            password: Contraseña
            database: Base de datos
            timeout: Timeout de conexión en ms
        """
        self.connection_string = f'mongodb://{username}:{password}@{host}:{port}/'
        self.database_name = database
        self.timeout = timeout
        
        self.client = None
        self.db = None
        
        self.connect()
    
    def connect(self):
        """Conectar a MongoDB"""
        try:
            self.client = MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=self.timeout
            )
            
            # Verificar conexión
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            
            logger.info(f"✅ Conectado a MongoDB: {self.database_name}")
            return True
            
        except errors.ConnectionFailure as e:
            logger.error(f"❌ Error conectando a MongoDB: {e}")
            raise
    
    def get_collection(self, collection_name):
        """
        Obtener una colección
        
        Args:
            collection_name: Nombre de la colección
            
        Returns:
            MongoDB collection object
        """
        if self.db is None:
            self.connect()
        
        return self.db[collection_name]
    
    def close(self):
        """Cerrar conexión"""
        if self.client:
            self.client.close()
            logger.info("🔌 Conexión MongoDB cerrada")
    
    def __enter__(self):
        """Context manager support"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup"""
        self.close()

