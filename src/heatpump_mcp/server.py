"""
HeatPumpHQ MCP Server

Main server implementation using the Model Context Protocol.
"""

from mcp.server.fastmcp import FastMCP

from .config import SERVER_NAME
from .tools import quick_sizer, bill_estimator, cold_climate_check, project_cost_estimator
from .resources import get_api_status, get_available_endpoints

# Initialize MCP server
mcp = FastMCP(SERVER_NAME)

# Register tools
mcp.tool()(quick_sizer)
mcp.tool()(bill_estimator) 
mcp.tool()(cold_climate_check)
mcp.tool()(project_cost_estimator)

# Register resources
mcp.resource("heatpump://api-status")(get_api_status)
mcp.resource("heatpump://endpoints")(get_available_endpoints)


def run_server():
    """Run the MCP server"""
    import asyncio
    asyncio.run(mcp.run())


if __name__ == "__main__":
    run_server()