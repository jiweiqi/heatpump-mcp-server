"""
API client for HeatPumpHQ backend services
"""

import logging
import requests
from typing import Dict
from mcp import McpError
from mcp.types import ErrorData

from .config import API_BASE_URL, API_KEY, API_TIMEOUT

logger = logging.getLogger(__name__)


def make_api_request(endpoint: str, data: dict) -> dict:
    """Make a request to the HeatPumpHQ API"""
    url = f"{API_BASE_URL}/api/{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=API_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        error_data = ErrorData(code=-1, message=f"Failed to call HeatPumpHQ API: {str(e)}")
        raise McpError(error_data)


def check_api_health() -> dict:
    """Check the health of the HeatPumpHQ API"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=API_TIMEOUT)
        return {
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text
        }
    except requests.exceptions.RequestException as e:
        return {
            "status_code": 0,
            "error": str(e)
        }