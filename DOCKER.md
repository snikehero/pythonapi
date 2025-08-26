# Docker Setup Guide

This guide explains how to containerize and run your Python API + Node-RED backend using Docker.

## 📁 Docker Files

- **`Dockerfile`** - Container configuration for Python API
- **`docker-compose.yml`** - Orchestrates Python API + Node-RED services
- **`.dockerignore`** - Excludes files from Docker build context

## 🚀 Quick Start

### Option 1: Using Docker Compose (Recommended)

```bash
# Build and start both services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Option 2: Individual Docker Commands

```bash
# Build Python API image
docker build -t python-api .

# Run Python API container
docker run -d \
  --name python-api \
  -p 8000:8000 \
  -e NODE_RED_URL=http://host.docker.internal:1880 \
  python-api

# Run Node-RED container (if not already running)
docker run -d \
  --name node-red \
  -p 1880:1880 \
  -v node_red_data:/data \
  nodered/node-red:latest
```

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│           Docker Network            │
│                                     │
│  ┌─────────────┐  ┌─────────────┐   │
│  │Python API   │  │ Node-RED    │   │
│  │Port: 8000   │◄►│Port: 1880   │   │
│  │             │  │             │   │
│  └─────────────┘  └─────────────┘   │
│                                     │
└─────────────────────────────────────┘
         ▲                    ▲
         │                    │
    Port 8000              Port 1880
    (Python API)          (Node-RED)
```

## ⚙️ Configuration

### Environment Variables

The Python API container accepts these environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `NODE_RED_URL` | `http://node-red:1880` | Node-RED service URL |
| `API_HOST` | `0.0.0.0` | API server host |
| `API_PORT` | `8000` | API server port |
| `DEBUG` | `true` | Enable debug mode |
| `LOG_LEVEL` | `INFO` | Logging level |
| `NODE_RED_TIMEOUT` | `30` | Request timeout (seconds) |

### Docker Compose Override

Create `docker-compose.override.yml` for custom settings:

```yaml
version: '3.8'
services:
  python-api:
    environment:
      - DEBUG=false
      - LOG_LEVEL=WARNING
    ports:
      - "8080:8000"  # Custom port mapping
```

## 🧪 Testing

### Health Checks

Both services have built-in health checks:

```bash
# Check service health
docker-compose ps

# View health status
docker inspect python-api --format='{{.State.Health.Status}}'
docker inspect node-red --format='{{.State.Health.Status}}'
```

### Manual Testing

```bash
# Test Python API
curl http://localhost:8000/
curl http://localhost:8000/api/health

# Test Node-RED (after importing flows)
curl http://localhost:1880/sensors
curl http://localhost:1880/devices
```

### Integration Test

```bash
# Install test dependencies in container
docker-compose exec python-api pip install aiohttp

# Run integration test
docker-compose exec python-api python test_integration.py
```

## 📊 Management Commands

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f python-api
docker-compose logs -f node-red

# Last 50 lines
docker-compose logs --tail=50 python-api
```

### Service Management

```bash
# Start services
docker-compose start

# Stop services
docker-compose stop

# Restart specific service
docker-compose restart python-api

# Remove containers (keeps volumes)
docker-compose down

# Remove everything including volumes
docker-compose down -v
```

### Scaling

```bash
# Run multiple Python API instances
docker-compose up -d --scale python-api=3
```

## 💾 Data Persistence

### Node-RED Data

Node-RED flows and settings are persisted in a Docker volume:

```bash
# Backup Node-RED data
docker run --rm -v node-red-data:/data -v $(pwd):/backup \
  busybox tar czf /backup/node-red-backup.tar.gz -C /data .

# Restore Node-RED data
docker run --rm -v node-red-data:/data -v $(pwd):/backup \
  busybox tar xzf /backup/node-red-backup.tar.gz -C /data
```

### Application Logs

```bash
# Mount log directory
docker-compose up -d \
  -v ./logs:/app/logs
```

## 🔒 Security

### Production Considerations

1. **Use specific image tags** instead of `latest`
2. **Set resource limits**:

```yaml
services:
  python-api:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

3. **Use secrets for sensitive data**:

```yaml
services:
  python-api:
    secrets:
      - api_key
secrets:
  api_key:
    file: ./secrets/api_key.txt
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Connection Refused Between Services

```bash
# Check network connectivity
docker-compose exec python-api ping node-red

# Verify environment variables
docker-compose exec python-api env | grep NODE_RED_URL
```

#### 2. Port Already in Use

```bash
# Find process using port
lsof -i :8000
lsof -i :1880

# Use different ports
# Edit docker-compose.yml ports section
```

#### 3. Build Failures

```bash
# Clean build
docker-compose build --no-cache

# Check Dockerfile syntax
docker build -t test .
```

#### 4. Container Won't Start

```bash
# Check container logs
docker-compose logs python-api

# Debug with interactive shell
docker-compose run --rm python-api /bin/bash
```

### Debug Mode

```bash
# Run with debug output
docker-compose up --build

# Interactive debugging
docker-compose run --rm python-api python -c "
import asyncio
from utils import test_node_red_connection
print(asyncio.run(test_node_red_connection('http://node-red:1880')))
"
```

## 📦 Production Deployment

### Multi-stage Build

For production, consider a multi-stage Dockerfile:

```dockerfile
# Development stage
FROM python:3.9-slim as development
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM python:3.9-slim as production
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN adduser --disabled-password appuser && chown -R appuser:appuser /app
USER appuser
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment-specific Compose

```bash
# Development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 🚀 Next Steps

1. **Import Node-RED flows** using the provided `node-red-flows.json`
2. **Test the complete setup** with the integration test
3. **Configure your frontend** to connect to `http://localhost:8000`
4. **Set up CI/CD pipeline** for automated deployment
5. **Add monitoring** with tools like Prometheus/Grafana

Your containerized backend is now ready for development and deployment! 🎉
