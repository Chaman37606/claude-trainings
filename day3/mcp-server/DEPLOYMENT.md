# Deployment Guide - MCP Search Server

Complete guide for deploying the MCP Search Server to production environments.

## Table of Contents

1. [Cloud Platforms](#cloud-platforms)
2. [Docker Deployment](#docker-deployment)
3. [Environment Configuration](#environment-configuration)
4. [Monitoring & Logging](#monitoring--logging)
5. [Performance Optimization](#performance-optimization)
6. [Security Considerations](#security-considerations)
7. [Troubleshooting](#troubleshooting)

---

## Cloud Platforms

### AWS (Elastic Container Service)

#### Prerequisites
- AWS Account with ECS permissions
- ECR repository created
- CloudWatch configured

#### Deployment Steps

**1. Create ECR Repository**
```bash
aws ecr create-repository --repository-name mcp-search-server --region us-east-1
```

**2. Build and Push Image**
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build image
docker build -t mcp-search-server:latest .

# Tag image
docker tag mcp-search-server:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/mcp-search-server:latest

# Push to ECR
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/mcp-search-server:latest
```

**3. Create ECS Task Definition**
```json
{
  "family": "mcp-search-server",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "mcp-search-server",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/mcp-search-server:latest",
      "portMappings": [
        {
          "containerPort": 3001,
          "hostPort": 3001,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "MCP_PORT",
          "value": "3001"
        },
        {
          "name": "SEARCH_PROVIDER",
          "value": "duckduckgo"
        }
      ],
      "secrets": [
        {
          "name": "BRAVE_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:<account-id>:secret:mcp/brave-api-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/mcp-search-server",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

**4. Create ECS Service**
```bash
aws ecs create-service \
  --cluster mcp-cluster \
  --service-name mcp-search-server \
  --task-definition mcp-search-server \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

**5. Setup Load Balancer**
```bash
# Create target group
aws elbv2 create-target-group \
  --name mcp-search-tg \
  --protocol HTTP \
  --port 3001 \
  --vpc-id vpc-xxx

# Create load balancer
aws elbv2 create-load-balancer \
  --name mcp-search-lb \
  --subnets subnet-xxx subnet-yyy \
  --security-groups sg-xxx
```

### Google Cloud Platform (Cloud Run)

#### Prerequisites
- GCP Project with Cloud Run enabled
- gcloud CLI installed

#### Deployment Steps

**1. Build and Push to Container Registry**
```bash
# Enable required APIs
gcloud services enable cloudbuild.googleapis.com containerregistry.googleapis.com

# Build image
gcloud builds submit --tag gcr.io/PROJECT-ID/mcp-search-server

# Alternative: Build locally and push
docker build -t gcr.io/PROJECT-ID/mcp-search-server:latest .
docker push gcr.io/PROJECT-ID/mcp-search-server:latest
```

**2. Deploy to Cloud Run**
```bash
gcloud run deploy mcp-search-server \
  --image gcr.io/PROJECT-ID/mcp-search-server:latest \
  --platform managed \
  --region us-central1 \
  --memory 512Mi \
  --cpu 1 \
  --set-env-vars "MCP_PORT=8080,SEARCH_PROVIDER=duckduckgo" \
  --set-secrets "BRAVE_API_KEY=brave-key:latest" \
  --allow-unauthenticated
```

**3. Configure Custom Domain**
```bash
# Map custom domain
gcloud run domain-mappings create \
  --service mcp-search-server \
  --domain mcp.example.com \
  --platform managed \
  --region us-central1
```

### Azure (App Service)

#### Prerequisites
- Azure Account
- Azure CLI installed

#### Deployment Steps

**1. Create Resource Group**
```bash
az group create --name mcp-rg --location eastus
```

**2. Create Container Registry**
```bash
az acr create --resource-group mcp-rg --name mcpregistry --sku Basic
```

**3. Build and Push Image**
```bash
# Build in Azure
az acr build --registry mcpregistry --image mcp-search-server:latest .

# Or build locally
docker build -t mcp-search-server:latest .
docker tag mcp-search-server:latest mcpregistry.azurecr.io/mcp-search-server:latest
docker push mcpregistry.azurecr.io/mcp-search-server:latest
```

**4. Create App Service Plan**
```bash
az appservice plan create \
  --name mcp-plan \
  --resource-group mcp-rg \
  --is-linux \
  --sku B1
```

**5. Create Web App**
```bash
az webapp create \
  --resource-group mcp-rg \
  --plan mcp-plan \
  --name mcp-search-app \
  --deployment-container-image-name mcpregistry.azurecr.io/mcp-search-server:latest
```

---

## Docker Deployment

### Docker Standalone

**1. Build Image**
```bash
docker build -t mcp-search-server:v1.0.0 .
```

**2. Run Container**
```bash
docker run -d \
  --name mcp-server \
  -p 3001:3001 \
  -e MCP_PORT=3001 \
  -e SEARCH_PROVIDER=duckduckgo \
  -e BRAVE_API_KEY=$BRAVE_API_KEY \
  mcp-search-server:v1.0.0
```

**3. View Logs**
```bash
docker logs -f mcp-server
```

### Docker Compose (Recommended for Local/Staging)

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Kubernetes (Production)

**1. Create Namespace**
```bash
kubectl create namespace mcp-prod
```

**2. Create ConfigMap**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mcp-config
  namespace: mcp-prod
data:
  MCP_PORT: "3001"
  SEARCH_PROVIDER: "duckduckgo"
  UI_PORT: "3000"
```

**3. Create Secret**
```bash
kubectl create secret generic mcp-secrets \
  --from-literal=BRAVE_API_KEY=$BRAVE_API_KEY \
  -n mcp-prod
```

**4. Create Deployment**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-search-server
  namespace: mcp-prod
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcp-search-server
  template:
    metadata:
      labels:
        app: mcp-search-server
    spec:
      containers:
      - name: mcp-server
        image: <registry>/mcp-search-server:v1.0.0
        ports:
        - containerPort: 3001
        envFrom:
        - configMapRef:
            name: mcp-config
        - secretRef:
            name: mcp-secrets
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3001
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 3001
          initialDelaySeconds: 5
          periodSeconds: 5
```

**5. Create Service**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: mcp-search-service
  namespace: mcp-prod
spec:
  selector:
    app: mcp-search-server
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3001
  type: LoadBalancer
```

**6. Deploy**
```bash
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

# Check status
kubectl get pods -n mcp-prod
kubectl get svc -n mcp-prod
```

---

## Environment Configuration

### Environment Variables

```env
# Server Configuration
MCP_PORT=3001
UI_PORT=3000

# Search Provider (duckduckgo, google, bing, brave)
SEARCH_PROVIDER=duckduckgo

# API Keys (optional - enable premium features)
BRAVE_API_KEY=your_brave_api_key
GOOGLE_API_KEY=your_google_api_key
BING_API_KEY=your_bing_api_key
APIFY_API_TOKEN=your_apify_token

# Security
NODE_ENV=production
DEBUG=false

# Performance
MAX_WORKERS=4
CACHE_TTL=3600

# Monitoring
LOG_LEVEL=info
SENTRY_DSN=your_sentry_dsn
```

### Secrets Management

**AWS Secrets Manager**
```bash
aws secretsmanager create-secret \
  --name mcp/api-keys \
  --secret-string '{
    "brave_api_key": "key...",
    "google_api_key": "key..."
  }'
```

**GCP Secret Manager**
```bash
echo -n "api_key_value" | gcloud secrets create mcp-brave-api-key --data-file=-
```

**Azure Key Vault**
```bash
az keyvault secret set \
  --vault-name mcp-vault \
  --name brave-api-key \
  --value "key..."
```

---

## Monitoring & Logging

### CloudWatch (AWS)

**1. Create Log Group**
```bash
aws logs create-log-group --log-group-name /mcp/search-server
```

**2. Setup Alarms**
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name mcp-high-error-rate \
  --alarm-description "Alert when error rate > 5%" \
  --metric-name ErrorRate \
  --namespace MCP \
  --statistic Average \
  --period 300 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold
```

### Stackdriver (GCP)

```bash
# Create log sink
gcloud logging sinks create mcp-sink logging.googleapis.com/projects/PROJECT-ID/logs/mcp-server

# Create uptime check
gcloud monitoring uptime create --display-name="MCP Health" \
  --resource-type=uptime-url \
  --monitored-resource=url="https://mcp.example.com/health"
```

### Datadog Integration

```yaml
# deployment.yaml
env:
  - name: DD_TRACE_ENABLED
    value: "true"
  - name: DD_AGENT_HOST
    valueFrom:
      fieldRef:
        fieldPath: status.hostIP
```

---

## Performance Optimization

### Caching Strategy

```typescript
// Redis caching for search results
import Redis from 'redis';
const redis = new Redis();

async function cachedSearch(query: string) {
  const cacheKey = `search:${query}`;
  const cached = await redis.get(cacheKey);
  
  if (cached) return JSON.parse(cached);
  
  const results = await performSearch(query);
  await redis.setex(cacheKey, 3600, JSON.stringify(results));
  
  return results;
}
```

### Load Balancing

**NGINX Configuration**
```nginx
upstream mcp_backend {
    least_conn;
    server mcp-1:3001;
    server mcp-2:3001;
    server mcp-3:3001;
}

server {
    listen 80;
    server_name mcp.example.com;

    location / {
        proxy_pass http://mcp_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /health {
        access_log off;
        proxy_pass http://mcp_backend;
    }
}
```

### Rate Limiting

```typescript
import rateLimit from 'express-rate-limit';

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP'
});

app.use('/mcp/search', limiter);
```

---

## Security Considerations

### HTTPS/TLS

**Let's Encrypt with Certbot**
```bash
certbot certonly --standalone -d mcp.example.com
# Point to certificates in docker volume
```

### API Security

```typescript
// Add security headers
app.use(helmet());

// CORS Configuration
app.use(cors({
  origin: ['https://mcp.example.com', 'https://app.example.com'],
  credentials: true
}));

// Rate limiting
app.use(rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100
}));
```

### Input Validation

```typescript
// Validate search queries
const validateQuery = (query: string): boolean => {
  if (query.length > 500) return false;
  if (!/^[a-zA-Z0-9\s\-_.]+$/.test(query)) return false;
  return true;
};
```

### Environment Variables Security

Never commit `.env` files:
```bash
# .gitignore
.env
.env.local
.env.*.local
```

Use secrets management services instead.

---

## Troubleshooting

### High Memory Usage

```bash
# Check memory in container
docker exec mcp-server free -h

# Increase container memory limit
docker run -m 1g mcp-search-server
```

### Connection Timeouts

```bash
# Increase timeout in deployment
env:
  - name: TIMEOUT
    value: "30000"

# Check network connectivity
docker exec mcp-server curl -I http://google.com
```

### API Rate Limits

```bash
# Monitor rate limit hits
docker logs mcp-server | grep "429"

# Implement exponential backoff
async function searchWithRetry(query, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await search(query);
    } catch (error) {
      if (i < maxRetries - 1) {
        await sleep(Math.pow(2, i) * 1000);
      }
    }
  }
}
```

### Database Persistence

```yaml
# Add persistent volume for caching
volumes:
  - name: mcp-cache
    persistentVolumeClaim:
      claimName: mcp-cache-pvc
```

---

## Rollback Procedure

### Kubernetes Rollback

```bash
# Check rollout history
kubectl rollout history deployment/mcp-search-server

# Rollback to previous version
kubectl rollout undo deployment/mcp-search-server

# Rollback to specific revision
kubectl rollout undo deployment/mcp-search-server --to-revision=2
```

### Docker Rollback

```bash
# Stop current container
docker stop mcp-server

# Remove current image
docker rm mcp-server

# Run previous version
docker run -d --name mcp-server mcp-search-server:v1.0.0
```

---

## Scaling

### Horizontal Scaling

```bash
# Kubernetes - increase replicas
kubectl scale deployment/mcp-search-server --replicas=5

# Docker Compose - use multiple containers
docker-compose up -d --scale mcp-server=3
```

### Vertical Scaling

```yaml
# Kubernetes - increase resources
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "1Gi"
    cpu: "500m"
```

---

## Health Checks & Monitoring

### Health Endpoint

```bash
# Check server health
curl http://localhost:3001/health

# Response:
# {
#   "status": "healthy",
#   "mcp_version": "1.0.0",
#   "provider": "duckduckgo",
#   "timestamp": "2024-01-01T12:00:00Z"
# }
```

### Metrics Export

```typescript
// Prometheus metrics endpoint
app.get('/metrics', (req, res) => {
  res.set('Content-Type', 'text/plain');
  res.send(
    '# HELP mcp_search_requests_total Total search requests\n' +
    '# TYPE mcp_search_requests_total counter\n' +
    `mcp_search_requests_total{provider="${provider}"} ${totalRequests}`
  );
});
```

---

## Support & Documentation

- GitHub: https://github.com/your-org/mcp-search-server
- Issues: https://github.com/your-org/mcp-search-server/issues
- Documentation: See README.md, QUICKSTART.md, TESTING.md

For additional help, refer to cloud provider documentation:
- AWS ECS: https://docs.aws.amazon.com/ecs/
- Google Cloud Run: https://cloud.google.com/run/docs
- Azure App Service: https://docs.microsoft.com/azure/app-service/
- Kubernetes: https://kubernetes.io/docs/
