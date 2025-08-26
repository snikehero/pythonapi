# Python API with Node-RED Integration

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-009688.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-ready FastAPI backend service that seamlessly integrates with Node-RED for IoT and automation applications. Features automatic flow deployment, comprehensive documentation, and Docker containerization.

## ✨ Features

- 🚀 **FastAPI Framework** - Modern, fast, and async web framework
- 🔴 **Node-RED Integration** - Seamless HTTP communication with Node-RED flows
- 🐳 **Docker Ready** - Complete containerization with auto-deployment
- 📊 **Auto-Import Flows** - Automatically imports and deploys Node-RED flows on startup
- ⚡ **Async Support** - High-performance asynchronous request handling
- 🌐 **CORS Enabled** - Ready for frontend integration (React, Vue, Angular)
- 🛡️ **Error Handling** - Comprehensive error handling and logging
- 📚 **Auto Documentation** - Interactive API docs with Swagger/OpenAPI
- 🔧 **Configurable** - Environment-based configuration
- 🧪 **Testing** - Integrated testing suite and health checks

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone <your-repo-url>
cd pythonapi

# Start the complete stack (API + Node-RED with auto-imported flows)
docker-compose up -d --build

# Access the API
curl http://localhost:8000/api/health

# Access Node-RED
open http://localhost:1880
```

### Option 2: Local Development

```bash
# Install dependencies
pip3 install -r requirements.txt

# Copy environment template
cp .env.example .env

# Start the API
python3 start_api.py
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│                Frontend                     │
│            (React/Vue/Angular)              │
└─────────────────┬───────────────────────────┘
                  │ HTTP/REST
┌─────────────────▼───────────────────────────┐
│             Python FastAPI                  │
│         (Port 8000 - This Project)          │
└─────────────────┬───────────────────────────┘
                  │ HTTP
┌─────────────────▼───────────────────────────┐
│              Node-RED                       │
│     (Port 1880 - IoT/Automation Layer)      │
└─────────────────┬───────────────────────────┘
                  │ Various Protocols
┌─────────────────▼───────────────────────────┐
│            IoT Devices/Sensors               │
│        (MQTT, HTTP, Serial, etc.)           │
└─────────────────────────────────────────────┘
```

## 📁 Project Structure

```
pythonapi/
├── 🐍 Core Application
│   ├── main.py                  # FastAPI application
│   ├── config.py               # Configuration management
│   ├── utils.py                # Node-RED client utilities
│   └── start_api.py            # Application startup script
│
├── 🔴 Node-RED Integration
│   ├── flows.json              # Node-RED flows for auto-import
│   ├── auto-import-flows.py    # Automatic flow deployment
│   └── node-red-flows.json     # Alternative flow format
│
├── 🐳 Docker Configuration
│   ├── Dockerfile              # Container definition
│   ├── docker-compose.yml      # Multi-service orchestration
│   └── .dockerignore          # Docker build exclusions
│
├── 📚 Documentation
│   ├── README.md              # This file
│   ├── DOCKER.md              # Docker setup guide
│   └── NODE-RED-SETUP.md      # Node-RED configuration
│
├── 🧪 Testing & Configuration
│   ├── test_integration.py     # Integration tests
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example          # Environment variables template
│   └── .gitignore            # Git exclusions
│
└── 📄 Additional Files
    ├── LICENSE               # Project license
    └── .github/              # GitHub Actions (optional)
```

## 🌐 API Endpoints

### 🔍 Health & Status
- `GET /` - Basic API status
- `GET /api/health` - Detailed health check with Node-RED connectivity
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

### 🔄 Node-RED Communication
- `GET /api/data/{endpoint}` - Generic data fetching from Node-RED
- `POST /api/data/{endpoint}` - Send data to Node-RED endpoints

### 📊 IoT Endpoints (Auto-configured)
- `GET /api/sensors` - Sensor data (temperature, humidity, light, motion)
- `GET /api/devices` - Device status (lights, thermostats, cameras)
- `POST /api/data/control` - Device control commands
- `GET /api/data/status` - System status and statistics

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Default | Description |
|----------|---------|-------------|
| `NODE_RED_URL` | `http://localhost:1880` | Node-RED base URL |
| `NODE_RED_TIMEOUT` | `30` | Request timeout in seconds |
| `API_HOST` | `0.0.0.0` | API server host |
| `API_PORT` | `8000` | API server port |
| `DEBUG` | `true` | Enable debug mode |
| `LOG_LEVEL` | `INFO` | Logging level |
| `ALLOWED_ORIGINS` | `http://localhost:3000,...` | CORS allowed origins |

