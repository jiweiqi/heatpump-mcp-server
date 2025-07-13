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
from fastapi import FastAPI, Request, HTTPException
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
        
    async def handle_mcp_request(self, message: dict) -> dict:
        """Handle MCP JSON-RPC 2.0 request and return response"""
        request_id = message.get("id")
        method = message.get("method")
        params = message.get("params", {})
        
        logger.info(f"Handling MCP request: {method}")
        
        try:
            # Handle MCP protocol methods
            if method == "initialize":
                # MCP initialization handshake
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {},
                            "resources": {}
                        },
                        "serverInfo": {
                            "name": "HeatPumpHQ",
                            "version": "1.0.0"
                        }
                    }
                }
                
            elif method == "tools/list":
                # List available tools
                tools = [
                    {
                        "name": "quick_sizer",
                        "description": "Calculate required BTU capacity for heat pump based on home characteristics",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "zip_code": {"type": "string", "description": "5-digit US ZIP code"},
                                "square_feet": {"type": "integer", "minimum": 100, "maximum": 10000},
                                "build_year": {"type": "integer", "minimum": 1900, "maximum": 2025}
                            },
                            "required": ["zip_code", "square_feet", "build_year"]
                        }
                    },
                    {
                        "name": "bill_estimator", 
                        "description": "Estimate electricity costs and ROI for heat pump vs current heating system",
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
                            "required": ["zip_code", "square_feet", "build_year", "heat_pump_model", "current_heating_fuel"]
                        }
                    },
                    {
                        "name": "cold_climate_check",
                        "description": "Verify heat pump performance at design temperatures for cold climates", 
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "zip_code": {"type": "string"},
                                "square_feet": {"type": "integer", "minimum": 100, "maximum": 10000},
                                "build_year": {"type": "integer", "minimum": 1900, "maximum": 2025},
                                "heat_pump_model": {"type": "string"},
                                "existing_backup_heat": {"type": "string"}
                            },
                            "required": ["zip_code", "square_feet", "build_year", "heat_pump_model"]
                        }
                    },
                    {
                        "name": "project_cost_estimator",
                        "description": "Estimate total project costs for heat pump installation",
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
                                       "insulation_quality", "air_sealing"]
                        }
                    }
                ]
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"tools": tools}
                }
                
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
                            "code": -32601,
                            "message": f"Unknown tool: {tool_name}"
                        }
                    }
                    
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
                }
                
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
                }
                
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown method: {method}"
                    }
                }
                
        except Exception as e:
            logger.error(f"Error handling request {method}: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }

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
            
        # Handle MCP request
        response = await mcp_server.handle_mcp_request(data)
        
        return response
        
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