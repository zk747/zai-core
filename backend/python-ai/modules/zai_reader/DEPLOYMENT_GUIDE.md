# ZAI Reader - Deployment Guide

This guide covers deploying ZAI Reader in various production environments.

---

## 📋 Table of Contents

1. [Local Development](#local-development)
2. [Linux Server](#linux-server)
3. [Docker Container](#docker-container)
4. [Kubernetes](#kubernetes)
5. [Cloud Platforms](#cloud-platforms)
6. [Performance Tuning](#performance-tuning)
7. [Monitoring](#monitoring)
8. [Security](#security)

---

## Local Development

### Setup

```bash
# Clone repository
git clone <repo> && cd zai-reader

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

### Access

- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Linux Server

### Prerequisites

```bash
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev
sudo apt-get install -y libfitz-dev  # For PDF support
```

### Installation

```bash
# Create application directory
sudo mkdir -p /opt/zai-reader
cd /opt/zai-reader

# Download files
sudo git clone <repo> .

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Systemd Service

**File**: `/etc/systemd/system/zai-reader.service`

```ini
[Unit]
Description=ZAI Reader API Service
After=network.target
Documentation=https://example.com/docs

[Service]
Type=simple
User=zai-reader
Group=zai-reader
WorkingDirectory=/opt/zai-reader
Environment="PATH=/opt/zai-reader/venv/bin"
ExecStart=/opt/zai-reader/venv/bin/python3 /opt/zai-reader/app.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### Start Service

```bash
# Create user
sudo useradd -r -s /bin/false zai-reader

# Set permissions
sudo chown -R zai-reader:zai-reader /opt/zai-reader

# Enable and start service
sudo systemctl enable zai-reader
sudo systemctl start zai-reader

# Check status
sudo systemctl status zai-reader

# View logs
sudo journalctl -u zai-reader -f
```

### Nginx Reverse Proxy

**File**: `/etc/nginx/sites-available/zai-reader`

```nginx
upstream zai_reader_api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name zai-reader.example.com;

    location / {
        proxy_pass http://zai_reader_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeout for long scans
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
    }
}
```

### Enable Nginx

```bash
sudo ln -s /etc/nginx/sites-available/zai-reader /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Docker Container

### Dockerfile

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libfitz-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy files
COPY requirements.txt .
COPY zai_reader.py .
COPY app.py .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN useradd -m -u 1000 zai && chown -R zai:zai /app
USER zai

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/')"

# Run application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  zai-reader:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/data
      - ./logs:/app/logs
    environment:
      - LOG_LEVEL=INFO
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - zai-reader
    restart: unless-stopped
```

### Build and Run

```bash
# Build image
docker build -t zai-reader:latest .

# Run container
docker run -d \
  --name zai-reader \
  -p 8000:8000 \
  -v /data:/data \
  zai-reader:latest

# Check logs
docker logs -f zai-reader

# Using Docker Compose
docker-compose up -d
```

---

## Kubernetes

### Deployment YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: zai-reader
  namespace: default
spec:
  replicas: 3
  selector:
    matchLabels:
      app: zai-reader
  template:
    metadata:
      labels:
        app: zai-reader
    spec:
      containers:
      - name: zai-reader
        image: zai-reader:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
        volumeMounts:
        - name: data
          mountPath: /data
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: zai-reader-data

---
apiVersion: v1
kind: Service
metadata:
  name: zai-reader-service
spec:
  selector:
    app: zai-reader
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: zai-reader-data
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

### Deploy

```bash
# Create namespace
kubectl create namespace zai-reader

# Deploy application
kubectl apply -f deployment.yaml -n zai-reader

# Check status
kubectl get pods -n zai-reader

# View logs
kubectl logs -n zai-reader deployment/zai-reader
```

---

## Cloud Platforms

### AWS - EC2

```bash
# SSH into instance
ssh -i key.pem ubuntu@instance-ip

# Follow Linux Server setup above
```

### AWS - ECS

```bash
# Create ECR repository
aws ecr create-repository --repository-name zai-reader

# Build and push image
docker build -t zai-reader .
docker tag zai-reader:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/zai-reader:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/zai-reader:latest

# Create ECS task and service using AWS Console
```

### Google Cloud Run

```bash
# Build image
gcloud builds submit --tag gcr.io/PROJECT_ID/zai-reader

# Deploy
gcloud run deploy zai-reader \
  --image gcr.io/PROJECT_ID/zai-reader \
  --platform managed \
  --region us-central1 \
  --memory 512Mi \
  --timeout 300
```

### Azure Container Instances

```bash
# Create container registry
az acr create --resource-group mygroup --name zairegistry --sku Basic

# Build and push
az acr build --registry zairegistry --image zai-reader .

# Deploy
az container create \
  --resource-group mygroup \
  --name zai-reader \
  --image zairegistry.azurecr.io/zai-reader \
  --ports 8000 \
  --memory 0.5
```

---

## Performance Tuning

### Uvicorn Workers

```bash
# Determine CPU count
python -c "import multiprocessing; print(multiprocessing.cpu_count())"

# Run with multiple workers
uvicorn app:app --workers 4 --host 0.0.0.0 --port 8000
```

### Gunicorn Configuration

```ini
# gunicorn_config.py
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
keepalive = 5
timeout = 120
max_requests = 1000
max_requests_jitter = 50
```

```bash
gunicorn app:app -c gunicorn_config.py
```

### File Size Limits

Adjust max_file_size_mb in app.py:
```python
DocumentReader(max_file_size_mb=100)  # Increase for larger files
```

---

## Monitoring

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, make_wsgi_app
from fastapi import FastAPI

task_counter = Counter('zai_tasks_total', 'Total tasks')
processing_time = Histogram('zai_processing_seconds', 'Processing time')

app = FastAPI()

@app.post("/read-folder")
async def read_folder(...):
    task_counter.inc()
    ...
```

### Logging

Enable structured logging:
```python
import logging
import json

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter'
        }
    }
})
```

### Health Checks

```bash
# Simple health check
curl http://localhost:8000/

# Detailed status
curl http://localhost:8000/stats
```

---

## Security

### SSL/TLS

```nginx
server {
    listen 443 ssl http2;

    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # ... rest of config
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    return 301 https://$server_name$request_uri;
}
```

### API Authentication

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthCredentials = Depends(security)):
    token = credentials.credentials
    if token != "your-secret-token":
        raise HTTPException(status_code=403, detail="Invalid token")
    return token

@app.post("/read-folder")
async def read_folder(..., token: str = Depends(verify_token)):
    ...
```

### Rate Limiting

```bash
pip install slowapi

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/read-folder")
@limiter.limit("5/minute")
async def read_folder(...):
    ...
```

---

## Troubleshooting

### Check Service Status

```bash
sudo systemctl status zai-reader
sudo journalctl -u zai-reader -n 50
```

### Restart Service

```bash
sudo systemctl restart zai-reader
```

### Check Port Availability

```bash
sudo netstat -tlnp | grep 8000
```

### View Resource Usage

```bash
top
df -h
free -m
```

---

**Version**: 1.0.0  
**Last Updated**: 2024-01-15
