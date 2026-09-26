# Deployment Guide - Eli Lilly ALCOA+ QA System

## 🌐 Production Deployment

### System Requirements

- **Server**: Linux server (Ubuntu 20.04+ or RHEL 8+)
- **CPU**: 2+ cores
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 20GB for logs and data
- **Database**: SQLite for small deployments, PostgreSQL for enterprise

### Security Recommendations

#### 1. Enable HTTPS/SSL
```bash
# Using Let's Encrypt with Nginx
sudo certbot certonly --standalone -d yourdomain.com
```

#### 2. Configure Authentication
Update `main.py` to enable proper OAuth2/JWT:
```python
from fastapi_jwt_auth import AuthJWT

@app.post("/auth/login")
async def login(username: str, password: str):
    # Implement proper authentication
    pass
```

#### 3. Environment Variables
Create `.env` file:
```
DATABASE_URL=postgresql://user:password@localhost/alcoa_db
SECRET_KEY=your-secret-key-here
API_KEY=api-key-for-external-integrations
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
```

#### 4. Database Security
- Use PostgreSQL instead of SQLite
- Enable SSL connections
- Regular backups
- Implement row-level security

### Docker Deployment

#### Deploy with Docker Compose
```bash
# 1. Clone repository
git clone <repo> eli-lilly-qc

# 2. Create production docker-compose file
cp docker-compose.yml docker-compose.prod.yml

# 3. Update environment variables
nano .env.prod

# 4. Start services
docker-compose -f docker-compose.prod.yml up -d

# 5. Verify deployment
curl https://yourdomain.com/
```

#### Production docker-compose.yml
```yaml
version: '3.8'

services:
  backend:
    build: .
    container_name: qc-api-prod
    restart: always
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://qcuser:${DB_PASSWORD}@postgres:5432/alcoa_db
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./logs:/app/logs
    depends_on:
      - postgres
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: postgres:15-alpine
    container_name: qc-db-prod
    restart: always
    environment:
      - POSTGRES_USER=qcuser
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=alcoa_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U qcuser"]
      interval: 10s
      timeout: 5s
      retries: 5

  nginx:
    image: nginx:alpine
    container_name: qc-proxy-prod
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.prod.conf:/etc/nginx/conf.d/default.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - ./index.html:/usr/share/nginx/html/index.html:ro
    depends_on:
      - backend
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:
    driver: local
```

### Kubernetes Deployment

#### Create namespace
```bash
kubectl create namespace eli-lilly-qc
```

#### Deploy backend
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: alcoa-backend
  namespace: eli-lilly-qc
spec:
  replicas: 3
  selector:
    matchLabels:
      app: alcoa-backend
  template:
    metadata:
      labels:
        app: alcoa-backend
    spec:
      containers:
      - name: backend
        image: eli-lilly-qc:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: connection-string
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: alcoa-backend
  namespace: eli-lilly-qc
spec:
  type: ClusterIP
  ports:
  - port: 8000
    targetPort: 8000
  selector:
    app: alcoa-backend
```

### Nginx Production Configuration

```nginx
upstream backend {
    server backend:8000;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Compression
    gzip on;
    gzip_types text/plain text/css text/javascript application/json;
    gzip_min_length 1000;

    # Static files
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
        expires 1h;
        add_header Cache-Control "public, max-age=3600";
    }

    # API proxy
    location /api {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/m;
    location /api {
        limit_req zone=api_limit burst=200;
    }
}
```

### Database Migration to PostgreSQL

#### 1. Export SQLite data
```bash
sqlite3 alcoa_qc.db .dump > backup.sql
```

#### 2. Create PostgreSQL database
```bash
createdb -U postgres alcoa_db
```

#### 3. Update connection string
```python
# In main.py
DATABASE_URL = "postgresql://user:password@localhost/alcoa_db"
```

#### 4. Migrate schema
```bash
alembic upgrade head
```

### Backup & Recovery

#### Daily Backup Script
```bash
#!/bin/bash
BACKUP_DIR="/backups/alcoa"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="alcoa_db"

# PostgreSQL backup
pg_dump -U postgres $DB_NAME | gzip > $BACKUP_DIR/alcoa_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/alcoa_$DATE.sql.gz"
```

#### Restore Backup
```bash
gunzip -c alcoa_20240101_120000.sql.gz | psql -U postgres alcoa_db
```

### Monitoring & Logging

#### Setup ELK Stack (Elasticsearch, Logstash, Kibana)
```yaml
# logstash.conf
input {
  file {
    path => "/app/logs/*.log"
    start_position => "beginning"
  }
}

filter {
  json {
    source => "message"
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "alcoa-%{+YYYY.MM.dd}"
  }
}
```

#### Prometheus Metrics
```python
from prometheus_client import Counter, Histogram

# Track API requests
request_count = Counter(
    'alcoa_requests_total',
    'Total API requests',
    ['method', 'endpoint']
)

request_duration = Histogram(
    'alcoa_request_duration_seconds',
    'API request duration',
    ['endpoint']
)
```

### Performance Optimization

#### 1. Database Indexing
```python
# Add indexes for common queries
db.execute("""
    CREATE INDEX idx_batch_number ON qa_records(batch_number);
    CREATE INDEX idx_status ON qa_records(status);
    CREATE INDEX idx_created_at ON qa_records(created_at);
    CREATE INDEX idx_audit_record_id ON audit_logs(qa_record_id);
""")
```

#### 2. Caching
```python
from fastapi_cache2 import FastAPICache2
from fastapi_cache2.backends.redis import RedisBackend

@app.get("/api/compliance/status")
@cached(namespace="compliance", expire=300)
async def compliance_status():
    # This result is cached for 5 minutes
    pass
```

#### 3. Query Optimization
```python
# Use select() with joinedload for eager loading
stmt = select(QARecord).options(joinedload(QARecord.audit_logs))
records = db.execute(stmt).unique().scalars().all()
```

### Health Checks & Monitoring

#### Add health endpoint
```python
@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "database": "connected"
        }
    except:
        return {"status": "unhealthy"}
```

### Compliance & Auditing

#### 1. Audit Log Retention
```python
# Implement data retention policy
AUDIT_LOG_RETENTION_DAYS = 2555  # 7 years for pharma

# Archive old logs
def archive_old_logs():
    cutoff_date = datetime.utcnow() - timedelta(days=365)
    old_logs = db.query(AuditLog).filter(
        AuditLog.timestamp < cutoff_date
    ).all()
    # Export to secure storage
```

#### 2. Compliance Reports
```python
@app.get("/api/compliance/report")
async def generate_compliance_report(
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db)
):
    # Generate 21 CFR Part 11 compliance report
    pass
```

### Disaster Recovery

#### RTO/RPO Goals
- Recovery Time Objective (RTO): 1 hour
- Recovery Point Objective (RPO): 1 hour

#### Failover Setup
- Database replication
- Multi-region deployment
- Load balancing across regions
- Automated failover

---

**Production deployment ensures compliance and reliability for enterprise QA operations.**
