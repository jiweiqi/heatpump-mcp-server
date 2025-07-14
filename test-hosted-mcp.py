#!/usr/bin/env python3
"""
Test script for hosted MCP server at https://mcp.wattsavy.com
Tests both the health endpoint and MCP functionality
"""

import requests
import json
import time
import sys

MCP_BASE_URL = "https://mcp.wattsavy.com"

def test_health_endpoint():
    """Test the health endpoint and show version info"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{MCP_BASE_URL}/health", timeout=10)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Health Status: {data.get('status', 'unknown')}")
            
            # Check for version info (should be present after deployment)
            if 'version' in data:
                print(f"   Server Version: {data.get('version')}")
                print(f"   Build ID: {data.get('build_id', 'unknown')}")
                print(f"   Deployment: {data.get('deployment_timestamp', 'unknown')}")
                print(f"   Backend API: {data.get('backend_api', 'unknown')}")
            else:
                print("   ⚠️  Version info not available (old deployment)")
            
            return True, data
        else:
            print(f"   ❌ Health check failed with status {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False, None

def test_mcp_endpoint():
    """Test MCP endpoint via HTTP POST"""
    print("🔍 Testing MCP endpoint...")
    try:
        # Test MCP initialize request
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        
        response = requests.post(
            f"{MCP_BASE_URL}/mcp",
            json=mcp_request,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "result" in data:
                server_info = data["result"].get("serverInfo", {})
                print(f"   MCP Server: {server_info.get('name', 'unknown')}")
                print(f"   MCP Version: {server_info.get('version', 'unknown')}")
                print(f"   ✅ MCP initialization successful")
                return True, data
            else:
                print(f"   ❌ MCP response invalid: {data}")
                return False, None
        else:
            print(f"   ❌ MCP request failed with status {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False, None
            
    except Exception as e:
        print(f"   ❌ MCP test error: {e}")
        return False, None

def test_mcp_tools():
    """Test MCP tools listing"""
    print("🔍 Testing MCP tools...")
    try:
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        response = requests.post(
            f"{MCP_BASE_URL}/mcp",
            json=tools_request,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            if "result" in data:
                tools = data["result"].get("tools", [])
                print(f"   Found {len(tools)} tools:")
                for tool in tools:
                    print(f"     - {tool.get('name', 'unknown')}: {tool.get('description', 'no description')}")
                print(f"   ✅ Tools listing successful")
                return True, tools
            else:
                print(f"   ❌ Tools response invalid: {data}")
                return False, None
        else:
            print(f"   ❌ Tools request failed with status {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"   ❌ Tools test error: {e}")
        return False, None

def test_quick_sizer_tool():
    """Test the quick_sizer tool"""
    print("🔍 Testing quick_sizer tool...")
    try:
        tool_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "quick_sizer",
                "arguments": {
                    "zip_code": "10001",
                    "square_feet": 2000,
                    "build_year": 2010
                }
            }
        }
        
        response = requests.post(
            f"{MCP_BASE_URL}/mcp",
            json=tool_request,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if "result" in data:
                content = data["result"].get("content", [])
                if content and len(content) > 0:
                    result_text = content[0].get("text", "")
                    if result_text:
                        try:
                            result_data = json.loads(result_text)
                            print(f"   Climate Zone: {result_data.get('climate_zone', 'unknown')}")
                            print(f"   BTU Range: {result_data.get('btu_range_min', 'N/A')} - {result_data.get('btu_range_max', 'N/A')}")
                            print(f"   ✅ Quick sizer tool working")
                            return True, result_data
                        except json.JSONDecodeError:
                            print(f"   ❌ Invalid JSON in result: {result_text[:100]}...")
                            return False, None
                    else:
                        print(f"   ❌ Empty result content")
                        return False, None
                else:
                    print(f"   ❌ No content in result")
                    return False, None
            else:
                print(f"   ❌ Tool response invalid: {data}")
                return False, None
        else:
            print(f"   ❌ Tool request failed with status {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False, None
            
    except Exception as e:
        print(f"   ❌ Tool test error: {e}")
        return False, None

def main():
    """Run all tests"""
    print("🚀 Testing Hosted MCP Server")
    print(f"📍 Server: {MCP_BASE_URL}")
    print("=" * 60)
    
    results = []
    
    # Test 1: Health endpoint
    print("\n1️⃣ Health Check")
    health_success, health_data = test_health_endpoint()
    results.append(("Health Check", health_success))
    
    # Test 2: MCP initialization
    print("\n2️⃣ MCP Protocol")
    mcp_success, mcp_data = test_mcp_endpoint()
    results.append(("MCP Protocol", mcp_success))
    
    # Test 3: Tools listing
    print("\n3️⃣ Tools Listing")
    tools_success, tools_data = test_mcp_tools()
    results.append(("Tools Listing", tools_success))
    
    # Test 4: Tool execution
    print("\n4️⃣ Tool Execution")
    tool_success, tool_data = test_quick_sizer_tool()
    results.append(("Tool Execution", tool_success))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if health_data and 'version' in health_data:
        print(f"\n🔖 Server Version: {health_data['version']}")
        print(f"📅 Deployed: {health_data.get('deployment_timestamp', 'unknown')}")
        print(f"🔢 Build: #{health_data.get('build_id', 'unknown')}")
    
    # Exit with appropriate code
    return 0 if passed == total else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)