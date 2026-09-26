# Observability (AI-DLC Step 15)

Traces + metrics via OpenTelemetry, exported to a pre-provisioned collector →
Tempo (traces) + Prometheus (metrics) → Grafana stack. This app doesn't ship
its own observability infrastructure — it connects to the stack already
running for this environment at `/home/labuser/day4/docker-compose.yaml`.

## Enabling it

Set in `.env` (see `.env.example`):

```
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
OTEL_SERVICE_NAME=biomed-agentic-rag-backend
```

Leave `OTEL_EXPORTER_OTLP_ENDPOINT` empty to disable observability entirely
(the default — `backend/app/observability/otel_setup.py` no-ops so `pytest`
never touches the network).

Start the stack (if not already running):

```bash
cd /home/labuser/day4 && sudo docker compose up -d
```

Endpoints: Grafana `http://localhost:3001` (admin/admin), Prometheus
`http://localhost:9090`. Tempo has no host-published port — query it through
Grafana (Explore → Tempo datasource) or the app's own dashboard below.

## What's instrumented

- **FastAPI auto-instrumentation** — every HTTP request gets a root span (`GET /domains`, `POST /query`, ...).
- **`agent.run_query`** (`backend/app/agent/loop.py`) — one span per agent turn, attributes `domain`, `tool_call_count`.
  - **`llm.messages.create`** — one child span per Anthropic API call, attributes `llm.model`, `llm.stop_reason`; records `llm_call_duration_seconds` and `llm_token_usage` (by `token_type`: input/output).
  - **`tool.<name>`** (`backend/app/agent/tool_registry.py`) — one span per tool dispatch, attribute `tool.outcome` (ok/error/unknown_tool); records `tool_call_count` and `tool_call_duration_seconds`.
    - **`rag.retrieve`** (`backend/app/rag/retriever.py`) — nested under the `rag_search` tool span; attributes `domain`, `top_k`, `result_count`; records `rag_retrieve_duration_seconds`.
- **`RequestsInstrumentor`** — auto-traces the PubMed/Semantic Scholar/ChEMBL HTTP calls the tools make.
- **`SystemMetricsInstrumentor`** — process/host CPU, memory, disk, network (same convention as the existing `sip-calculator-overview` dashboard).

## Dashboard

`docs/grafana/biomed-rag-overview.json` — request rate/latency, tool call rate/errors/latency by tool, RAG retrieval latency by domain, LLM latency by model, token usage by type, process CPU/memory. Deployed to the live provisioning folder:

```bash
cp docs/grafana/biomed-rag-overview.json /home/labuser/day4/grafana/dashboards/
```

(Grafana's dashboard provisioner polls that folder every 10s — no restart needed.) View it at `http://localhost:3001/d/biomed-rag-overview/`.

**Metric name note:** this app's `opentelemetry-instrumentation-fastapi` version emits `http_server_duration_milliseconds_*` (not `http_server_request_duration_seconds_*`, which the semantic conventions changed to in some other language/version combos — the existing `sip-calculator-overview.json` dashboard uses that name). Verify actual metric names via `curl http://localhost:9090/api/v1/label/__name__/values` before copying a query across dashboards — don't assume the name.

## Two infrastructure bugs found and fixed while wiring this up

Both were in the pre-existing stack config, not this app — noted here since they'd silently reappear if that stack is ever recreated with the original files:

1. **`/home/labuser/day4/tempo.yaml` used a Tempo 2.x schema** (`compactor:` block) **against a Tempo 3.0.0 image**, which dropped that top-level key for monolithic mode — the container crash-looped. Fixed by removing the block ([migration guide](https://grafana.com/docs/tempo/latest/set-up-for-tracing/setup-tempo/migrate-to-3/)).
2. **Tempo's OTLP receiver had no explicit `endpoint:`**, so it defaulted to `127.0.0.1:4317` — unreachable from the `otel-collector` container. Fixed by setting `endpoint: 0.0.0.0:4317` / `0.0.0.0:4318` under `distributor.receivers.otlp.protocols`.

## Verification performed

- Generated real HTTP traffic (`/health`, `/domains`) against the running backend and confirmed root spans landed in Tempo (queried via Grafana's container network, since Tempo has no host port): `GET /domains`, `GET /health` traces present with correct `service.name`.
- Ran the agent loop with a mocked Anthropic client (real code path, no live API key needed) and confirmed the full nested span tree in one trace:
  ```
  agent.run_query (796ms)
    llm.messages.create (stop_reason=tool_use)
    tool.rag_search (outcome=ok)
      rag.retrieve (domain=general_biomedical, result_count=1)
    llm.messages.create (stop_reason=end_turn)
  ```
- Confirmed all custom metrics registered in Prometheus (`tool_call_count_total`, `tool_call_duration_seconds_*`, `llm_call_duration_seconds_*`, `llm_token_usage_total`, `rag_retrieve_duration_seconds_*`) plus the auto-instrumented HTTP/process/system metrics.
- Dry-ran every dashboard panel's PromQL against live Prometheus before deploying it; 9/10 returned data, the 10th (tool error rate) correctly returned zero series since no tool has errored yet.
