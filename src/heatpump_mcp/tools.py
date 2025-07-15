"""
MCP tools for HeatPumpHQ calculations
"""

from typing import Optional
from .api_client import make_api_request


def quick_sizer(zip_code: str, square_feet: int, build_year: int) -> dict:
    """
    Calculate the required BTU capacity for a heat pump based on home characteristics.
    
    Args:
        zip_code: 5-digit US ZIP code
        square_feet: Home square footage (100-10000)
        build_year: Year the home was built (1900-2025)
    
    Returns:
        Dictionary containing BTU requirements, climate data, and sizing recommendations
    """
    data = {
        "zip_code": zip_code,
        "square_feet": square_feet,
        "build_year": build_year
    }
    return make_api_request("quick-sizer/calculate", data)


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
    Estimate heating costs, savings, and payback period compared to current heating system.
    
    Args:
        zip_code: 5-digit US ZIP code
        square_feet: Home square footage (100-10000)
        build_year: Year the home was built (1900-2025)
        heat_pump_model: Heat pump model (e.g., 'Mitsubishi MXZ-3C24NA')
        current_heating_fuel: Current heating fuel (gas, electric, oil, propane)
        gas_price_per_therm: Gas price per therm (optional)
        electricity_rate_override: Electricity rate override (optional)
    
    Returns:
        Dictionary containing cost estimates, savings, and payback analysis
    """
    data = {
        "zip_code": zip_code,
        "square_feet": square_feet,
        "build_year": build_year,
        "heat_pump_model": heat_pump_model,
        "current_heating_fuel": current_heating_fuel
    }
    
    if gas_price_per_therm is not None:
        data["gas_price_per_therm"] = gas_price_per_therm
    if electricity_rate_override is not None:
        data["electricity_rate_override"] = electricity_rate_override
    
    return make_api_request("bill-estimator/calculate", data)


def cold_climate_check(
    zip_code: str, 
    square_feet: int, 
    build_year: int, 
    heat_pump_model: str, 
    existing_backup_heat: Optional[str] = None
) -> dict:
    """
    Check heat pump performance in cold climate conditions and backup heating requirements.
    
    Args:
        zip_code: 5-digit US ZIP code
        square_feet: Home square footage (100-10000)
        build_year: Year the home was built (1900-2025)
        heat_pump_model: Heat pump model (e.g., 'Mitsubishi MXZ-3C24NA')
        existing_backup_heat: Existing backup heating type (electric_strip, gas_furnace, oil_boiler, none)
    
    Returns:
        Dictionary containing climate analysis, performance curves, and backup heating recommendations
    """
    data = {
        "zip_code": zip_code,
        "square_feet": square_feet,
        "build_year": build_year,
        "heat_pump_model": heat_pump_model
    }
    
    if existing_backup_heat:
        data["existing_backup_heat"] = existing_backup_heat
    
    return make_api_request("cold-climate/check", data)


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
    Estimate total project cost including equipment, installation, and complexity factors.
    
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
        Dictionary containing cost breakdown, complexity assessment, and installation recommendations
    """
    data = {
        "zip_code": zip_code,
        "square_feet": square_feet,
        "build_year": build_year,
        "heat_pump_model": heat_pump_model,
        "existing_heating_type": existing_heating_type,
        "ductwork_condition": ductwork_condition,
        "home_stories": home_stories,
        "insulation_quality": insulation_quality,
        "air_sealing": air_sealing
    }
    return make_api_request("project-cost/estimate", data)