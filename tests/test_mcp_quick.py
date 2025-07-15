#!/usr/bin/env python3
"""Quick MCP server connectivity test without pytest dependency."""

import requests
import sys
import time

MCP_BASE_URL = "https://mcp.wattsavy.com"
TIMEOUT_SECONDS = 30

def test_endpoint(url, description, expected_codes=None):
    """Test a single endpoint and return results."""
    if expected_codes is None:
        expected_codes = [200]
    
    try:
        start_time = time.time()
        response = requests.get(url, timeout=TIMEOUT_SECONDS)
        end_time = time.time()
        response_time = end_time - start_time
        
        status = "✅ PASS" if response.status_code in expected_codes else "❌ FAIL"
        print(f"{status} {description}")
        print(f"    URL: {url}")
        print(f"    Status: {response.status_code}")
        print(f"    Time: {response_time:.2f}s")
        
        if response.status_code not in expected_codes:
            print(f"    Expected: {expected_codes}, Got: {response.status_code}")
            try:
                print(f"    Response: {response.text[:200]}...")
            except:
                pass
        
        print()
        return response.status_code in expected_codes
        
    except requests.exceptions.RequestException as e:
        print(f"❌ FAIL {description}")
        print(f"    URL: {url}")
        print(f"    Error: {e}")
        print()
        return False

def test_oauth_metadata():
    """Test OAuth metadata endpoints that were failing."""
    oauth_endpoints = [
        "/.well-known/oauth-authorization-server",
        "/.well-known/openid_configuration", 
        "/oauth/metadata",
        "/.well-known/mcp-metadata"
    ]
    
    print("Testing OAuth/metadata endpoints:")
    working_endpoints = []
    
    for endpoint in oauth_endpoints:
        url = f"{MCP_BASE_URL}{endpoint}"
        try:
            response = requests.get(url, timeout=TIMEOUT_SECONDS)
            if response.status_code == 200:
                working_endpoints.append(endpoint)
                print(f"✅ {endpoint} - Working (200)")
            elif response.status_code == 404:
                print(f"ℹ️  {endpoint} - Not found (404) - OK")
            elif response.status_code in [502, 503]:
                print(f"❌ {endpoint} - Server error ({response.status_code}) - PROBLEM!")
                return False
            else:
                print(f"ℹ️  {endpoint} - Status {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint} - Connection error: {e}")
            return False
    
    print(f"Working OAuth endpoints: {working_endpoints}")
    print()
    return True

def main():
    """Run all MCP smoke tests."""
    print("🔍 Running MCP Server Smoke Tests")
    print(f"Target: {MCP_BASE_URL}")
    print("=" * 50)
    
    all_passed = True
    
    # Basic connectivity tests
    tests = [
        (f"{MCP_BASE_URL}/health", "Health endpoint", [200]),
        (f"{MCP_BASE_URL}/", "Root endpoint", [200, 404]),
        (f"{MCP_BASE_URL}/mcp", "MCP protocol endpoint", [200, 400, 405, 422]),
        (f"{MCP_BASE_URL}/mcp/sse", "SSE endpoint", [200, 400, 405, 422]),
    ]
    
    for url, description, expected_codes in tests:
        if not test_endpoint(url, description, expected_codes):
            all_passed = False
    
    # OAuth metadata test (the problematic one)
    if not test_oauth_metadata():
        all_passed = False
    
    # Summary
    if all_passed:
        print("✅ All MCP smoke tests passed!")
        return 0
    else:
        print("❌ Some MCP smoke tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())