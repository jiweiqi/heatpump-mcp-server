#!/usr/bin/env python3
"""
Quick deployment check for MCP server
"""
import requests
import sys

def check_deployment():
    urls = [
        "https://mcp.wattsavy.com/health",
        "https://mcp.wattsavy.com/",
        "https://api.wattsavy.com/health"
    ]
    
    print("🔍 Checking deployment status...")
    
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {url} - HTTP {response.status_code}")
            
            if response.status_code == 502:
                print("   → Server is down or not deployed")
            elif response.status_code == 200:
                try:
                    data = response.json()
                    if 'status' in data:
                        print(f"   → Status: {data['status']}")
                except:
                    print("   → Non-JSON response")
                    
        except requests.exceptions.ConnectionError:
            print(f"❌ {url} - Connection refused")
        except requests.exceptions.Timeout:
            print(f"❌ {url} - Timeout")
        except Exception as e:
            print(f"❌ {url} - Error: {e}")
    
    print("\n💡 To deploy the MCP server:")
    print("   1. SSH to EC2 instance")
    print("   2. cd /home/ubuntu/HeatPumpHQ/mcp-server")
    print("   3. git pull origin main")
    print("   4. docker build -t heatpump-mcp:latest .")
    print("   5. docker stop heatpump-mcp && docker rm heatpump-mcp")
    print("   6. docker run -d --name heatpump-mcp --restart unless-stopped -p 3002:3002 \\")
    print("      -e API_BASE_URL=https://api.wattsavy.com -e LOG_LEVEL=INFO \\")
    print("      -e MCP_HTTP_HOST=0.0.0.0 -e MCP_HTTP_PORT=3002 heatpump-mcp:latest")

if __name__ == "__main__":
    check_deployment()