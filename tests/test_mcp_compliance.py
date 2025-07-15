#!/usr/bin/env python3
"""
Test MCP Server 2025-03-26 Compliance

Basic validation test for our enhanced MCP server to ensure
it follows the 2025-03-26 protocol specifications.
"""

import json
import asyncio
from server_http import MCPHTTPServer

async def test_mcp_compliance():
    """Test basic MCP 2025-03-26 compliance"""
    server = MCPHTTPServer()
    
    print("🧪 Testing MCP Server 2025-03-26 Compliance")
    print("=" * 50)
    
    # Test 1: Initialize with 2025-03-26 protocol
    print("\n1️⃣ Testing initialize with 2025-03-26 protocol...")
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "clientInfo": {
                "name": "Test Client",
                "version": "1.0.0"
            }
        }
    }
    
    response, session_id = await server.handle_mcp_request(init_request)
    assert response["result"]["protocolVersion"] == "2025-03-26"
    assert "authorization" in response["result"]["capabilities"]
    assert "sampling" in response["result"]["capabilities"]
    print("✅ Initialize works with 2025-03-26 protocol")
    
    # Test 2: List tools with enhanced metadata
    print("\n2️⃣ Testing tools/list with 2025-03-26 annotations...")
    tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    
    response, _ = await server.handle_mcp_request(tools_request, session_id)
    tools = response["result"]["tools"]
    
    # Verify all tools have required 2025-03-26 annotations
    for tool in tools:
        assert "annotations" in tool, f"Tool {tool['name']} missing annotations"
        assert "readOnlyHint" in tool["annotations"]
        assert "idempotentHint" in tool["annotations"]
        assert "destructiveHint" in tool["annotations"]
        assert "$schema" in tool["inputSchema"]
        assert "additionalProperties" in tool["inputSchema"]
    
    print(f"✅ All {len(tools)} tools have proper 2025-03-26 annotations")
    
    # Test 3: Error handling with standardized codes
    print("\n3️⃣ Testing standardized error handling...")
    invalid_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "invalid_method",
        "params": {}
    }
    
    response, _ = await server.handle_mcp_request(invalid_request, session_id)
    assert "error" in response
    assert response["error"]["code"] == -32601  # METHOD_NOT_FOUND
    assert "available_methods" in response["error"]["data"]
    print("✅ Error handling follows MCP standards")
    
    # Test 4: Tool execution
    print("\n4️⃣ Testing tool execution...")
    tool_request = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "quick_sizer",
            "arguments": {
                "zip_code": "10001",
                "square_feet": 2000,
                "build_year": 2020
            }
        }
    }
    
    response, _ = await server.handle_mcp_request(tool_request, session_id)
    assert "result" in response
    assert "content" in response["result"]
    print("✅ Tool execution works correctly")
    
    print("\n🎉 All MCP 2025-03-26 compliance tests passed!")
    print("\nServer is ready for Claude Code and other MCP clients")

if __name__ == "__main__":
    asyncio.run(test_mcp_compliance())