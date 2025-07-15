#!/usr/bin/env python3
"""
HeatPumpHQ MCP Server - Main Entry Point

This is the main entry point for the HeatPumpHQ MCP server.
The actual implementation is now organized in the src/heatpump_mcp package.
"""

import sys
import os

# Add src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from heatpump_mcp.server import mcp
from heatpump_mcp.tools import quick_sizer, bill_estimator, cold_climate_check, project_cost_estimator
from heatpump_mcp.resources import get_api_status, get_available_endpoints
from heatpump_mcp.config import API_BASE_URL

# Export functions for backward compatibility with tests
__all__ = [
    'mcp', 
    'quick_sizer', 
    'bill_estimator', 
    'cold_climate_check', 
    'project_cost_estimator',
    'get_api_status',
    'get_available_endpoints',
    'API_BASE_URL'
]

if __name__ == "__main__":
    import mcp.server.stdio
    mcp.server.stdio.run_server()