from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import logging
from typing import Dict, Any, Optional
from config import settings
from utils import NodeRedClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI instance
app = FastAPI(
    title="Python API with Node-RED Integration",
    description="API that communicates with Node-RED to fetch and serve data",
    version="1.0.0"
)

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Node-RED client
node_red_client = NodeRedClient(settings.NODE_RED_BASE_URL)

@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Python API is running",
        "status": "healthy",
        "node_red_url": settings.NODE_RED_BASE_URL
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test connection to Node-RED
        node_red_status = await node_red_client.check_connection()
        return {
            "api_status": "healthy",
            "node_red_status": node_red_status,
            "timestamp": "2025-08-26T00:42:45Z"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.get("/api/data/{endpoint}")
async def get_node_red_data(endpoint: str, params: Optional[str] = None):
    """
    Generic endpoint to fetch data from Node-RED
    
    Args:
        endpoint: The Node-RED endpoint to call
        params: Optional query parameters as string
    """
    try:
        data = await node_red_client.get_data(endpoint, params)
        return {
            "success": True,
            "data": data,
            "source": "node-red",
            "endpoint": endpoint
        }
    except httpx.HTTPError as e:
        logger.error(f"Error fetching data from Node-RED: {e}")
        raise HTTPException(status_code=502, detail="Failed to fetch data from Node-RED")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/data/{endpoint}")
async def send_node_red_data(endpoint: str, payload: Dict[str, Any]):
    """
    Send data to Node-RED endpoint
    
    Args:
        endpoint: The Node-RED endpoint to send data to
        payload: Data to send to Node-RED
    """
    try:
        response = await node_red_client.send_data(endpoint, payload)
        return {
            "success": True,
            "response": response,
            "message": f"Data sent to Node-RED endpoint: {endpoint}"
        }
    except httpx.HTTPError as e:
        logger.error(f"Error sending data to Node-RED: {e}")
        raise HTTPException(status_code=502, detail="Failed to send data to Node-RED")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/sensors")
async def get_sensor_data():
    """
    Example endpoint - get sensor data from Node-RED
    Assumes Node-RED has a /sensors endpoint
    """
    try:
        data = await node_red_client.get_data("sensors")
        return {
            "success": True,
            "sensors": data,
            "timestamp": "2025-08-26T00:42:45Z"
        }
    except Exception as e:
        logger.error(f"Error fetching sensor data: {e}")
        raise HTTPException(status_code=502, detail="Failed to fetch sensor data")

@app.get("/api/devices")
async def get_device_status():
    """
    Example endpoint - get device status from Node-RED
    Assumes Node-RED has a /devices endpoint
    """
    try:
        data = await node_red_client.get_data("devices")
        return {
            "success": True,
            "devices": data,
            "timestamp": "2025-08-26T00:42:45Z"
        }
    except Exception as e:
        logger.error(f"Error fetching device data: {e}")
        raise HTTPException(status_code=502, detail="Failed to fetch device data")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
