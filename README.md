# Python API with Node-RED Integration

A FastAPI-based backend service that communicates with Node-RED to fetch and serve data to frontend applications.

## Features

- **FastAPI Framework**: Modern, fast web framework for building APIs
- **Node-RED Integration**: Built-in HTTP client for communicating with Node-RED endpoints
- **Async Support**: Fully asynchronous request handling for better performance
- **CORS Enabled**: Ready for frontend integration (React, Vue, etc.)
- **Error Handling**: Comprehensive error handling and logging
- **Configurable**: Environment-based configuration

## Project Structure

```
pythonapi/
├── main.py              # Main FastAPI application
├── config.py            # Configuration settings
├── utils.py             # Node-RED client utilities
├── requirements.txt     # Python dependencies
├── start_api.py         # Server start script
└── README.md           # This file
```

## Installation

1. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Configure Node-RED URL (optional):**
   Set environment variable if your Node-RED runs on a different URL:
   ```bash
   export NODE_RED_URL="http://localhost:1880"
   ```

## Running the API

### Option 1: Using the start script
```bash
python3 start_api.py
```

### Option 2: Using uvicorn directly
```bash
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: http://localhost:8000

## API Endpoints

### Health Check
- `GET /` - Basic API status
- `GET /api/health` - Detailed health check including Node-RED connection

### Generic Node-RED Communication
- `GET /api/data/{endpoint}` - Fetch data from Node-RED endpoint
- `POST /api/data/{endpoint}` - Send data to Node-RED endpoint

### Example Endpoints
- `GET /api/sensors` - Get sensor data from Node-RED
- `GET /api/devices` - Get device status from Node-RED

## Configuration

The API uses environment variables for configuration:

| Variable | Default | Description |
|----------|---------|-------------|
| `NODE_RED_URL` | `http://localhost:1880` | Node-RED base URL |
| `NODE_RED_TIMEOUT` | `30` | Request timeout in seconds |
| `API_HOST` | `0.0.0.0` | API server host |
| `API_PORT` | `8000` | API server port |
| `LOG_LEVEL` | `INFO` | Logging level |
| `DEBUG` | `true` | Enable debug mode |

## Node-RED Setup

Your Node-RED flows should expose HTTP endpoints that this API can communicate with. Example Node-RED endpoints:

- `/sensors` - Return sensor data
- `/devices` - Return device status
- `/control` - Accept control commands
- `/data` - Generic data endpoint

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Example Usage

### Fetch sensor data
```bash
curl http://localhost:8000/api/sensors
```

### Send control command
```bash
curl -X POST http://localhost:8000/api/data/control \\
  -H "Content-Type: application/json" \\
  -d '{"device": "light1", "action": "on"}'
```

### Check health
```bash
curl http://localhost:8000/api/health
```

## Frontend Integration

The API is configured with CORS to allow requests from:
- `http://localhost:3000` (React development server)
- `http://127.0.0.1:3000`
- `http://localhost:3001`

## Development

### Adding New Endpoints

1. **Add endpoint to main.py:**
   ```python
   @app.get("/api/your-endpoint")
   async def your_function():
       data = await node_red_client.get_data("your-node-red-endpoint")
       return {"success": True, "data": data}
   ```

2. **Update Node-RED endpoints in config.py** if needed

### Error Handling

The API includes comprehensive error handling:
- HTTP 502: Node-RED communication errors
- HTTP 503: Service unavailable
- HTTP 500: Internal server errors

## Logs

The API logs all Node-RED communication and errors. Check console output for debugging information.

## Next Steps

1. **Set up Node-RED flows** with appropriate HTTP endpoints
2. **Create React frontend** to consume this API
3. **Add authentication** if needed
4. **Add database integration** for data persistence
5. **Deploy to production** server

## Troubleshooting

### "Node-RED connection failed"
- Check if Node-RED is running on the configured URL
- Verify Node-RED HTTP endpoints are accessible
- Check firewall settings

### "Import errors"
- Ensure all dependencies are installed: `pip3 install -r requirements.txt`
- Check Python version (requires Python 3.7+)
