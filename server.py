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
from mcp import McpError
from mcp.types import Tool, ErrorData

# Load environment variables
# Check for environment-specific files first, then fall back to defaults
env_mode = os.getenv('ENV_MODE', 'default')
if env_mode == 'production' and os.path.exists('.env.production'):
    load_dotenv('.env.production')
elif env_mode == 'local' and os.path.exists('.env.local'):
    load_dotenv('.env.local')
elif os.path.exists('.env.local'):
    load_dotenv('.env.local')
else:
    load_dotenv()

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=getattr(logging, log_level))
logger = logging.getLogger(__name__)

# Configuration
API_BASE_URL = os.getenv("HEATPUMP_API_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY")  # Optional
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))

# Initialize MCP server
mcp = FastMCP("HeatPumpHQ")

# Pydantic models for input validation
class QuickSizerInput(BaseModel):
    zip_code: str = Field(..., description="5-digit US ZIP code")
    square_feet: int = Field(..., ge=100, le=10000, description="Home square footage (100-10000)")
    build_year: int = Field(..., ge=1900, le=2025, description="Year the home was built (1900-2025)")

class BillEstimatorInput(BaseModel):
    zip_code: str = Field(..., description="5-digit US ZIP code")
    square_feet: int = Field(..., ge=100, le=10000, description="Home square footage (100-10000)")
    build_year: int = Field(..., ge=1900, le=2025, description="Year the home was built (1900-2025)")
    heat_pump_model: str = Field(..., description="Heat pump model (e.g., 'Mitsubishi MXZ-3C24NA')")
    current_heating_fuel: str = Field(..., description="Current heating fuel (gas, electric, oil, propane)")
    gas_price_per_therm: Optional[float] = Field(None, description="Gas price per therm (optional)")
    electricity_rate_override: Optional[float] = Field(None, description="Electricity rate override (optional)")

class ColdClimateInput(BaseModel):
    zip_code: str = Field(..., description="5-digit US ZIP code")
    square_feet: int = Field(..., ge=100, le=10000, description="Home square footage (100-10000)")
    build_year: int = Field(..., ge=1900, le=2025, description="Year the home was built (1900-2025)")
    heat_pump_model: str = Field(..., description="Heat pump model (e.g., 'Mitsubishi MXZ-3C24NA')")
    existing_backup_heat: Optional[str] = Field(None, description="Existing backup heating type (electric_strip, gas_furnace, oil_boiler, none)")

class ProjectCostInput(BaseModel):
    zip_code: str = Field(..., description="5-digit US ZIP code")
    square_feet: int = Field(..., ge=100, le=10000, description="Home square footage (100-10000)")
    build_year: int = Field(..., ge=1900, le=2025, description="Year the home was built (1900-2025)")
    heat_pump_model: str = Field(..., description="Heat pump model (e.g., 'Fujitsu AOU24RLXFZ')")
    existing_heating_type: str = Field(..., description="Existing heating type (gas_furnace, electric_baseboard, oil_boiler, etc.)")
    ductwork_condition: str = Field(..., description="Ductwork condition (good, fair, poor, none)")
    home_stories: int = Field(..., ge=1, le=4, description="Number of home stories (1-4)")
    insulation_quality: str = Field(..., description="Insulation quality (excellent, good, fair, poor)")
    air_sealing: str = Field(..., description="Air sealing quality (excellent, good, fair, poor)")


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


