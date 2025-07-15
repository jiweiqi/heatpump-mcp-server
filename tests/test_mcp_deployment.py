#!/usr/bin/env python3
"""
Test MCP deployment at https://mcp.wattsavy.com

This script tests:
1. Health endpoints
2. MCP protocol endpoints
3. Tool functionality via HTTP
4. SSE connectivity
5. OAuth metadata
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
MCP_BASE_URL = "https://mcp.wattsavy.com"
TIMEOUT = 30

def print_test(test_name, result, details=""):
    """Print test result with formatting"""
    status = "✅ PASS" if result else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"   {details}")

def test_health_endpoint():
    """Test the health endpoint"""
    print("\n🏥 Testing Health Endpoint...")
    try:
        response = requests.get(f"{MCP_BASE_URL}/health", timeout=TIMEOUT)
        success = response.status_code == 200
        
        details = f"Status: {response.status_code}"
        if success:
            data = response.json()
            details += f", Status: {data.get('status', 'unknown')}"
            if 'version' in data:
                details += f", Version: {data.get('version')}"
        else:
            details += f", Response: {response.text[:100]}"
            
        print_test("Health endpoint", success, details)
        return success
    except Exception as e:
        print_test("Health endpoint", False, f"Error: {str(e)}")
        return False

def test_root_endpoint():
    """Test the root endpoint"""
    print("\n🌐 Testing Root Endpoint...")
    try:
        response = requests.get(f"{MCP_BASE_URL}/", timeout=TIMEOUT)
        success = response.status_code == 200
        
        details = f"Status: {response.status_code}"
        if success and response.headers.get('content-type', '').startswith('application/json'):
            data = response.json()
            details += f", Server: {data.get('name', 'unknown')}"
            
        print_test("Root endpoint", success, details)
        return success
    except Exception as e:
        print_test("Root endpoint", False, f"Error: {str(e)}")
        return False

def test_mcp_protocol():
    """Test MCP protocol endpoint with initialize request"""
    print("\n🔧 Testing MCP Protocol...")
    
    # Test 1: Initialize request
    initialize_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    try:
        response = requests.post(
            f"{MCP_BASE_URL}/mcp",
            json=initialize_request,
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        
        success = response.status_code in [200, 201]
        details = f"Status: {response.status_code}"
        
        if success:
            data = response.json()
            if 'result' in data:
                server_info = data['result'].get('serverInfo', {})
                details += f", Server: {server_info.get('name', 'unknown')}"
        else:
            details += f", Response: {response.text[:100]}"
            
        print_test("MCP Initialize", success, details)
        
        # Test 2: List tools request
        if success:
            list_tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            response = requests.post(
                f"{MCP_BASE_URL}/mcp",
                json=list_tools_request,
                headers={"Content-Type": "application/json"},
                timeout=TIMEOUT
            )
            
            tools_success = response.status_code in [200, 201]
            if tools_success and 'result' in response.json():
                tools = response.json()['result'].get('tools', [])
                print_test("MCP List Tools", True, f"Found {len(tools)} tools")
            else:
                print_test("MCP List Tools", False, f"Status: {response.status_code}")
                
        return success
        
    except Exception as e:
        print_test("MCP Protocol", False, f"Error: {str(e)}")
        return False

def test_sse_endpoint():
    """Test SSE endpoint accessibility"""
    print("\n📡 Testing SSE Endpoint...")
    try:
        # Just test that the endpoint exists and responds
        response = requests.get(
            f"{MCP_BASE_URL}/mcp/sse",
            timeout=5,  # Short timeout since we're not waiting for events
            stream=True
        )
        
        # SSE endpoints typically return 200 with text/event-stream
        success = response.status_code == 200
        content_type = response.headers.get('content-type', '')
        
        details = f"Status: {response.status_code}, Content-Type: {content_type}"
        print_test("SSE endpoint", success, details)
        
        response.close()
        return success
        
    except requests.exceptions.Timeout:
        # Timeout is expected for SSE
        print_test("SSE endpoint", True, "Endpoint accessible (timeout expected)")
        return True
    except Exception as e:
        print_test("SSE endpoint", False, f"Error: {str(e)}")
        return False

def test_cors_headers():
    """Test CORS headers"""
    print("\n🔒 Testing CORS Headers...")
    try:
        response = requests.options(
            f"{MCP_BASE_URL}/mcp",
            headers={"Origin": "https://claude.ai"},
            timeout=TIMEOUT
        )
        
        cors_headers = {
            'access-control-allow-origin': response.headers.get('access-control-allow-origin'),
            'access-control-allow-methods': response.headers.get('access-control-allow-methods'),
            'access-control-allow-headers': response.headers.get('access-control-allow-headers')
        }
        
        has_cors = any(v for v in cors_headers.values() if v)
        
        details = f"CORS headers: {', '.join(k for k, v in cors_headers.items() if v)}"
        print_test("CORS headers", has_cors, details)
        return has_cors
        
    except Exception as e:
        print_test("CORS headers", False, f"Error: {str(e)}")
        return False

def test_tool_execution():
    """Test actual tool execution via MCP protocol"""
    print("\n⚡ Testing Tool Execution...")
    
    # First initialize
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0.0"}
        }
    }
    
    try:
        # Initialize session
        response = requests.post(f"{MCP_BASE_URL}/mcp", json=init_request, timeout=TIMEOUT)
        if response.status_code != 200:
            print_test("Tool execution", False, "Failed to initialize")
            return False
            
        # Call quick_sizer tool
        tool_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "quick_sizer",
                "arguments": {
                    "zip_code": "02101",
                    "square_feet": 2000,
                    "build_year": 2010
                }
            }
        }
        
        response = requests.post(
            f"{MCP_BASE_URL}/mcp",
            json=tool_request,
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        
        success = response.status_code == 200
        if success:
            data = response.json()
            if 'result' in data:
                result = data['result']
                if 'content' in result:
                    print_test("Tool execution", True, "quick_sizer returned results")
                else:
                    print_test("Tool execution", True, f"Response: {json.dumps(result)[:100]}")
            else:
                print_test("Tool execution", False, f"No result in response")
        else:
            print_test("Tool execution", False, f"Status: {response.status_code}")
            
        return success
        
    except Exception as e:
        print_test("Tool execution", False, f"Error: {str(e)}")
        return False

def test_oauth_metadata():
    """Test OAuth metadata endpoint if configured"""
    print("\n🔐 Testing OAuth Metadata...")
    try:
        response = requests.get(
            f"{MCP_BASE_URL}/.well-known/oauth-authorization-server",
            timeout=TIMEOUT
        )
        
        # OAuth metadata is optional
        if response.status_code == 404:
            print_test("OAuth metadata", True, "Not configured (optional)")
            return True
        elif response.status_code == 200:
            print_test("OAuth metadata", True, "OAuth configured")
            return True
        else:
            print_test("OAuth metadata", False, f"Status: {response.status_code}")
            return False
            
    except Exception as e:
        print_test("OAuth metadata", False, f"Error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 MCP Deployment Verification")
    print(f"📍 Testing: {MCP_BASE_URL}")
    print(f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health_endpoint),
        ("Root Endpoint", test_root_endpoint),
        ("MCP Protocol", test_mcp_protocol),
        ("SSE Endpoint", test_sse_endpoint),
        ("CORS Headers", test_cors_headers),
        ("Tool Execution", test_tool_execution),
        ("OAuth Metadata", test_oauth_metadata)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} - Unexpected error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! MCP deployment is healthy.")
        return 0
    else:
        print("⚠️  Some tests failed. Check deployment status.")
        return 1

if __name__ == "__main__":
    sys.exit(main())