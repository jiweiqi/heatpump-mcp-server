"""
MCP resources for HeatPumpHQ server information
"""

import requests
from .config import API_BASE_URL, API_TIMEOUT


def get_api_status() -> str:
    """Get the current status of the HeatPumpHQ API"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=API_TIMEOUT)
        if response.status_code == 200:
            return f"✅ HeatPumpHQ API is healthy (HTTP {response.status_code})"
        else:
            return f"⚠️ HeatPumpHQ API returned HTTP {response.status_code}"
    except Exception as e:
        return f"❌ HeatPumpHQ API is unreachable: {str(e)}"


def get_available_endpoints() -> str:
    """List all available HeatPumpHQ API endpoints"""
    endpoints = [
        "🏠 quick_sizer - Calculate required BTU capacity based on home characteristics",
        "💰 bill_estimator - Estimate costs, savings, and payback period vs current heating",
        "❄️ cold_climate_check - Verify heat pump performance in cold climate conditions",
        "🔧 project_cost_estimator - Calculate total project cost including complexity factors",
        "",
        f"📡 API Base URL: {API_BASE_URL}",
        "📋 All tools support standard home parameters (ZIP, square feet, build year)",
        "🎯 Designed for residential heat pump sizing and cost analysis"
    ]
    return "\n".join(endpoints)