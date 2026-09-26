#!/usr/bin/env bash
# PostToolUse hook (all tools): append a compact {tool,input_hash,ts} record
# to .claude/logs/tool_calls.jsonl. Dev-time precursor to the app's own
# OpenTelemetry instrumentation (step 15) — same "trace every action" instinct,
# applied to the build process itself.
set -euo pipefail

payload="$(cat)"
tool_name="$(echo "$payload" | jq -r '.tool_name // "unknown"')"
input_hash="$(echo "$payload" | jq -c '.tool_input // {}' | sha256sum | cut -d' ' -f1)"
ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

log_dir="$(dirname "$0")/../logs"
mkdir -p "$log_dir"

jq -nc --arg tool "$tool_name" --arg hash "$input_hash" --arg ts "$ts" \
  '{tool: $tool, input_hash: $hash, ts: $ts}' >> "$log_dir/tool_calls.jsonl"

exit 0
