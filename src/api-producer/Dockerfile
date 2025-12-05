FROM python:3.11-slim

WORKDIR /app

# System deps (optional but good practice)
RUN apt-get update && apt-get install -y --no-install-recommends     ca-certificates curl &&     rm -rf /var/lib/apt/lists/*

COPY src/api-producer/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY src/api-producer/app /app/app

ENV PYTHONUNBUFFERED=1     PORT=8080

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
