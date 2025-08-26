# Node-RED HTTP Endpoints Setup Guide

This guide will help you set up HTTP endpoints in your Docker-based Node-RED installation that work seamlessly with your Python API.

## 📋 Available Endpoints

The provided flow creates these HTTP endpoints:

| Method | Endpoint | Description | Response Type |
|--------|----------|-------------|---------------|
| GET    | `/sensors` | Returns mock sensor data (temperature, humidity, light, motion) | JSON |
| GET    | `/devices` | Returns device status (lights, thermostat, fan, camera) | JSON |
| POST   | `/control` | Accepts device control commands | JSON |
| GET    | `/status` | Returns system status and statistics | JSON |
| GET    | `/data` | Returns generic measurement data | JSON |
| POST   | `/data` | Stores incoming data | JSON |

## 🚀 Quick Setup

### Step 1: Access Node-RED
1. Open your browser and go to your Node-RED Docker instance (usually http://localhost:1880)
2. Log in if authentication is enabled

### Step 2: Import the Flow
1. Click the hamburger menu (☰) in the top-right corner
2. Select **Import**
3. Click **select a file to import**
4. Choose the `node-red-flows.json` file from this directory
5. Click **Import**

### Step 3: Deploy
1. Click the **Deploy** button in the top-right corner
2. Your endpoints are now active!

## 📊 Endpoint Details

### GET /sensors
Returns real-time sensor data with random values:
```json
{
  "timestamp": "2025-08-26T00:52:47Z",
  "sensors": [
    {
      "id": "temp_01",
      "name": "Temperature Sensor 1",
      "type": "temperature",
      "value": 23.45,
      "unit": "°C",
      "status": "online",
      "location": "Living Room"
    },
    {
      "id": "humid_01",
      "name": "Humidity Sensor 1", 
      "type": "humidity",
      "value": 65.2,
      "unit": "%",
      "status": "online",
      "location": "Living Room"
    }
    // ... more sensors
  ],
  "total_sensors": 4,
  "active_sensors": 4
}
```

### GET /devices
Returns current device statuses:
```json
{
  "timestamp": "2025-08-26T00:52:47Z",
  "devices": [
    {
      "id": "light_living_room",
      "name": "Living Room Light",
      "type": "light",
      "status": "on",
      "brightness": 75,
      "color": "#FFFFFF",
      "location": "Living Room",
      "power_consumption": 15
    }
    // ... more devices
  ],
  "total_devices": 4,
  "online_devices": 4,
  "system_status": "normal"
}
```

### POST /control
Accepts device control commands:

**Request:**
```json
{
  "device": "light_living_room",
  "action": "on",
  "brightness": 80
}
```

**Response:**
```json
{
  "timestamp": "2025-08-26T00:52:47Z",
  "status": "success",
  "message": "Device light_living_room turned on successfully with brightness set to 80%",
  "device_id": "light_living_room",
  "action_performed": "on",
  "brightness": 80,
  "new_state": "on"
}
```

### GET /status
Returns system status:
```json
{
  "timestamp": "2025-08-26T00:52:47Z",
  "system": {
    "status": "online",
    "uptime": 3600,
    "version": "1.0.0",
    "node_red_version": "3.1.0"
  },
  "statistics": {
    "total_requests": 1234,
    "active_connections": 5,
    "memory_usage": 45,
    "cpu_usage": 25
  },
  "services": {
    "http_server": "running",
    "mqtt_broker": "running",
    "database": "connected",
    "file_system": "accessible"
  }
}
```

## 🧪 Testing the Endpoints

### Using curl (from terminal):

```bash
# Test sensor data
curl http://localhost:1880/sensors

# Test device status
curl http://localhost:1880/devices

# Test control command
curl -X POST http://localhost:1880/control \
  -H "Content-Type: application/json" \
  -d '{"device": "light_living_room", "action": "toggle"}'

# Test system status
curl http://localhost:1880/status

# Test generic data
curl http://localhost:1880/data
```

### Using your Python API:

```bash
# Test through Python API
python3 start_api.py

# In another terminal:
curl http://localhost:8000/api/sensors
curl http://localhost:8000/api/devices
curl -X POST http://localhost:8000/api/data/control \
  -H "Content-Type: application/json" \
  -d '{"device": "thermostat_main", "action": "on", "temperature": 22}'
```

## ⚙️ Customization

### Modify Sensor Data
1. Double-click the "Generate Sensor Data" function node
2. Edit the JavaScript code to customize:
   - Sensor types and IDs
   - Value ranges
   - Locations
   - Additional properties

### Add New Endpoints
1. Drag an "http in" node from the palette
2. Configure the URL and method
3. Add a function node to process the request
4. Connect an "http response" node
5. Deploy the changes

### Change Response Format
Edit the function nodes to modify the JSON response structure according to your needs.

## 🔧 Advanced Configuration

### Enable CORS (if needed)
Add this to the function nodes to handle CORS:
```javascript
msg.headers = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE",
    "Access-Control-Allow-Headers": "Content-Type"
};
```

### Add Authentication
1. Install the `node-red-contrib-httpauth` node
2. Add authentication nodes before your endpoints
3. Configure credentials as needed

### Database Integration
1. Install database nodes (e.g., `node-red-node-mysql`)
2. Replace mock data generation with real database queries
3. Add database connection configuration

## 🐛 Troubleshooting

### Endpoints Not Working
- Check that the flow is deployed
- Verify Node-RED is running on port 1880
- Check the Node-RED debug panel for errors

### Python API Can't Connect
- Ensure Node-RED Docker container exposes port 1880
- Check if there's a firewall blocking the connection
- Verify the NODE_RED_URL in your Python API config

### Getting 404 Errors
- Make sure the flow is imported correctly
- Check that all nodes are connected properly
- Verify the endpoint URLs match exactly

## 📝 Next Steps

1. **Replace Mock Data**: Connect real sensors and devices
2. **Add Persistence**: Store data in a database
3. **Add WebSocket Support**: For real-time updates
4. **Implement Authentication**: Secure your endpoints
5. **Add Logging**: Track API usage and errors
6. **Scale Up**: Add more device types and endpoints

## 🔗 Integration with Python API

Your Python API is already configured to work with these endpoints:

- `http://localhost:8000/api/sensors` → `http://localhost:1880/sensors`
- `http://localhost:8000/api/devices` → `http://localhost:1880/devices`
- `http://localhost:8000/api/data/control` → `http://localhost:1880/control`

The Python API adds additional features like:
- Error handling and retry logic
- Request/response logging
- CORS support for frontend integration
- Consistent API response format

## 🚀 Ready to Build Your Frontend!

With both the Python API and Node-RED endpoints running, you can now:
1. Start building your React frontend
2. Make API calls to `http://localhost:8000/api/*`
3. Display real-time sensor data and device controls
4. Send commands through the control endpoints

Your full-stack IoT application architecture is now complete! 🎉
