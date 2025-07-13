#!/usr/bin/env python3
"""
HeatPumpHQ MCP HTTP/SSE Server

An HTTP + Server-Sent Events (SSE) based MCP server that provides remote access to 
HeatPumpHQ's heat pump calculation APIs. Implements the standard HTTP transport
that Claude Code supports.

Compatible with Claude Code MCP client expectations:
- HTTP POST for requests
- Server-Sent Events (SSE) for streaming responses
- JSON-RPC 2.0 message format
- Standard MCP protocol compliance
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Optional, Any
import uuid
from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

# Import MCP server logic from existing server.py
from server import (
    mcp, 
    API_BASE_URL, 
    API_KEY, 
    make_api_request,
    quick_sizer,
    bill_estimator, 
    cold_climate_check,
    project_cost_estimator
)

# Load environment variables
load_dotenv()

# HTTP server configuration
HTTP_HOST = os.getenv("MCP_HTTP_HOST", "0.0.0.0")
HTTP_PORT = int(os.getenv("MCP_HTTP_PORT", "3002"))
ALLOWED_ORIGINS = os.getenv("MCP_ALLOWED_ORIGINS", "*").split(",")

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=getattr(logging, log_level))
logger = logging.getLogger(__name__)

# Standard MCP error codes for 2025-03-26
MCP_ERRORS = {
    "PARSE_ERROR": -32700,
    "INVALID_REQUEST": -32600,
    "METHOD_NOT_FOUND": -32601,
    "INVALID_PARAMS": -32602,
    "INTERNAL_ERROR": -32603,
    "TOOL_ERROR": -32000,  # MCP-specific
    "RESOURCE_NOT_FOUND": -32001,  # MCP-specific
    "AUTHORIZATION_ERROR": -32002   # MCP-specific
}

# FastAPI app
app = FastAPI(title="HeatPumpHQ MCP HTTP Server", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MCPHTTPServer:
    """HTTP + SSE server implementing MCP protocol"""
    
    def __init__(self):
        self.connections = {}
        
    async def handle_mcp_request(self, message: dict, session_id: str = None) -> tuple[dict, str]:
        """Handle MCP JSON-RPC 2.0 request and return response with optional session ID"""
        request_id = message.get("id")
        method = message.get("method")
        params = message.get("params", {})
        
        logger.info(f"Handling MCP request: {method}")
        
        try:
            # Handle MCP protocol methods
            if method == "initialize":
                # Generate session ID for new connections
                import uuid
                new_session_id = str(uuid.uuid4())
                
                # Support both 2024-11-05 and 2025-03-26 protocol versions
                client_version = params.get("protocolVersion", "2024-11-05")
                supported_versions = ["2024-11-05", "2025-03-26"]
                
                # Prefer latest version if client supports it
                if "2025-03-26" in [client_version] + supported_versions:
                    protocol_version = "2025-03-26"
                else:
                    protocol_version = "2024-11-05"
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": protocol_version,
                        "capabilities": {
                            "tools": {},
                            "resources": {},
                            "authorization": {"oauth2": True},
                            "sampling": False
                        },
                        "serverInfo": {
                            "name": "HeatPumpHQ MCP Server",
                            "version": "1.0.0",
                            "vendor": "WattSavy",
                            "protocolVersion": protocol_version,
                            "description": "Professional heat pump sizing, cost estimation, and cold-climate performance verification",
                            "homepage": "https://www.wattsavy.com",
                            "repository": "https://github.com/weiqi-anthropic/HeatPumpHQ",
                            "category": "energy-efficiency",
                            "tags": ["heatpump", "hvac", "energy", "residential", "calculations"]
                        }
                    }
                }, new_session_id
                
            elif method == "tools/list":
                # List available tools
                tools = [
                    {
                        "name": "quick_sizer",
                        "description": "Calculate required BTU capacity for heat pump based on home characteristics. Essential first step for proper heat pump sizing.",
                        "category": "sizing",
                        "tags": ["btu", "capacity", "sizing", "hvac"],
                        "annotations": {
                            "readOnlyHint": True,
                            "idempotentHint": True,
                            "destructiveHint": False
                        },
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "zip_code": {"type": "string", "pattern": "^[0-9]{5}$", "description": "5-digit US ZIP code for climate zone determination"},
                                "square_feet": {"type": "integer", "minimum": 100, "maximum": 10000, "description": "Home square footage (100-10,000)"},
                                "build_year": {"type": "integer", "minimum": 1900, "maximum": 2025, "description": "Year home was built (affects insulation standards)"}
                            },
                            "required": ["zip_code", "square_feet", "build_year"],
                            "additionalProperties": False,
                            "$schema": "http://json-schema.org/draft-07/schema#"
                        }
                    },
                    {
                        "name": "bill_estimator", 
                        "description": "Estimate electricity costs and ROI for heat pump vs current heating system. Provides payback analysis and monthly savings projections.",
                        "category": "financial",
                        "tags": ["cost", "savings", "roi", "electricity", "payback"],
                        "annotations": {
                            "readOnlyHint": False,
                            "idempotentHint": True,
                            "destructiveHint": False
                        },
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "zip_code": {"type": "string"},
                                "square_feet": {"type": "integer", "minimum": 100, "maximum": 10000},
                                "build_year": {"type": "integer", "minimum": 1900, "maximum": 2025},
                                "heat_pump_model": {"type": "string"},
                                "current_heating_fuel": {"type": "string"},
                                "gas_price_per_therm": {"type": "number"},
                                "electricity_rate_override": {"type": "number"}
                            },
                            "required": ["zip_code", "square_feet", "build_year", "heat_pump_model", "current_heating_fuel"],
                            "additionalProperties": False,
                            "$schema": "http://json-schema.org/draft-07/schema#"
                        }
                    },
                    {
                        "name": "cold_climate_check",
                        "description": "Verify heat pump performance at design temperatures for cold climates. Critical for ensuring adequate heating in harsh winter conditions.",
                        "category": "performance",
                        "tags": ["cold-climate", "winter", "performance", "backup-heat", "design-temp"],
                        "annotations": {
                            "readOnlyHint": False,
                            "idempotentHint": True,
                            "destructiveHint": False
                        },
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "zip_code": {"type": "string"},
                                "square_feet": {"type": "integer", "minimum": 100, "maximum": 10000},
                                "build_year": {"type": "integer", "minimum": 1900, "maximum": 2025},
                                "heat_pump_model": {"type": "string"},
                                "existing_backup_heat": {"type": "string"}
                            },
                            "required": ["zip_code", "square_feet", "build_year", "heat_pump_model"],
                            "additionalProperties": False,
                            "$schema": "http://json-schema.org/draft-07/schema#"
                        }
                    },
                    {
                        "name": "project_cost_estimator",
                        "description": "Estimate total project costs for heat pump installation including equipment, labor, permits, and efficiency upgrades. Comprehensive cost breakdown for project planning.",
                        "category": "project-planning",
                        "tags": ["installation", "project-cost", "labor", "permits", "total-cost", "upgrades"],
                        "annotations": {
                            "readOnlyHint": False,
                            "idempotentHint": True,
                            "destructiveHint": False
                        },
                        "inputSchema": {
                            "type": "object", 
                            "properties": {
                                "zip_code": {"type": "string"},
                                "square_feet": {"type": "integer", "minimum": 100, "maximum": 10000},
                                "build_year": {"type": "integer", "minimum": 1900, "maximum": 2025},
                                "heat_pump_model": {"type": "string"},
                                "existing_heating_type": {"type": "string"},
                                "ductwork_condition": {"type": "string"},
                                "home_stories": {"type": "integer", "minimum": 1, "maximum": 4},
                                "insulation_quality": {"type": "string"},
                                "air_sealing": {"type": "string"}
                            },
                            "required": ["zip_code", "square_feet", "build_year", "heat_pump_model", 
                                       "existing_heating_type", "ductwork_condition", "home_stories",
                                       "insulation_quality", "air_sealing"],
                            "additionalProperties": False,
                            "$schema": "http://json-schema.org/draft-07/schema#"
                        }
                    }
                ]
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"tools": tools}
                }, session_id
                
            elif method == "tools/call":
                # Execute tool call
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                
                if tool_name == "quick_sizer":
                    result = quick_sizer(**tool_args)
                elif tool_name == "bill_estimator":
                    result = bill_estimator(**tool_args)
                elif tool_name == "cold_climate_check":
                    result = cold_climate_check(**tool_args)
                elif tool_name == "project_cost_estimator":
                    result = project_cost_estimator(**tool_args)
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": MCP_ERRORS["TOOL_ERROR"],
                            "message": f"Unknown tool: {tool_name}",
                            "data": {
                                "available_tools": ["quick_sizer", "bill_estimator", "cold_climate_check", "project_cost_estimator"]
                            }
                        }
                    }, session_id
                    
                # Wrap result in MCP tool response format
                tool_result = {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": tool_result
                }, session_id
                
            elif method == "resources/list":
                # List available resources
                resources = [
                    {
                        "uri": "heatpump://api-status",
                        "name": "API Status",
                        "description": "Current status of the HeatPumpHQ API"
                    },
                    {
                        "uri": "heatpump://endpoints", 
                        "name": "Available Endpoints",
                        "description": "List of all available HeatPumpHQ tools"
                    }
                ]
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"resources": resources}
                }, session_id
                
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": MCP_ERRORS["METHOD_NOT_FOUND"],
                        "message": f"Unknown method: {method}",
                        "data": {
                            "available_methods": ["initialize", "tools/list", "tools/call", "resources/list"]
                        }
                    }
                }, session_id
                
        except Exception as e:
            logger.error(f"Error handling request {method}: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": MCP_ERRORS["INTERNAL_ERROR"],
                    "message": f"Internal error: {str(e)}",
                    "data": {
                        "method": method,
                        "timestamp": str(asyncio.get_event_loop().time())
                    }
                }
            }, session_id

# Global MCP server instance
mcp_server = MCPHTTPServer()

@app.post("/mcp")
async def handle_mcp_post(request: Request):
    """Handle MCP HTTP POST requests"""
    try:
        # Parse JSON-RPC 2.0 request
        body = await request.body()
        data = json.loads(body)
        
        logger.info(f"Received MCP request: {data.get('method')}")
        
        # Validate JSON-RPC 2.0 format
        if not isinstance(data, dict) or data.get("jsonrpc") != "2.0":
            raise HTTPException(status_code=400, detail="Invalid JSON-RPC 2.0 format")
        
        # Extract session ID from headers
        session_id = request.headers.get("Mcp-Session-Id")
        
        # Handle MCP request
        response, new_session_id = await mcp_server.handle_mcp_request(data, session_id)
        
        # Set up response with session ID header if provided
        json_response = Response(
            content=json.dumps(response),
            media_type="application/json"
        )
        
        # Add session ID header for initialize method or if session exists
        if new_session_id:
            json_response.headers["Mcp-Session-Id"] = new_session_id
            
        return json_response
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        logger.error(f"Error in MCP POST handler: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/mcp/sse")
async def handle_mcp_sse(request: Request):
    """Handle MCP Server-Sent Events connection"""
    
    async def event_stream():
        connection_id = str(uuid.uuid4())
        mcp_server.connections[connection_id] = True
        
        try:
            # Send connection established event
            yield f"data: {json.dumps({'type': 'connection', 'id': connection_id})}\n\n"
            
            # Keep connection alive
            while mcp_server.connections.get(connection_id):
                # Send periodic keepalive
                yield f"data: {json.dumps({'type': 'keepalive', 'timestamp': str(asyncio.get_event_loop().time())})}\n\n"
                await asyncio.sleep(30)
                
        except Exception as e:
            logger.error(f"SSE connection error: {e}")
        finally:
            mcp_server.connections.pop(connection_id, None)
    
    return StreamingResponse(
        event_stream(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*"
        }
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "server": "HeatPumpHQ MCP HTTP Server",
        "version": "1.0.0",
        "backend_api": API_BASE_URL
    }

@app.get("/")
async def root():
    """Root endpoint with server info"""
    return {
        "name": "HeatPumpHQ MCP HTTP Server",
        "version": "1.0.0",
        "description": "HTTP + SSE based MCP server for heat pump calculations",
        "endpoints": {
            "mcp_post": "/mcp",
            "mcp_sse": "/mcp/sse", 
            "health": "/health"
        },
        "tools": ["quick_sizer", "bill_estimator", "cold_climate_check", "project_cost_estimator"]
    }

if __name__ == "__main__":
    logger.info(f"Starting HeatPumpHQ MCP HTTP server on {HTTP_HOST}:{HTTP_PORT}")
    logger.info(f"Backend API: {API_BASE_URL}")
    logger.info(f"Allowed Origins: {ALLOWED_ORIGINS}")
    
    uvicorn.run(
        app,
        host=HTTP_HOST,
        port=HTTP_PORT,
        log_level=log_level.lower()
    )