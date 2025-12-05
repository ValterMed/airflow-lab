# api-producer (FastAPI → Kafka)

A small HTTP API that validates and publishes events to Kafka in real time. It **only produces**; your existing consumer keeps writing to MongoDB.

## Quick Start

1) Copy this folder into the root of your lab repo (next to your existing compose file).
2) Create `.env` from `.env.example` and adjust values (especially `KAFKA_BROKER`, `KAFKA_TOPIC`).
3) Add the `api-producer` **service block** from `docker-compose.snippet.yml` into your existing `docker-compose.yml`.
4) Build and run:
```bash
docker compose build api-producer
docker compose up -d api-producer
```
5) Health check:
```bash
curl -s http://localhost:8080/health | jq
```

## Ingest example
```bash
curl -s -X POST http://localhost:8080/ingest   -H "Content-Type: application/json"   -d '{
        "source":"manual",
        "payload":{"temperature":27.4,"unit":"C"},
        "timestamp":"2025-10-25T14:00:00Z"
      }' | jq
```

If `REQUIRE_ID=false`, the server will assign a UUID `id` when missing.

## Environment Variables
See `.env.example` for a complete list and defaults.

## Observability
- `/health` exposes minimal counters and uptime.
- Logs include one line per publish attempt with `id`, `source`, and outcome.

## Limits & Backpressure
- Requests larger than `MAX_PAYLOAD_BYTES` are rejected with `413`.
- On broker errors, API returns `5xx` so clients can retry with backoff.
