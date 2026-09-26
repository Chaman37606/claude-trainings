#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

echo "Starting observability backend (Collector, Tempo, Prometheus, Grafana)..."
docker compose up -d

echo "Waiting for the OTLP collector to accept connections on :4318..."
for i in $(seq 1 30); do
  if curl -sf "http://localhost:4318" >/dev/null 2>&1 || nc -z localhost 4318 2>/dev/null; then
    break
  fi
  sleep 1
done

echo "Starting the app with OpenTelemetry instrumentation..."
exec node -r ./otel-setup.js server.js
