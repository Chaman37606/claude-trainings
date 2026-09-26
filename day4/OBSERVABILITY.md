# Observability: verification

Stack: app (instrumented with OpenTelemetry) → OTel Collector → Tempo (traces) / Prometheus (metrics) → Grafana.

## 1. Start the backend stack

```bash
npm run observability:up
# or: ./start-observability.sh   (also starts the app)
```

This brings up 4 containers: `otel-collector`, `tempo`, `prometheus`, `grafana`.

## 2. Start the app with instrumentation

```bash
npm start
```

`npm start` now runs `node -r ./otel-setup.js server.js`, which preloads the OTel SDK before Express/http are required, so calls into them are auto-instrumented. It exports traces/metrics to the collector at `localhost:4317`/`localhost:4318`.

## 3. Generate some traffic

```bash
curl -X POST localhost:3000/api/calc \
  -H 'Content-Type: application/json' \
  -d '{"amount":5000,"rate":12,"years":10}'

curl localhost:3000/api/health
```

Do this a few times so there's more than one data point.

## 4. Check Grafana

> **Port note:** the app uses `:3000`, so Grafana is mapped to **`http://localhost:3001`** (not 3000) to avoid a clash.

1. Open `http://localhost:3001` and log in with `admin` / `admin`.
2. Both **Prometheus** and **Tempo** datasources are pre-provisioned — no setup needed.
3. **Dashboard**: a pre-built dashboard, **SIP Calculator Overview**, is auto-provisioned (Dashboards list, or `http://localhost:3001/d/sip-calculator-overview`). It has 8 panels: request rate, p50/p95/p99 latency, requests by route, requests by status code, and process/host CPU & memory.
4. **Traces**: go to *Explore*, pick the **Tempo** datasource, search by service name `sip-calculator-backend`. You should see spans for the `/api/calc` and `/api/health` requests you just made.
5. **Metrics** (ad hoc): go to *Explore*, pick the **Prometheus** datasource, and query e.g.:
   - `http_server_request_duration_seconds_count` / `_bucket` / `_sum` — request counts/latency from the auto-instrumentation (stable HTTP semconv, seconds — not the old `http_server_duration_milliseconds_*` name)
   - `process_cpu_utilization`, `process_memory_usage` — process metrics from `@opentelemetry/host-metrics`
   - `system_cpu_utilization`, `system_memory_utilization` — host metrics from `@opentelemetry/host-metrics`
6. You can also check Prometheus directly at `http://localhost:9090/targets` — the `otel-collector` job should show as `UP`.

## Tearing down

```bash
npm run observability:down
```
