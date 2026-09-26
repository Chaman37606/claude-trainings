FROM python:3.12-slim

WORKDIR /app

COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/ backend/
COPY frontend/ frontend/

ENV HOST=0.0.0.0 \
    PORT=8000 \
    DATABASE_URL=sqlite:////data/banner_health.db \
    LOG_LEVEL=INFO \
    CORS_ALLOW_ORIGINS=*

# Persist the SQLite file outside the container's writable layer.
VOLUME ["/data"]

EXPOSE 8000

WORKDIR /app/backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
