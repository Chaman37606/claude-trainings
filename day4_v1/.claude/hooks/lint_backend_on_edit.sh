#!/usr/bin/env bash
# PostToolUse hook: after Edit/Write on a backend/**/*.py file, lint-fix it
# and run the unit tests it's most likely to affect. Reads the tool-call
# JSON payload from stdin (Claude Code's PostToolUse hook contract).
set -euo pipefail

payload="$(cat)"
file_path="$(echo "$payload" | jq -r '.tool_input.file_path // empty')"

if [[ -z "$file_path" || "$file_path" != *"backend/"*.py ]]; then
  exit 0
fi

cd "$(dirname "$0")/../.."

ruff check --fix "$file_path" || true
python3 -m pytest -q -k unit backend/tests/unit || true

exit 0
