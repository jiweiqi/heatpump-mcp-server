#!/usr/bin/env python3
"""
Simple MCP Server Test - Basic validation without dependencies
"""

import json
import os
import sys

# Test MCP server configuration
def test_mcp_config():
    """Test MCP configuration files"""
    print("🧪 Testing MCP Server Configuration")
    print("=" * 50)
    
    # Test mcp.json
    try:
        with open('mcp.json', 'r') as f:
            mcp_config = json.load(f)
        
        print("✅ mcp.json: Valid JSON")
        print(f"   - Protocol Version: {mcp_config.get('protocolVersion')}")
        print(f"   - Tool Count: {len(mcp_config['capabilities']['tools']['names'])}")
        print(f"   - Transport: {', '.join(mcp_config['transport'].keys())}")
        
    except Exception as e:
        print(f"❌ mcp.json: Error - {e}")
        return False
    
    # Test VS Code config
    try:
        with open('.vscode/mcp.json', 'r') as f:
            vscode_config = json.load(f)
        
        print("✅ .vscode/mcp.json: Valid JSON")
        print(f"   - Server Count: {len(vscode_config['servers'])}")
        
    except Exception as e:
        print(f"❌ .vscode/mcp.json: Error - {e}")
    
    # Test server syntax
    try:
        with open('server.py', 'r') as f:
            server_code = f.read()
        
        if 'API_BASE_URL' in server_code and 'make_api_request' in server_code:
            print("✅ server.py: Basic structure OK")
        else:
            print("❌ server.py: Missing key components")
            return False
            
    except Exception as e:
        print(f"❌ server.py: Error - {e}")
        return False
    
    print("\n🎉 Configuration validation complete!")
    return True

def test_api_connectivity():
    """Test backend API connectivity"""
    print("\n🌐 Testing Backend API Connectivity")
    print("=" * 50)
    
    import urllib.request
    import urllib.error
    
    # Test API endpoints
    endpoints = [
        "https://api.wattsavy.com/health",
        "https://api.wattsavy.com/",
        "https://api.wattsavy.com/api/quick-sizer/calculate",  # POST endpoint
    ]
    
    for endpoint in endpoints:
        try:
            if endpoint.endswith('/calculate'):
                # POST request
                data = json.dumps({"zip_code": "10001", "square_feet": 2000, "build_year": 2020}).encode()
                req = urllib.request.Request(endpoint, data=data, headers={'Content-Type': 'application/json'})
                response = urllib.request.urlopen(req, timeout=10)
                status = response.getcode()
            else:
                # GET request
                response = urllib.request.urlopen(endpoint, timeout=10)
                status = response.getcode()
            
            if status == 200:
                print(f"✅ {endpoint}: HTTP {status}")
            else:
                print(f"⚠️ {endpoint}: HTTP {status}")
                
        except urllib.error.HTTPError as e:
            print(f"❌ {endpoint}: HTTP {e.code} - {e.reason}")
        except Exception as e:
            print(f"❌ {endpoint}: Error - {e}")

if __name__ == "__main__":
    print("🚀 HeatPumpHQ MCP Server - Simple Test Suite")
    print("=" * 60)
    
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    success = test_mcp_config()
    test_api_connectivity()
    
    if success:
        print("\n✅ Basic tests passed - MCP server configuration is valid")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed - check configuration")
        sys.exit(1)