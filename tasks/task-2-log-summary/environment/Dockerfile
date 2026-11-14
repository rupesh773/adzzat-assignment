FROM python:3.11-slim

RUN pip install --no-cache-dir pytest==8.2.0

WORKDIR /app
COPY server_logs.jsonl /app/server_logs.jsonl
