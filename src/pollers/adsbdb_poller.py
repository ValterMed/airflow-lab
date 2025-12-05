#!/usr/bin/env python3
import os
import time
import requests

PRODUCER_BASE_URL = os.getenv("PRODUCER_BASE_URL", "http://api-producer:8080")
INTERVAL_SEC = float(os.getenv("INTERVAL_SEC", "3.0"))
DURATION_SEC = float(os.getenv("DURATION_SEC", "120.0"))

def main():
    print(f"[poller] Iniciando: {PRODUCER_BASE_URL} cada {INTERVAL_SEC}s durante {DURATION_SEC}s")
    deadline = time.monotonic() + DURATION_SEC
    url = f"{PRODUCER_BASE_URL}/ingest/adsbdb"
    count = 0
    while time.monotonic() < deadline:
        try:
            r = requests.post(url, timeout=15)
            if r.status_code in (200, 202):
                count += 1
                print(f"[poller] OK #{count}: {r.status_code} -> {r.text[:120]}...")
            else:
                print(f"[poller] Error HTTP {r.status_code}: {r.text[:120]}...")
        except Exception as e:
            print(f"[poller] Excepción: {e}")
        time.sleep(INTERVAL_SEC)
    print(f"[poller] Finalizado. Peticiones realizadas: {count}")

if __name__ == "__main__":
    main()
