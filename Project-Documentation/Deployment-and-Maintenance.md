# Deployment and Maintenance Guide

This guide covers production deployment strategies, monitoring, maintenance procedures, and operational best practices for the AI Triage System.

## Deployment Options

### 1. Docker Compose Deployment (Recommended)

#### Production Docker Compose Setup

**File: `docker-compose.prod.yml`**
```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: unless-stopped
    env_file:
      - ./backend/.env.production
    ports:
      - "9001:9001"
    environment:
      - TTS_SERVICE_URL=http://106.201.228.100:9003
      - ROOT_PATH=/intelligent-triage
      - PROXY_DOMAIN=https://your-domain.com
    volumes:
      - ./backend/responses:/app/responses
      - ./backend/uploads:/app/uploads
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9001/docs"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    restart: unless-stopped
    ports:
      - "8010:80"
    environment:
      - NEXT_PUBLIC_BACKEND_URL=https://your-domain.com
      - NEXT_PUBLIC_API_BASE_PATH=/intelligent-triage
    depends_on:
      - backend
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - frontend
      - backend

  redis:
    image: redis:alpine
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

volumes:
  redis_data:
```

#### Deployment Commands

```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# Update deployment
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d --force-recreate

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale backend=3

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 2. Kubernetes Deployment

#### Kubernetes Manifests

**Namespace:**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ai-triage
```

**ConfigMap:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ai-triage-config
  namespace: ai-triage
data:
  ROOT_PATH: "/intelligent-triage"
  TTS_SERVICE_URL: "http://106.201.228.100:9003"
  PROXY_DOMAIN: "https://your-domain.com"
```

**Secret:**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: ai-triage-secrets
  namespace: ai-triage
type: Opaque
data:
  GEMINI_API_KEY: <base64-encoded-key>
  MURF_API_KEY: <base64-encoded-key>
```

**Backend Deployment:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-triage-backend
  namespace: ai-triage
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-triage-backend
  template:
    metadata:
      labels:
        app: ai-triage-backend
    spec:
      containers:
      - name: backend
        image: ai-triage/backend:latest
        ports:
        - containerPort: 9001
        env:
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: ai-triage-secrets
              key: GEMINI_API_KEY
        - name: ROOT_PATH
          valueFrom:
            configMapKeyRef:
              name: ai-triage-config
              key: ROOT_PATH
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /docs
            port: 9001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /tts/health
            port: 9001
          initialDelaySeconds: 5
          periodSeconds: 5
```

**Service:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: ai-triage-backend-service
  namespace: ai-triage
spec:
  selector:
    app: ai-triage-backend
  ports:
  - protocol: TCP
    port: 9001
    targetPort: 9001
  type: ClusterIP
```

**Ingress:**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ai-triage-ingress
  namespace: ai-triage
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /$2
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - your-domain.com
    secretName: ai-triage-tls
  rules:
  - host: your-domain.com
    http:
      paths:
      - path: /intelligent-triage(/|$)(.*)
        pathType: Prefix
        backend:
          service:
            name: ai-triage-frontend-service
            port:
              number: 80
      - path: /intelligent-triage/api(/|$)(.*)
        pathType: Prefix
        backend:
          service:
            name: ai-triage-backend-service
            port:
              number: 9001
