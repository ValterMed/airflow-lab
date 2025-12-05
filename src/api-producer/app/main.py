import os
import time
import json
import uuid
import hashlib
import httpx
import asyncio

from typing import Optional, Any, Dict, Union
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
from kafka import KafkaProducer
from dotenv import load_dotenv

load_dotenv()

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "events.raw")
API_VERSION = os.getenv("API_VERSION", "1.0.0")
MAX_PAYLOAD_BYTES = int(os.getenv("MAX_PAYLOAD_BYTES", "65536"))
REQUIRE_ID = os.getenv("REQUIRE_ID", "false").lower() == "true"
ACCEPT_SOURCES = [s.strip() for s in os.getenv("ACCEPT_SOURCES", "").split(",") if s.strip()]

# NEW: endpoint externo a consumir
ADSB_ENDPOINT = "https://api.adsbdb.com/v0/aircraft/random"

app = FastAPI(title="api-producer", version=API_VERSION)

# Minimal in-memory counters
COUNTERS = {
    "accepted": 0,
    "rejected": 0,
}
LAST_ERROR: Optional[str] = None
START_TIME = time.time()

# Configure Kafka producer (linger/retries for resilience)
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v, separators=(",", ":")).encode("utf-8"),
    key_serializer=lambda v: v if isinstance(v, (bytes, bytearray)) else None,
    retries=3,
    linger_ms=10,
)

def now_ms() -> int:
    return int(time.time() * 1000)

def to_ms(ts: Union[str, int, float, None]) -> int:
    if ts is None:
        return now_ms()
    if isinstance(ts, (int, float)):
        # assume already epoch ms or s; normalize to ms
        # heuristic: if < 10^12 treat as seconds
        return int(ts if ts > 10**12 else ts * 1000)
    if isinstance(ts, str):
        # naive parse: try fromisoformat, fallback to now
        try:
            # Python's fromisoformat does not parse Z, strip if present
            s = ts.strip().replace("Z", "+00:00")
            import datetime as dt
            dt_obj = dt.datetime.fromisoformat(s)
            return int(dt_obj.timestamp() * 1000)
        except Exception:
            return now_ms()
    return now_ms()

class IngestEvent(BaseModel):
    id: Optional[str] = None
    timestamp: Optional[Union[int, float, str]] = None
    source: str
    payload: Dict[str, Any]

    @field_validator("source")
    @classmethod
    def validate_source(cls, v: str):
        if not isinstance(v, str) or not v or len(v) > 64:
            raise ValueError("source must be a non-empty short string (<=64 chars)")
        if ACCEPT_SOURCES and v not in ACCEPT_SOURCES:
            raise ValueError(f"source '{v}' not in ACCEPT_SOURCES")
        return v

    @field_validator("payload")
    @classmethod
    def validate_payload(cls, v: Dict[str, Any]):
        if not isinstance(v, dict):
            raise ValueError("payload must be an object")
        return v

@app.get("/health")
def health():
    uptime = int(time.time() - START_TIME)
    resp = {
        "status": "ok",
        "topic": KAFKA_TOPIC,
        "accepted_last_min": COUNTERS["accepted"],
        "uptime_seconds": uptime,
        "counters": COUNTERS,
        "last_error": LAST_ERROR,
        "api_version": API_VERSION,
    }
    return JSONResponse(resp, status_code=200)

# NEW: helper para publicar y responder de forma uniforme
def _publish_record_and_response(event_id: str, record: dict, key_bytes: Optional[bytes]):
    """
    Publica en Kafka y devuelve la respuesta estándar 202 con id/partition/offset.
    """
    global LAST_ERROR
    try:
        fut = producer.send(KAFKA_TOPIC, key=key_bytes, value=record)
        metadata = fut.get(timeout=5.0)  # espera ack
        COUNTERS["accepted"] += 1
        resp = {
            "id": event_id,
            "topic": KAFKA_TOPIC,
            "partition": metadata.partition,
            "offset": metadata.offset,
            "status": "enqueued",
        }
        return JSONResponse(resp, status_code=202)
    except Exception as e:
        LAST_ERROR = str(e)
        COUNTERS["rejected"] += 1
        raise HTTPException(status_code=503, detail=f"Broker error: {e}. This may be retriable.")

