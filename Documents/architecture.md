# Architecture (API Producer Add-On)

```mermaid
flowchart LR
    Client[Client / External Source] --> |HTTP JSON| API[API Producer (FastAPI)]
    API --> |publish| K[Kafka Topic: events.raw]
    C[Existing Consumer] --> |consume| K
    C --> |write| M[(MongoDB)]
    ME[mongo-express] --> |view| M
    KUI[Kafka UI] --> |monitor offsets| K
```