```

### 3. Cloud Platform Deployment

#### AWS ECS Deployment

**Task Definition:**
```json
{
  "family": "ai-triage",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "your-account.dkr.ecr.region.amazonaws.com/ai-triage-backend:latest",
      "portMappings": [
        {
          "containerPort": 9001,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ROOT_PATH",
          "value": "/intelligent-triage"
        }
      ],
      "secrets": [
        {
          "name": "GEMINI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:ai-triage/gemini-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/ai-triage",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### Google Cloud Run Deployment

```bash
# Build and push image
gcloud builds submit --tag gcr.io/PROJECT-ID/ai-triage-backend

# Deploy to Cloud Run
gcloud run deploy ai-triage-backend \
  --image gcr.io/PROJECT-ID/ai-triage-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ROOT_PATH=/intelligent-triage \
  --set-secrets GEMINI_API_KEY=gemini-key:latest
```

## Environment Configuration

### Production Environment Variables

**Backend (.env.production):**
```env
# API Keys
GEMINI_API_KEY=your_production_gemini_key
MURF_API_KEY=your_production_murf_key
MODEL_NAME=gemini-2.5-flash

# Service Configuration
TTS_SERVICE_URL=http://106.201.228.100:9003
ROOT_PATH=/intelligent-triage
PROXY_DOMAIN=https://your-domain.com

# Performance Settings
WORKERS=4
MAX_SESSIONS=1000
SESSION_TIMEOUT=3600

# Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/backend.log

# Security
CORS_ORIGINS=https://your-domain.com
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

**Frontend (.env.production):**
```env
NEXT_PUBLIC_BACKEND_URL=https://your-domain.com
NEXT_PUBLIC_API_BASE_PATH=/intelligent-triage
NEXT_PUBLIC_ENVIRONMENT=production
NEXT_PUBLIC_ANALYTICS_ID=your_analytics_id
```

### SSL/TLS Configuration

**Nginx SSL Configuration:**
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;

    location /intelligent-triage/ {
        proxy_pass http://frontend:80/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /intelligent-triage/api/ {
        proxy_pass http://backend:9001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Monitoring and Observability

### Health Checks

**Backend Health Endpoints:**
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": {
            "gemini_api": await check_gemini_health(),
            "tts_service": await check_tts_health()
        }
    }

@app.get("/metrics")
async def metrics():
    return {
        "active_sessions": len(sessions),
        "total_requests": request_counter,
        "average_response_time": avg_response_time,
        "error_rate": error_rate
    }
```

### Logging Configuration

**Structured Logging:**
```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if hasattr(record, 'session_id'):
            log_entry['session_id'] = record.session_id
            
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
            
        return json.dumps(log_entry)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler('/app/logs/backend.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler('/app/logs/backend.log'))
```

### Monitoring Stack

**Prometheus Configuration:**
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'ai-triage-backend'
    static_configs:
      - targets: ['backend:9001']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'ai-triage-frontend'
    static_configs:
      - targets: ['frontend:80']
    metrics_path: '/metrics'
    scrape_interval: 30s
```

**Grafana Dashboard:**
```json
{
  "dashboard": {
    "title": "AI Triage System",
    "panels": [
      {
        "title": "Active Sessions",
        "type": "stat",
        "targets": [
          {
            "expr": "ai_triage_active_sessions"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "ai_triage_response_time_seconds"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(ai_triage_errors_total[5m])"
          }
        ]
      }
    ]
  }
}
```

### Alerting Rules

**Prometheus Alerts:**
```yaml
groups:
  - name: ai-triage-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(ai_triage_errors_total[5m]) > 0.1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors per second"

      - alert: ServiceDown
        expr: up{job="ai-triage-backend"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "AI Triage Backend is down"
          description: "Backend service has been down for more than 1 minute"

      - alert: HighMemoryUsage
        expr: container_memory_usage_bytes{name="ai-triage-backend"} / container_spec_memory_limit_bytes > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Memory usage is above 80%"
```

## Backup and Recovery

### Data Backup Strategy

**Session Data Backup (if using Redis):**
```bash
#!/bin/bash
# backup-sessions.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/sessions"
REDIS_HOST="localhost"
REDIS_PORT="6379"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup Redis data
redis-cli -h $REDIS_HOST -p $REDIS_PORT --rdb $BACKUP_DIR/sessions_$DATE.rdb

# Compress backup
gzip $BACKUP_DIR/sessions_$DATE.rdb

# Clean old backups (keep 7 days)
find $BACKUP_DIR -name "*.rdb.gz" -mtime +7 -delete

echo "Backup completed: sessions_$DATE.rdb.gz"
```

**Configuration Backup:**
```bash
#!/bin/bash
# backup-config.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/config"
PROJECT_DIR="/app/ai-triage"

mkdir -p $BACKUP_DIR

# Backup configuration files
tar -czf $BACKUP_DIR/config_$DATE.tar.gz \
  $PROJECT_DIR/docker-compose.yml \
  $PROJECT_DIR/nginx.conf \
  $PROJECT_DIR/backend/.env.production \
  $PROJECT_DIR/frontend/.env.production

echo "Configuration backup completed: config_$DATE.tar.gz"
```

### Disaster Recovery Plan

**Recovery Procedures:**

1. **Service Restoration:**
```bash
# Stop current services
docker-compose down

# Restore from backup
tar -xzf /backups/config/config_latest.tar.gz -C /

# Restore session data (if using Redis)
redis-cli -h localhost -p 6379 --rdb /backups/sessions/sessions_latest.rdb

# Restart services
docker-compose up -d
```

2. **Database Migration (Future):**
```sql
-- Restore from SQL backup
psql -h localhost -U postgres -d ai_triage < /backups/db/ai_triage_backup.sql

-- Verify data integrity
SELECT COUNT(*) FROM sessions;
SELECT COUNT(*) FROM emr_data;
```

## Maintenance Procedures

### Regular Maintenance Tasks

**Daily Tasks:**
```bash
#!/bin/bash
# daily-maintenance.sh

# Check service health
docker-compose ps

# Clean up old logs
find /app/logs -name "*.log" -mtime +7 -delete

# Check disk space
df -h

# Monitor memory usage
free -h

# Check for security updates
apt list --upgradable
```

**Weekly Tasks:**
```bash
#!/bin/bash
# weekly-maintenance.sh

# Update Docker images
docker-compose pull

# Clean up unused Docker resources
docker system prune -f

# Rotate logs
logrotate /etc/logrotate.d/ai-triage

# Performance analysis
docker stats --no-stream

# Security scan
docker scan ai-triage/backend:latest
```

**Monthly Tasks:**
```bash
#!/bin/bash
# monthly-maintenance.sh

# Update system packages
apt update && apt upgrade -y

# Renew SSL certificates
certbot renew --nginx

# Performance optimization
docker-compose restart

# Backup verification
./verify-backups.sh

# Security audit
./security-audit.sh
```

### Performance Optimization

**Backend Optimization:**
```python
# Optimize session management
import asyncio
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_cached_response(query_hash: str):
    """Cache common responses."""
    pass

async def cleanup_expired_sessions():
    """Remove expired sessions."""
    current_time = datetime.utcnow()
    expired_sessions = [
        session_id for session_id, session in sessions.items()
        if (current_time - session.updated_at).seconds > SESSION_TIMEOUT
    ]
    
    for session_id in expired_sessions:
        del sessions[session_id]
```

**Database Optimization (Future):**
```sql
-- Index optimization
CREATE INDEX CONCURRENTLY idx_sessions_updated_at ON sessions(updated_at);
CREATE INDEX CONCURRENTLY idx_emr_emergency_flag ON emr_data(emergency_flag);

-- Query optimization
EXPLAIN ANALYZE SELECT * FROM sessions WHERE updated_at > NOW() - INTERVAL '1 hour';

-- Vacuum and analyze
VACUUM ANALYZE sessions;
VACUUM ANALYZE emr_data;
```

### Security Maintenance

**Security Updates:**
```bash
#!/bin/bash
# security-updates.sh

# Update base images
docker pull python:3.12-slim
docker pull node:18-alpine
docker pull nginx:alpine

# Rebuild with security patches
docker-compose build --no-cache

# Scan for vulnerabilities
docker scan ai-triage/backend:latest
docker scan ai-triage/frontend:latest

# Update dependencies
cd backend && pip-audit
cd frontend && npm audit
```

**Access Control Review:**
```bash
#!/bin/bash
# access-review.sh

# Review nginx access logs
tail -n 1000 /var/log/nginx/access.log | grep -E "(40[0-9]|50[0-9])"

# Check for suspicious activity
grep -E "(sql|script|alert)" /app/logs/backend.log

# Review API key usage
grep "GEMINI_API_KEY" /app/logs/backend.log | tail -n 100
```

## Scaling Strategies

### Horizontal Scaling

**Load Balancer Configuration:**
```nginx
upstream backend_servers {
    server backend1:9001;
    server backend2:9001;
    server backend3:9001;
}

server {
    location /intelligent-triage/api/ {
        proxy_pass http://backend_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Auto-scaling with Docker Swarm:**
```yaml
version: '3.8'
services:
  backend:
    image: ai-triage/backend:latest
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
```

### Vertical Scaling

**Resource Allocation:**
```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

This deployment and maintenance guide provides comprehensive coverage for operating the AI Triage System in production environments. Regular monitoring, maintenance, and security updates are essential for reliable operation.