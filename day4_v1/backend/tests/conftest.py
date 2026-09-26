"""Force observability off for the entire test suite, regardless of what a
developer has in their local .env.

This must happen here, at conftest module-import time — not in a fixture —
because backend.app.main runs `setup_observability()` at *module* import
time (`app = create_app()`), which happens the moment any test file does
`from backend.app.main import app`, before any per-test fixture would get a
chance to run. Pytest loads this conftest.py (and its ancestors) before
importing test modules in this directory tree, so the override lands in
time as long as OTEL_EXPORTER_OTLP_ENDPOINT isn't read anywhere before this.
"""
import os

os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = ""
