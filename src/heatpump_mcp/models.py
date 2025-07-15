"""
Pydantic models for input validation
"""

from typing import Optional
from pydantic import BaseModel, Field


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