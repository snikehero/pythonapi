import os
from typing import Optional

class Settings:
    """Application settings and configuration"""
    
    # Node-RED Configuration
    NODE_RED_BASE_URL: str = os.getenv("NODE_RED_URL", "http://localhost:1880")
    NODE_RED_TIMEOUT: int = int(os.getenv("NODE_RED_TIMEOUT", "30"))  # seconds
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # CORS Settings
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",  # Alternative React port
    ]
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Development mode
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    def __init__(self):
        """Initialize settings and validate configuration"""
        self.validate_config()
    
    def validate_config(self):
        """Validate configuration settings"""
        if not self.NODE_RED_BASE_URL:
            raise ValueError("NODE_RED_URL must be set")
        
        if self.NODE_RED_TIMEOUT <= 0:
            raise ValueError("NODE_RED_TIMEOUT must be positive")
        
        if self.API_PORT <= 0 or self.API_PORT > 65535:
            raise ValueError("API_PORT must be between 1 and 65535")

# Global settings instance
settings = Settings()

# Environment-specific configurations
def get_node_red_endpoints():
    """
    Define Node-RED endpoints that this API will communicate with
    Modify this based on your Node-RED flow endpoints
    """
    return {
        "sensors": "/sensors",
        "devices": "/devices", 
        "status": "/status",
        "control": "/control",
        "data": "/data"
    }

def get_api_info():
    """Get API information for documentation"""
    return {
        "title": "Python API with Node-RED Integration",
        "version": "1.0.0",
        "description": "API that communicates with Node-RED to fetch and serve data to frontend",
        "node_red_url": settings.NODE_RED_BASE_URL,
        "api_url": f"http://{settings.API_HOST}:{settings.API_PORT}"
    }
