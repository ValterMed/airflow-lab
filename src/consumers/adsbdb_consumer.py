#!/usr/bin/env python3
"""
ADSBDB CONSUMER – Kafka -> MongoDB
Lee eventos del tópico (events.raw), filtra source='adsbdb' y escribe el payload
como documento en la colección 'adsbdb'. La colección se crea automáticamente
en el primer insert (comportamiento estándar de MongoDB).
"""

import os
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from kafka import KafkaConsumer
from pymongo import MongoClient, errors
from pymongo.collection import Collection

# ----------------- Config -----------------
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "events.raw")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "adsbdb-mongo-writer")

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://admin:mongopass@localhost:27017/")
MONGODB_DB = os.getenv("MONGODB_DB", "kafka_events_db")
# El nombre de la colección será el 'source' del evento (adsbdb)
EXPECTED_SOURCE = os.getenv("EXPECTED_SOURCE", "adsbdb")

# logging básico
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger("adsbdb_consumer")


# ----------------- Conexiones -----------------
def connect_mongo_collection(db_name: str, coll_name: str) -> Collection:
    """
    Conecta a MongoDB y devuelve la colección (se crea automáticamente si no existe).
    """
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        log.info("✅ Conectado a MongoDB")
        db = client[db_name]
        coll = db[coll_name]
        # Índice sugerido para upsert/deduplicación: event_id y/o (mode_s, registration, event_timestamp)
        try:
            coll.create_index([("event_id", 1)], name="idx_event_id", unique=False)
            coll.create_index(
                [("mode_s", 1), ("registration", 1), ("event_timestamp", 1)],
                name="idx_mode_registration_evt",
                unique=False,
            )
        except Exception as ie:
            log.warning(f"Índices: {ie}")
        return coll
    except errors.ConnectionFailure as e:
        log.error(f"❌ Error conectando a MongoDB: {e}")
        raise


def connect_kafka_consumer() -> KafkaConsumer:
    """
    Configura el KafkaConsumer para leer JSON.
    """
    cons = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=[KAFKA_BROKER],
        group_id=KAFKA_GROUP_ID,
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        # Si deseas mayor throughput:
        # max_poll_records=200,
        # fetch_min_bytes=1_048_576,
    )
    log.info(f"📡 Conectado a Kafka topic: {KAFKA_TOPIC}, group_id: {KAFKA_GROUP_ID}")
    return cons


# ----------------- Lógica de procesamiento -----------------
def normalize_doc_from_event(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Toma el evento completo producido por FastAPI:
      {
        "id": "...",
        "timestamp": <ms>,
        "source": "adsbdb",
        "payload": {...aircraft...},
        "ingested_at": <ms>,
        "api_version": "..."
      }
    Devuelve un documento listo para Mongo:
      - Cada campo del payload pasa como campo de nivel superior.
      - Se agregan metadatos: event_id, event_timestamp, ingested_at, api_version.
    Si no es de source='adsbdb', retorna None (lo ignoramos).
    """
    if not isinstance(event, dict):
        return None
    if event.get("source") != EXPECTED_SOURCE:
        return None

    payload = event.get("payload") or {}
    if not isinstance(payload, dict):
        log.warning(f"⚠️ Evento adsbdb con payload inválido: {event}")
        return None

    # Documento final: flat con los campos del payload
    doc = dict(payload)

    # Metadatos del evento (útiles para trazabilidad y upsert)
    doc["event_id"] = event.get("id")
    doc["event_timestamp"] = event.get("timestamp")  # ms desde epoch (según tu productor)
    doc["ingested_at"] = event.get("ingested_at")   # ms desde epoch (según tu productor)
    doc["api_version"] = event.get("api_version")

    # Timestamps legibles opcionales:
    try:
        if isinstance(doc["event_timestamp"], (int, float)):
            doc["event_timestamp_iso"] = datetime.utcfromtimestamp(doc["event_timestamp"]/1000.0).isoformat()
    except Exception:
        pass
    try:
        if isinstance(doc["ingested_at"], (int, float)):
            doc["ingested_at_iso"] = datetime.utcfromtimestamp(doc["ingested_at"]/1000.0).isoformat()
    except Exception:
        pass

    return doc


def upsert_adsbdb_document(coll: Collection, doc: Dict[str, Any]) -> bool:
    """
    Inserta/actualiza el documento.
    Estrategia de upsert:
      1) Si hay event_id, usarlo como clave.
      2) Si no, usar combinación (mode_s, registration, event_timestamp).
      3) Si tampoco hay, inserción simple (sin upsert).
    """
    try:
        # 1) Preferir event_id del evento
        event_id = doc.get("event_id")
        if event_id:
            res = coll.update_one({"event_id": event_id}, {"$set": doc}, upsert=True)
            if res.upserted_id:
                log.info(f"📥 Insertado (event_id): {event_id}")
            else:
                log.info("🔄 Actualizado (event_id existente)")
            return True

        # 2) Fallback con claves del payload+timestamp
        key = {}
        if "mode_s" in doc:
            key["mode_s"] = doc["mode_s"]
        if "registration" in doc:
            key["registration"] = doc["registration"]
        if "event_timestamp" in doc:
            key["event_timestamp"] = doc["event_timestamp"]

        if key:
            res = coll.update_one(key, {"$set": doc}, upsert=True)
            if res.upserted_id:
                log.info(f"📥 Insertado: {key}")
            else:
                log.info(f"🔄 Actualizado doc existente: {key}")
            return True

        # 3) Si no hay llaves distintivas, inserta “tal cual”
        coll.insert_one(doc)
        log.info("📥 Insertado (sin clave única)")
        return True

    except Exception as e:
        log.error(f"❌ Error al escribir en MongoDB: {e}")
        return False


def main():
    log.info("🚀 Iniciando ADSBDB Consumer – Kafka → MongoDB")
    consumer = connect_kafka_consumer()
    # colección = nombre del source ("adsbdb")
    collection = connect_mongo_collection(MONGODB_DB, EXPECTED_SOURCE)

    processed, skipped, errors = 0, 0, 0

    try:
        for msg in consumer:
            event = msg.value
            # Filtra y transforma
            doc = normalize_doc_from_event(event)
            if doc is None:
                skipped += 1
                continue

            ok = upsert_adsbdb_document(collection, doc)
            if ok:
                processed += 1
            else:
                errors += 1

            # Log liviano
            if (processed + skipped) % 10 == 0:
                log.info(f"📊 Stats: {processed} ok | {skipped} omitidos | {errors} errores")

    except KeyboardInterrupt:
        log.info("🛑 Detenido por usuario")
    finally:
        consumer.close()
        log.info("✅ Fin de sesión")
        log.info(f"   - Procesados: {processed}")
        log.info(f"   - Omitidos:   {skipped}")
        log.info(f"   - Errores:    {errors}")


if __name__ == "__main__":
    main()