### Docker Configuration

The `docker-compose.yml` automatically:
- ✅ Starts Node-RED with persistent data
- ✅ Imports flows automatically on startup
- ✅ Configures network communication between services
- ✅ Sets up health checks and restart policies

## 📖 Usage Examples

### Basic Health Check
```bash
curl http://localhost:8000/api/health
```

### Fetch Sensor Data
```bash
curl http://localhost:8000/api/sensors
```

### Control Device
```bash
curl -X POST http://localhost:8000/api/data/control \
  -H "Content-Type: application/json" \
  -d '{
    "device": "light_living_room",
    "action": "on",
    "brightness": 80
  }'
```

### Integration with Frontend (JavaScript)
```javascript
// Fetch sensor data
const response = await fetch('http://localhost:8000/api/sensors');
const data = await response.json();
console.log(data.sensors);

// Control device
await fetch('http://localhost:8000/api/data/control', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    device: 'thermostat_main',
    action: 'on',
    temperature: 22
  })
});
```

## 🧪 Testing

### Manual Testing
```bash
# Test API endpoints
curl http://localhost:8000/
curl http://localhost:8000/api/sensors

# Test Node-RED direct access
curl http://localhost:1880/sensors
```

### Integration Testing
```bash
# Run comprehensive integration tests
python3 test_integration.py

# Or with Docker
docker-compose exec python-api python test_integration.py
```

## 🚀 Deployment

### Production Docker Deployment
```bash
# Build and deploy
docker-compose -f docker-compose.yml up -d --build

# Check service health
docker-compose ps
docker-compose logs -f python-api
```

### DockerHub Deployment
```bash
# Build and tag image
docker build -t yourusername/python-api:latest .

# Push to DockerHub
docker push yourusername/python-api:latest
```

### Environment-Specific Deployment
```bash
# Development
docker-compose up -d

# Production (with custom config)
cp .env.example .env.production
# Edit .env.production with production values
docker-compose --env-file .env.production up -d
```

## 🛠️ Development

### Adding New Endpoints

1. **Add to main.py:**
```python
@app.get("/api/your-endpoint")
async def your_endpoint():
    data = await node_red_client.get_data("your-node-red-endpoint")
    return {"success": True, "data": data}
```

2. **Add corresponding Node-RED flow**
3. **Update documentation**
4. **Add tests**

### Node-RED Flow Development

Flows are automatically imported from `flows.json`. To modify:

1. Edit flows in Node-RED UI
2. Export flows and save to `flows.json`
3. Restart services: `docker-compose restart`

### Local Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-asyncio black flake8

# Format code
black .

# Lint code
flake8 .

# Run tests
pytest
```

## 🔧 Troubleshooting

### Common Issues

#### Node-RED Connection Failed
```bash
# Check if Node-RED is running
docker-compose ps
curl http://localhost:1880

# Check container logs
docker-compose logs node-red
```

#### Flow Import Failed
```bash
# Check flow-importer logs
docker logs flow-importer

# Manually import flows
# Go to http://localhost:1880 → Import → flows.json
```

#### Port Already in Use
```bash
# Find process using port
lsof -i :8000  # API port
lsof -i :1880  # Node-RED port

# Kill process or use different ports in .env
```

### Debug Mode
```bash
# Enable debug logging
export DEBUG=true
export LOG_LEVEL=DEBUG

# Or in docker-compose.yml
DEBUG=true
LOG_LEVEL=DEBUG
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework
- [Node-RED](https://nodered.org/) - Low-code programming for IoT
- [Docker](https://www.docker.com/) - Containerization platform
- [Uvicorn](https://www.uvicorn.org/) - ASGI web server

## 📞 Support

- 📖 **Documentation**: Check the `docs/` directory
- 🐛 **Issues**: [GitHub Issues](../../issues)
- 💬 **Discussions**: [GitHub Discussions](../../discussions)
- 📧 **Email**: your-email@example.com

---

**⭐ If this project helped you, please give it a star!**
