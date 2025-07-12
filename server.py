#!/usr/bin/env python3
"""
HeatPumpHQ MCP Server

An MCP server that provides access to HeatPumpHQ's heat pump calculation APIs.
This server exposes tools for quick sizing, bill estimation, cold climate checking,
and project cost estimation through the Model Context Protocol.
"""

import asyncio
import logging
import os
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
import requests
from pydantic import BaseModel, Field

from mcp.server.fastmcp import FastMCP
from mcp.server import McpError, types
from mcp.types import Tool

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
API_BASE_URL = os.getenv("HEATPUMP_API_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY")  # Optional

# Initialize MCP server
mcp = FastMCP("HeatPumpHQ")

# Pydantic models for input validation
class QuickSizerInput(BaseModel):
    zip_code: str = Field(..., description="5-digit US ZIP code")
    square_feet: int = Field(..., ge=100, le=10000, description="Home square footage (100-10000)")
    build_year: int = Field(..., ge=1900, le=2025, description="Year the home was built (1900-2025)")

class BillEstimatorInput(BaseModel):
    zip_code: str = Field(..., description="5-digit US ZIP code")
    total_heating_load: int = Field(..., description="Total heating load in BTU/hr")
    total_cooling_load: int = Field(..., description="Total cooling load in BTU/hr")
    current_system: str = Field(..., description="Current heating system (gas, electric, oil, propane)")
    home_size: int = Field(..., description="Home size in square feet")

class ColdClimateInput(BaseModel):
    zip_code: str = Field(..., description="5-digit US ZIP code")
    system_capacity: int = Field(..., description="Heat pump capacity in BTU/hr")
    backup_heat: str = Field(..., description="Backup heating type (electric, gas, none)")

class ProjectCostInput(BaseModel):
    zip_code: str = Field(..., description="5-digit US ZIP code")
    home_size: int = Field(..., description="Home size in square feet")
    building_age: str = Field(..., description="Building age category")
    system_type: str = Field(..., description="System type")
    installation_complexity: str = Field(..., description="Installation complexity level")
    hvac_experience: str = Field(..., description="HVAC contractor experience level")


def make_api_request(endpoint: str, data: dict) -> dict:
    """Make a request to the HeatPumpHQ API"""
    url = f"{API_BASE_URL}/api/{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        raise McpError("API_ERROR", f"Failed to call HeatPumpHQ API: {str(e)}")


@mcp.tool()
def quick_sizer(zip_code: str, square_feet: int, build_year: int) -> dict:
    """
    Calculate the required BTU capacity for a heat pump based on home characteristics.
    
    Args:
        zip_code: 5-digit US ZIP code
        square_feet: Home square footage (100-10000)
        build_year: Year the home was built (1900-2025)
    
    Returns:
        Dictionary containing calculated heating/cooling loads, climate zone, and recommendations
    """
    # Validate input
    input_data = QuickSizerInput(
        zip_code=zip_code,
        square_feet=square_feet,
        build_year=build_year
    )
    
    return make_api_request("quick-sizer/calculate", input_data.dict())


@mcp.tool()
def bill_estimator(
    zip_code: str,
    total_heating_load: int,
    total_cooling_load: int,
    current_system: str,
    home_size: int
) -> dict:
    """
    Estimate electricity costs and ROI for heat pump vs current heating system.
    
    Args:
        zip_code: 5-digit US ZIP code
        total_heating_load: Total heating load in BTU/hr
        total_cooling_load: Total cooling load in BTU/hr
        current_system: Current heating system (gas, electric, oil, propane)
        home_size: Home size in square feet
    
    Returns:
        Dictionary containing cost analysis, payback period, and savings estimates
    """
    input_data = BillEstimatorInput(
        zip_code=zip_code,
        total_heating_load=total_heating_load,
        total_cooling_load=total_cooling_load,
        current_system=current_system,
        home_size=home_size
    )
    
    return make_api_request("bill-estimator/calculate", input_data.dict())


@mcp.tool()
def cold_climate_check(zip_code: str, system_capacity: int, backup_heat: str = "electric") -> dict:
    """
    Verify heat pump performance at design temperatures for cold climates.
    
    Args:
        zip_code: 5-digit US ZIP code
        system_capacity: Heat pump capacity in BTU/hr
        backup_heat: Backup heating type (electric, gas, none)
    
    Returns:
        Dictionary containing climate analysis, design temperature data, and performance metrics
    """
    input_data = ColdClimateInput(
        zip_code=zip_code,
        system_capacity=system_capacity,
        backup_heat=backup_heat
    )
    
    return make_api_request("cold-climate/check", input_data.dict())


@mcp.tool()
def project_cost_estimator(
    zip_code: str,
    home_size: int,
    building_age: str,
    system_type: str,
    installation_complexity: str,
    hvac_experience: str
) -> dict:
    """
    Estimate total project costs for heat pump installation.
    
    Args:
        zip_code: 5-digit US ZIP code
        home_size: Home size in square feet
        building_age: Building age category
        system_type: System type
        installation_complexity: Installation complexity level
        hvac_experience: HVAC contractor experience level
    
    Returns:
        Dictionary containing cost breakdown, rebate information, and financing options
    """
    input_data = ProjectCostInput(
        zip_code=zip_code,
        home_size=home_size,
        building_age=building_age,
        system_type=system_type,
        installation_complexity=installation_complexity,
        hvac_experience=hvac_experience
    )
    
    return make_api_request("project-cost/calculate", input_data.dict())


@mcp.resource("heatpump://api-status")
def get_api_status() -> str:
    """Get the current status of the HeatPumpHQ API"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            return f"✅ HeatPumpHQ API is healthy at {API_BASE_URL}"
        else:
            return f"⚠️ HeatPumpHQ API returned status {response.status_code}"
    except Exception as e:
        return f"❌ HeatPumpHQ API is unreachable: {str(e)}"


@mcp.resource("heatpump://endpoints")
def get_available_endpoints() -> str:
    """List all available HeatPumpHQ API endpoints"""
    endpoints = [
        "🏠 quick_sizer - Calculate required BTU capacity",
        "💰 bill_estimator - Estimate costs and ROI",
        "❄️ cold_climate_check - Verify cold weather performance", 
        "🔧 project_cost_estimator - Calculate installation costs"
    ]
    return "Available HeatPumpHQ tools:\n" + "\n".join(endpoints)


if __name__ == "__main__":
    import mcp.server.stdio
    mcp.server.stdio.run_server()