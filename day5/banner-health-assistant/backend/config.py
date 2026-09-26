"""Centralized runtime configuration, read from environment variables.

Every setting has a default that preserves the exact previous hardcoded behavior, so nothing
changes for local/dev use unless these variables are explicitly set (e.g. via docker-compose's
.env support, or `export VAR=...` before launching uvicorn).
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE_URL = os.environ.get(
    "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'banner_health.db')}"
)

CORS_ALLOW_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("CORS_ALLOW_ORIGINS", "*").split(",")
    if origin.strip()
] or ["*"]

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8000"))

# --- Auth ---
# This default is clearly a placeholder, not a real secret: it exists so the app runs
# out-of-the-box for local/demo use. `main.py` logs a loud warning at startup if it's
# still in use. Set a real JWT_SECRET_KEY (e.g. `openssl rand -hex 32`) for anything
# beyond a local demo.
_DEFAULT_JWT_SECRET = "dev-only-INSECURE-default-secret-change-me-before-any-real-deploy-00"
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", _DEFAULT_JWT_SECRET)
JWT_IS_DEFAULT_SECRET = JWT_SECRET_KEY == _DEFAULT_JWT_SECRET
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
