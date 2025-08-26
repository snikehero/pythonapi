import httpx
import logging
from typing import Dict, Any, Optional
import json
from config import settings

logger = logging.getLogger(__name__)

class NodeRedClient:
    """Client for communicating with Node-RED HTTP endpoints"""
    
    def __init__(self, base_url: str):
        """
        Initialize Node-RED client
        
        Args:
            base_url: Base URL of Node-RED instance (e.g., http://localhost:1880)
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = settings.NODE_RED_TIMEOUT
        
        # Configure HTTP client
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'PythonAPI-NodeRED-Client/1.0'
            }
        )
    
    async def check_connection(self) -> Dict[str, Any]:
        """
        Check if Node-RED is reachable
        
        Returns:
            Dict with connection status information
        """
        try:
            response = await self.client.get(f"{self.base_url}/")
            if response.status_code == 200:
                return {
                    "status": "connected",
                    "message": "Node-RED is reachable",
                    "url": self.base_url
                }
            else:
                return {
                    "status": "error",
                    "message": f"Node-RED responded with status {response.status_code}",
                    "url": self.base_url
                }
        except httpx.ConnectError:
            return {
                "status": "disconnected",
                "message": "Cannot connect to Node-RED",
                "url": self.base_url
            }
        except Exception as e:
            logger.error(f"Error checking Node-RED connection: {e}")
            return {
                "status": "error",
                "message": f"Connection check failed: {str(e)}",
                "url": self.base_url
            }
    
    async def get_data(self, endpoint: str, params: Optional[str] = None) -> Dict[str, Any]:
        """
        Get data from Node-RED endpoint
        
        Args:
            endpoint: The endpoint path (without leading slash)
            params: Optional query parameters
            
        Returns:
            Data returned from Node-RED
            
        Raises:
            httpx.HTTPError: If the request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        if params:
            url += f"?{params}"
        
        logger.info(f"Getting data from Node-RED: {url}")
        
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            
            # Try to parse JSON response
            try:
                return response.json()
            except json.JSONDecodeError:
                # If not JSON, return text response
                return {"data": response.text}
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from Node-RED: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error to Node-RED: {e}")
            raise
    
    async def send_data(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send data to Node-RED endpoint via POST
        
        Args:
            endpoint: The endpoint path (without leading slash)
            payload: Data to send to Node-RED
            
        Returns:
            Response from Node-RED
            
        Raises:
            httpx.HTTPError: If the request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        logger.info(f"Sending data to Node-RED: {url}")
        logger.debug(f"Payload: {payload}")
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            # Try to parse JSON response
            try:
                return response.json()
            except json.JSONDecodeError:
                # If not JSON, return text response
                return {"response": response.text, "status_code": response.status_code}
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from Node-RED: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error to Node-RED: {e}")
            raise
    
    async def put_data(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update data in Node-RED endpoint via PUT
        
        Args:
            endpoint: The endpoint path (without leading slash)
            payload: Data to update in Node-RED
            
        Returns:
            Response from Node-RED
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        logger.info(f"Updating data in Node-RED: {url}")
        
        try:
            response = await self.client.put(url, json=payload)
            response.raise_for_status()
            
            try:
                return response.json()
            except json.JSONDecodeError:
                return {"response": response.text, "status_code": response.status_code}
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from Node-RED: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error to Node-RED: {e}")
            raise
    
    async def delete_data(self, endpoint: str) -> Dict[str, Any]:
        """
        Delete data from Node-RED endpoint via DELETE
        
        Args:
            endpoint: The endpoint path (without leading slash)
            
        Returns:
            Response from Node-RED
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        logger.info(f"Deleting data from Node-RED: {url}")
        
        try:
            response = await self.client.delete(url)
            response.raise_for_status()
            
            try:
                return response.json()
            except json.JSONDecodeError:
                return {"response": response.text, "status_code": response.status_code}
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from Node-RED: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error to Node-RED: {e}")
            raise
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

# Helper functions
async def test_node_red_connection(base_url: str) -> bool:
    """
    Test if Node-RED is accessible
    
    Args:
        base_url: Node-RED base URL
        
    Returns:
        True if Node-RED is accessible, False otherwise
    """
    client = NodeRedClient(base_url)
    try:
        result = await client.check_connection()
        return result["status"] == "connected"
    except Exception as e:
        logger.error(f"Error testing Node-RED connection: {e}")
        return False
    finally:
        await client.close()

def format_node_red_response(data: Any, endpoint: str) -> Dict[str, Any]:
    """
    Format Node-RED response for consistent API output
    
    Args:
        data: Raw data from Node-RED
        endpoint: The endpoint that was called
        
    Returns:
        Formatted response dictionary
    """
    return {
        "success": True,
        "data": data,
        "source": "node-red",
        "endpoint": endpoint,
        "timestamp": "2025-08-26T00:42:45Z"
    }
