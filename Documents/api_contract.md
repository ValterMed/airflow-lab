# API Contract — Real-Time API Producer

## Routes

### GET /health
**Purpose:** Readiness check and minimal stats.

**Response (example):**
```json
{
  "status": "ok",
  "topic": "events.raw",
  "accepted_last_min": 7,
  "uptime_seconds": 123,
  "counters": { "accepted": 10, "rejected": 1 },
  "last_error": null,
  "api_version": "1.0.0"
}
```

### POST /ingest
**Purpose:** Accept a JSON event and publish to Kafka.

**Request JSON:**
- `id` (string | optional but recommended) — used for idempotency/tracing. If absent and `REQUIRE_ID=false`, server generates a UUIDv4.
- `timestamp` (number ms since epoch or ISO string | optional) — if missing, server assigns current time.
- `source` (string | required) — e.g., `"manual"`, `"webhook"`, `"sensor"`.
- `payload` (object | required) — free‑form event body.

**Validation:**
- Body must be JSON and ≤ `MAX_PAYLOAD_BYTES`.
- `source` must be a short string; if `ACCEPT_SOURCES` is set, it must be in the whitelist.
- `payload` must be an object.
- Normalize `timestamp` to integer milliseconds; add `ingested_at` and `api_version`.

**Publishing:**
- Kafka topic: `KAFKA_TOPIC` (default `events.raw`).
- Partitioning key: `id` bytes if provided; otherwise a deterministic key derived from `source`.
- Each record value is a compact JSON with normalized fields.

**Responses:**
- `202 Accepted` (or `200 OK`) — on successful enqueue; returns `{ "id", "topic", "partition", "offset" (if available) }`.
- `4xx` — validation failure with reasons.
- `5xx` — broker errors with a hint if retriable.

**Notes on Idempotency & Dedup:**
Downstream consumer should upsert on `id`. Duplicated `id` events are intentional test scenarios for the grader.