@app.post("/ingest")
async def ingest(request: Request):
    global LAST_ERROR
    raw = await request.body()
    if not raw:
        COUNTERS["rejected"] += 1
        raise HTTPException(status_code=400, detail="Empty body")
    if len(raw) > MAX_PAYLOAD_BYTES:
        COUNTERS["rejected"] += 1
        raise HTTPException(status_code=413, detail=f"Payload exceeds MAX_PAYLOAD_BYTES={MAX_PAYLOAD_BYTES}")

    # Parse JSON
    try:
        data = json.loads(raw.decode("utf-8"))
    except Exception:
        COUNTERS["rejected"] += 1
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Validate & normalize with Pydantic
    try:
        ev = IngestEvent(**data)
    except Exception as e:
        COUNTERS["rejected"] += 1
        raise HTTPException(status_code=422, detail=str(e))

    # ID handling
    event_id = ev.id
    if REQUIRE_ID and not event_id:
        COUNTERS["rejected"] += 1
        raise HTTPException(status_code=400, detail="Field 'id' is required by server policy")
    if not event_id:
        event_id = str(uuid.uuid4())

    # Timestamps
    ts_ms = to_ms(ev.timestamp)
    ingested_at = now_ms()

    # Build record
    record = {
        "id": event_id,
        "timestamp": ts_ms,
        "source": ev.source,
        "payload": ev.payload,
        "ingested_at": ingested_at,
        "api_version": API_VERSION,
    }

    # Partition key bytes
    key_bytes: Optional[bytes] = None
    if event_id:
        key_bytes = event_id.encode("utf-8")
    else:
        key_bytes = hashlib.sha1(ev.source.encode("utf-8")).digest()

    # Publish (usando el helper nuevo)
    return _publish_record_and_response(event_id, record, key_bytes)

# NEW: endpoint que consume ADSBdb y encola el aircraft como payload
@app.post("/ingest/adsbdb")
async def ingest_from_adsbdb():
    """
    Llama a https://api.adsbdb.com/v0/aircraft/random,
    toma `response.aircraft` y lo publica en Kafka con source="adsbdb".
    """
    # 1) Llamada HTTP
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(ADSB_ENDPOINT)
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Upstream request failed: {e!s}")

    if r.status_code != 200:
        # Propaga error de servicio externo sin romper tu API
        raise HTTPException(status_code=502, detail=f"Upstream error {r.status_code}: {r.text[:200]}")

    # 2) Extraer JSON esperado
    try:
        payload_json = r.json()
    except ValueError:
        raise HTTPException(status_code=502, detail="Upstream returned non-JSON payload")

    aircraft = (payload_json.get("response") or {}).get("aircraft")
    if not isinstance(aircraft, dict):
        raise HTTPException(status_code=502, detail="Upstream payload missing 'response.aircraft'")

    # 3) Construir el record con el mismo formato
    event_id = aircraft.get("mode_s") or aircraft.get("registration") or str(uuid.uuid4())
    ts_ms = now_ms()
    record = {
        "id": event_id,
        "timestamp": ts_ms,
        "source": "adsbdb",
        "payload": aircraft,  # <- Cumple tu contrato actual
        "ingested_at": ts_ms,
        "api_version": API_VERSION,
    }

    # 4) Clave de partición (igual que en /ingest)
    key_bytes: Optional[bytes] = event_id.encode("utf-8") if event_id else hashlib.sha1(b"adsbdb").digest()

    # 5) Publicar a Kafka
    return _publish_record_and_response(event_id, record, key_bytes)


async def _adsbdb_burst_task(interval_sec: float, duration_sec: float):
    """
    Tarea asíncrona: durante duration_sec, cada interval_sec invoca a ADSB_ENDPOINT
    y publica en Kafka (mismo flujo que /ingest/adsbdb).
    """
    deadline = time.monotonic() + duration_sec
    while time.monotonic() < deadline:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(ADSB_ENDPOINT)
            if r.status_code == 200:
                payload_json = r.json()
                aircraft = (payload_json.get("response") or {}).get("aircraft")
                if isinstance(aircraft, dict):
                    event_id = aircraft.get("mode_s") or aircraft.get("registration") or str(uuid.uuid4())
                    ts_ms = now_ms()
                    record = {
                        "id": event_id,
                        "timestamp": ts_ms,
                        "source": "adsbdb",
                        "payload": aircraft,
                        "ingested_at": ts_ms,
                        "api_version": API_VERSION,
                    }
                    key_bytes = event_id.encode("utf-8")
                    # Publica en Kafka (helper existente):
                    _ = _publish_record_and_response(event_id, record, key_bytes)
                else:
                    # no rompemos el bucle, solo registramos
                    print("Upstream OK pero sin response.aircraft válido")
            else:
                print(f"Upstream error {r.status_code}: {r.text[:200]}")
        except Exception as e:
            print(f"Error en burst tick: {e}")
        await asyncio.sleep(interval_sec)


@app.post("/ingest/adsbdb/poll")
async def start_adsbdb_burst(
    background_tasks: BackgroundTasks,
    interval_sec: float = 3.0,
    duration_sec: float = 120.0
):
    """
    Lanza un burst en segundo plano (no bloquea la respuesta HTTP).
    Ej: POST /ingest/adsbdb/poll?interval_sec=3&duration_sec=120
    """
    if interval_sec <= 0 or duration_sec <= 0:
        raise HTTPException(status_code=400, detail="interval_sec y duration_sec deben ser > 0")
    job_id = str(uuid.uuid4())
    background_tasks.add_task(_adsbdb_burst_task, interval_sec, duration_sec)
    return {"status": "started", "job_id": job_id, "interval_sec": interval_sec, "duration_sec": duration_sec}