@mcp.tool()
def quick_sizer(zip_code: str, square_feet: int, build_year: int) -> dict:
    """
    Calculate the required BTU capacity for a heat pump based on home characteristics.
    
    Args:
        zip_code: 5-digit US ZIP code
        square_feet: Home square footage (100-10000)
        build_year: Year the home was built (1900-2025)
    
    Returns:
        Dictionary containing calculated heating/cooling loads, climate zone, and equipment recommendations
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
    square_feet: int,
    build_year: int,
    heat_pump_model: str,
    current_heating_fuel: str,
    gas_price_per_therm: Optional[float] = None,
    electricity_rate_override: Optional[float] = None
) -> dict:
    """
    Estimate electricity costs and ROI for heat pump vs current heating system.
    
    Args:
        zip_code: 5-digit US ZIP code
        square_feet: Home square footage (100-10000)
        build_year: Year the home was built (1900-2025)
        heat_pump_model: Heat pump model (e.g., 'Mitsubishi MXZ-3C24NA')
        current_heating_fuel: Current heating fuel (gas, electric, oil, propane)
        gas_price_per_therm: Gas price per therm (optional)
        electricity_rate_override: Electricity rate override (optional)
    
    Returns:
        Dictionary containing cost analysis, payback period, and 10-year savings projection
    """
    input_data = BillEstimatorInput(
        zip_code=zip_code,
        square_feet=square_feet,
        build_year=build_year,
        heat_pump_model=heat_pump_model,
        current_heating_fuel=current_heating_fuel,
        gas_price_per_therm=gas_price_per_therm,
        electricity_rate_override=electricity_rate_override
    )
    
    return make_api_request("bill-estimator/calculate", input_data.dict())


@mcp.tool()
def cold_climate_check(
    zip_code: str, 
    square_feet: int, 
    build_year: int, 
    heat_pump_model: str, 
    existing_backup_heat: Optional[str] = None
) -> dict:
    """
    Verify heat pump performance at design temperatures for cold climates.
    
    Args:
        zip_code: 5-digit US ZIP code
        square_feet: Home square footage (100-10000)
        build_year: Year the home was built (1900-2025)
        heat_pump_model: Heat pump model (e.g., 'Mitsubishi MXZ-3C24NA')
        existing_backup_heat: Existing backup heating type (electric_strip, gas_furnace, oil_boiler, none)
    
    Returns:
        Dictionary containing climate analysis, capacity curves, and backup heat recommendations
    """
    input_data = ColdClimateInput(
        zip_code=zip_code,
        square_feet=square_feet,
        build_year=build_year,
        heat_pump_model=heat_pump_model,
        existing_backup_heat=existing_backup_heat
    )
    
    return make_api_request("cold-climate/check", input_data.dict())


@mcp.tool()
def project_cost_estimator(
    zip_code: str,
    square_feet: int,
    build_year: int,
    heat_pump_model: str,
    existing_heating_type: str,
    ductwork_condition: str,
    home_stories: int,
    insulation_quality: str,
    air_sealing: str
) -> dict:
    """
    Estimate total project costs for heat pump installation including complexity assessment.
    
    Args:
        zip_code: 5-digit US ZIP code
        square_feet: Home square footage (100-10000)
        build_year: Year the home was built (1900-2025)
        heat_pump_model: Heat pump model (e.g., 'Fujitsu AOU24RLXFZ')
        existing_heating_type: Existing heating type (gas_furnace, electric_baseboard, oil_boiler, etc.)
        ductwork_condition: Ductwork condition (good, fair, poor, none)
        home_stories: Number of home stories (1-4)
        insulation_quality: Insulation quality (excellent, good, fair, poor)
        air_sealing: Air sealing quality (excellent, good, fair, poor)
    
    Returns:
        Dictionary containing cost breakdown, regional factors, and complexity analysis
    """
    input_data = ProjectCostInput(
        zip_code=zip_code,
        square_feet=square_feet,
        build_year=build_year,
        heat_pump_model=heat_pump_model,
        existing_heating_type=existing_heating_type,
        ductwork_condition=ductwork_condition,
        home_stories=home_stories,
        insulation_quality=insulation_quality,
        air_sealing=air_sealing
    )
    
    return make_api_request("project-cost/estimate", input_data.dict())


@mcp.resource("heatpump://api-status")
def get_api_status() -> str:
    """Get the current status of the HeatPumpHQ API"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=API_TIMEOUT)
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
        "🏠 quick_sizer - Calculate required BTU capacity based on home characteristics",
        "💰 bill_estimator - Estimate costs, savings, and payback period vs current heating",
        "❄️ cold_climate_check - Verify heat pump performance in cold climates", 
        "🔧 project_cost_estimator - Calculate total installation costs with complexity analysis"
    ]
    return "Available HeatPumpHQ tools:\n" + "\n".join(endpoints)


if __name__ == "__main__":
    import mcp.server.stdio
    mcp.server.stdio.run_server()