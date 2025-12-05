# Project Add-On: Real-Time API as Producer
   3.1. [API Producer (FastAPI)](#31-api-producer-fastapi)  
   3.2. [Poller (Scheduler)](#32-poller-scheduler)  
   3.3. [Kafka and Topic](#33-kafka-and-topic)  
   3.4. [Consumer (Kafka → MongoDB)](#34-consumer-kafka--mongodb)  
   3.5. [MongoDB](#35-mongodb)
4. [Data Schemas](#4-data-schemas)  
   4.1. [Kafka Event](#41-kafka-event)  
   4.2. [MongoDB Document](#42-mongodb-document)
5. [Producer Endpoints](#5-producer-endpoints)  
   5.1. [`POST /ingest`](#51-post-ingest)  
   5.2. [`POST /ingest/adsbdb`](#52-post-ingestadsbdb)  
   5.3. [`POST /ingest/adsbdb/poll`](#53-post-ingestadsbdbpoll)
6. [Docker Compose Deployment](#6-docker-compose-deployment)  
   6.1. [File Structure](#61-file-structure)  
   6.2. [Dockerfiles](#62-dockerfiles)  
   6.3. [Services in `docker-compose.yml`](#63-services-in-docker-composeyml)  
   6.4. [Bring Up the Stack](#64-bring-up-the-stack)
7. [Environment Configuration](#7-environment-configuration)
8. [Quick Testing](#8-quick-testing)
9. [Monitoring and Health](#9-monitoring-and-health)
10. [Best Practices and Security](#10-best-practices-and-security)
11. [Scalability Strategies](#11-scalability-strategies)
12. [Troubleshooting (FAQ)](#12-troubleshooting-faq)

---

## 1) System Overview
This project ingests real-time data from a **public aviation API (ADSBDB)** and processes it through **Kafka**:
- The **API Producer (FastAPI)** fetches the API data and publishes events to a Kafka topic.
- A **Consumer** listens to that topic and persists the payload into **MongoDB**, in a collection named after the `source` (e.g. `adsbdb`).
- A **Poller** can automate periodic calls to the Producer every few seconds for a defined duration.

---

## 2) Architecture and Data Flow
```
[ADSBDB API] --> [FastAPI Producer] --> [Kafka Topic: events.raw] --> [Consumer] --> [MongoDB]
                         ^                                              |
                         | (Poller triggers periodic calls)             v
                     [Optional Poller]                           Collection "adsbdb"
```

**Flow:**  
1. The Producer (FastAPI) calls `https://api.adsbdb.com/v0/aircraft/random`.  
2. It extracts `response.aircraft` as the `payload` and publishes an event into Kafka (`events.raw`).  
3. The Consumer subscribed to the topic filters for `source="adsbdb"`, and writes the `payload` as a new MongoDB document.

---

## 3) Components

### 3.1 API Producer (FastAPI)
- Endpoints:
  - `POST /ingest`: Generic ingestion accepting `{ source, payload }`.
  - `POST /ingest/adsbdb`: Fetches from ADSBDB and publishes the `aircraft` payload.
  - `POST /ingest/adsbdb/poll`: Runs a background task calling ADSBDB repeatedly at intervals.

### 3.2 Poller (Scheduler)
- A small service that sends `POST /ingest/adsbdb` every *INTERVAL_SEC* seconds for *DURATION_SEC*.
- Useful for automatic continuous ingestion in Docker environments.

### 3.3 Kafka and Topic
- Primary topic: **`events.raw`**.  
- Producer publishes all events here.  
- Consumer subscribes and filters by `source` value.

### 3.4 Consumer (Kafka → MongoDB)
- Reads events from Kafka.  
- Filters `source == adsbdb`.  
- Inserts/updates MongoDB collection named after `source`.  
- Performs upserts to avoid duplicates using `event_id` or composite keys.

### 3.5 MongoDB
- Database: configurable (default: `kafka_events_db`).  
- Collection: **`adsbdb`** (auto-created).  
- Document: flat structure with all payload fields + metadata (`event_id`, timestamps, API version).

---

## 4) Data Schemas

### 4.1 Kafka Event
```json
{
  "id": "3F28BC",
  "timestamp": 1730000000000,
  "source": "adsbdb",
  "payload": {
    "type": "G Hot Air Balloon",
    "icao_type": "BALL",
    "manufacturer": "Schroeder Fire Balloons",
    "mode_s": "3F28BC",
    "registration": "D-OBII",
    "registered_owner_country_iso_name": "DE",
    "registered_owner_country_name": "Germany",
    "registered_owner_operator_flag_code": "BALL",
    "registered_owner": "Private"
  },
  "ingested_at": 1730000000100,
  "api_version": "1.0.0"
}
```

### 4.2 MongoDB Document
```json
{
  "_id": { "$oid": "..." },
  "type": "G Hot Air Balloon",
  "icao_type": "BALL",
  "manufacturer": "Schroeder Fire Balloons",
  "mode_s": "3F28BC",
  "registration": "D-OBII",
  "registered_owner_country_iso_name": "DE",
  "registered_owner_country_name": "Germany",
  "registered_owner_operator_flag_code": "BALL",
  "registered_owner": "Private",
  "event_id": "3F28BC",
  "event_timestamp": 1730000000000,
  "ingested_at": 1730000000100,
  "api_version": "1.0.0",
  "event_timestamp_iso": "2025-10-26T20:16:03.123Z",
  "ingested_at_iso": "2025-10-26T20:16:03.123Z"
}
```

---

## 5) Producer Endpoints

### 5.1 `POST /ingest`
Generic ingestion for any JSON source.  
**Body:**
```json
{
  "source": "manual",
  "payload": { "message": "Hello from FastAPI", "value": 42 }
}
```
**Example:**
```bash
curl -X POST http://localhost:8090/ingest   -H "Content-Type: application/json"   -d '{"source":"manual","payload":{"message":"Hello","value":42}}'
```

### 5.2 `POST /ingest/adsbdb`
Fetches live data from ADSBDB and publishes an event.
```bash
curl -X POST http://localhost:8090/ingest/adsbdb
```

### 5.3 `POST /ingest/adsbdb/poll`
Triggers a background task that repeats calls to the ADSBDB endpoint.
```bash
curl -X POST "http://localhost:8090/ingest/adsbdb/poll?interval_sec=3&duration_sec=120"
```

---

## 6) Docker Compose Deployment

### 6.1 File Structure
```
.
├─ docker-compose.yml
├─ Dockerfile
├─ Dockerfile.worker
├─ consumers/
│  └─ adsbdb_consumer.py
└─ pollers/
   └─ adsbdb_poller.py
```

### 6.2 Dockerfiles

**Worker (shared for Consumer & Poller)**
```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY consumers/adsbdb_consumer.py consumers/adsbdb_consumer.py
COPY pollers/adsbdb_poller.py    pollers/adsbdb_poller.py
RUN pip install --no-cache-dir kafka-python pymongo requests
CMD ["python", "consumers/adsbdb_consumer.py"]
```

### 6.3 Services in `docker-compose.yml`
```yaml
  adsbdb-consumer:
    build:
      context: .
      dockerfile: Dockerfile.worker
    command: ["python", "consumers/adsbdb_consumer.py"]
    environment:
      - KAFKA_BROKER=kafka:29092
      - KAFKA_TOPIC=events.raw
      - KAFKA_GROUP_ID=adsbdb-mongo-writer
      - MONGODB_URI=mongodb://admin:mongopass@mongodb:27017/
      - MONGODB_DB=kafka_events_db
      - EXPECTED_SOURCE=adsbdb
    depends_on:
      kafka:
        condition: service_healthy
      mongodb:
        condition: service_healthy
      api-producer:
        condition: service_started
    networks:
      - kafka-mongo-network

  adsbdb-poller:
    build:
      context: .
      dockerfile: Dockerfile.worker
    command: ["python", "pollers/adsbdb_poller.py"]
    environment:
      - PRODUCER_BASE_URL=http://api-producer:8080
      - INTERVAL_SEC=3
      - DURATION_SEC=120
    depends_on:
      api-producer:
        condition: service_started
    networks:
      - kafka-mongo-network
```

### 6.4 Bring Up the Stack
```bash
docker compose up -d --build
```
Both services will start:  
- **Poller** calls `/ingest/adsbdb` every 3s for 2 min.  
- **Consumer** writes incoming events to MongoDB.

---

## 7) Environment Configuration

**Producer**
- `KAFKA_BROKER`
- `KAFKA_TOPIC`
- `API_VERSION`
- `MAX_PAYLOAD_BYTES`
- `REQUIRE_ID`
- `ACCEPT_SOURCES`

**Consumer**
- `KAFKA_BROKER`, `KAFKA_TOPIC`, `KAFKA_GROUP_ID`
- `MONGODB_URI`, `MONGODB_DB`
- `EXPECTED_SOURCE`

**Poller**
- `PRODUCER_BASE_URL`
- `INTERVAL_SEC`
- `DURATION_SEC`

---

## 8) Quick Testing

**Check Producer health**
```bash
curl http://localhost:8090/health
```

**Send manual event**
```bash
curl -X POST http://localhost:8090/ingest   -H "Content-Type: application/json"   -d '{"source":"manual","payload":{"message":"Hello","value":1}}'
```

**Trigger ADSBDB ingest**
```bash
curl -X POST http://localhost:8090/ingest/adsbdb
```

**Trigger Poll job**
```bash
curl -X POST "http://localhost:8090/ingest/adsbdb/poll?interval_sec=3&duration_sec=120"
```

**View MongoDB data**
```bash
mongosh
use kafka_events_db
db.adsbdb.find().limit(3).pretty()
```

---

## 9) Monitoring and Health
- Producer: `/health` endpoint with counters and last error.  
- Logs show producer, consumer, and poller activity.  
- Kafka monitoring can use `kafka-consumer-groups.sh` to check offsets/lag.

---

## 10) Best Practices and Security
- Use **timeouts/retries** when calling external APIs.  
- Configure **payload size limits**.  
- Validate inputs via **Pydantic** models.  
- Manage **secrets via environment variables**.  
- Restrict external exposure—only expose FastAPI port 8090.

---

## 11) Scalability Strategies
- **Horizontal scaling**: multiple consumers with same `group.id`.  
- **Kafka partitioning** for higher throughput.  
- **Batch inserts** into Mongo for performance.  
- Maintain indexes (`event_id`, `(mode_s, registration, event_timestamp)`).

---

## 12) Troubleshooting (FAQ)

**Q: `/ingest/adsbdb` returns 502**  
A: The public API may be down or slow. Retry; check producer logs.

**Q: Consumer doesn’t insert into Mongo.**  
A: Verify connection string, Kafka internal broker (`kafka:29092`), and credentials.

**Q: No documents in MongoDB.**  
A: Ensure event `source="adsbdb"` and the consumer is running.

**Q: Duplicate entries in MongoDB.**  
A: Adjust upsert keys (e.g., `event_id` or `mode_s`).

---

> Complete, modular, and scalable pipeline: **Public API → Kafka → FastAPI Producer → MongoDB**.

### Author: Valeria Ramirez Hernandez