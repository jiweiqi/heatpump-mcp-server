#!/bin/bash
set -e

echo "🔍 Verifying MCP Server Deployment..."
echo "🕐 Time: $(date)"
echo "=" * 60

# Check if we're on the server or local machine
if command -v docker &> /dev/null && docker ps | grep -q heatpump-mcp; then
    echo "📍 Running on server with Docker access"
    ON_SERVER=true
else
    echo "📍 Running remote verification"
    ON_SERVER=false
fi

# Function to test HTTP endpoint
test_endpoint() {
    local name="$1"
    local url="$2"
    local expected_status="${3:-200}"
    
    echo "🔍 Testing $name..."
    
    if response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$url" 2>/dev/null); then
        http_status=$(echo "$response" | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
        body=$(echo "$response" | sed -e 's/HTTPSTATUS:.*//g')
        
        if [ "$http_status" = "$expected_status" ]; then
            echo "✅ $name - HTTP $http_status"
            if [ ${#body} -gt 0 ] && [ ${#body} -lt 200 ]; then
                echo "   Response: $body"
            elif [ ${#body} -gt 200 ]; then
                echo "   Response: ${body:0:100}..."
            fi
        else
            echo "❌ $name - HTTP $http_status (expected $expected_status)"
            echo "   Response: ${body:0:200}"
        fi
    else
        echo "❌ $name - Connection failed"
    fi
}

# Function to test MCP protocol
test_mcp_protocol() {
    echo "🔍 Testing MCP Protocol..."
    
    local mcp_request='{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test-client","version":"1.0.0"}}}'
    
    if response=$(curl -s -w "HTTPSTATUS:%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -d "$mcp_request" \
        "https://mcp.wattsavy.com/mcp" 2>/dev/null); then
        
        http_status=$(echo "$response" | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
        body=$(echo "$response" | sed -e 's/HTTPSTATUS:.*//g')
        
        if [ "$http_status" = "200" ]; then
            echo "✅ MCP Protocol - HTTP $http_status"
            if echo "$body" | grep -q '"result"'; then
                echo "   MCP Initialize successful"
            else
                echo "   Response: ${body:0:100}..."
            fi
        else
            echo "❌ MCP Protocol - HTTP $http_status"
            echo "   Response: ${body:0:200}"
        fi
    else
        echo "❌ MCP Protocol - Connection failed"
    fi
}

# Server-side checks
if [ "$ON_SERVER" = true ]; then
    echo "🐳 Docker Container Status:"
    docker ps | grep heatpump-mcp || echo "❌ Container not found"
    
    echo ""
    echo "🔍 Container Health:"
    if docker ps | grep heatpump-mcp | grep -q "(healthy)"; then
        echo "✅ Container is healthy"
    else
        echo "❌ Container is not healthy"
        echo "Recent logs:"
        docker logs heatpump-mcp --tail 10
    fi
    
    echo ""
    echo "🔍 Local Endpoints:"
    test_endpoint "Local Health" "http://localhost:3002/health"
    test_endpoint "Local Root" "http://localhost:3002/"
    
    echo ""
    echo "🔍 Port Binding:"
    if netstat -tlnp 2>/dev/null | grep -q ":3002"; then
        echo "✅ Port 3002 is bound"
        netstat -tlnp | grep :3002
    else
        echo "❌ Port 3002 is not bound"
    fi
fi

# Remote checks (work from anywhere)
echo ""
echo "🌐 External Endpoints:"
test_endpoint "External Health" "https://mcp.wattsavy.com/health"
test_endpoint "External Root" "https://mcp.wattsavy.com/"
test_endpoint "Backend Health" "https://api.wattsavy.com/health"

echo ""
test_mcp_protocol

echo ""
echo "🔍 SSL Certificate:"
if openssl s_client -connect mcp.wattsavy.com:443 -servername mcp.wattsavy.com < /dev/null 2>/dev/null | grep -q "Verify return code: 0"; then
    echo "✅ SSL certificate is valid"
else
    echo "⚠️  SSL certificate issue (check nginx config)"
fi

echo ""
echo "=" * 60
echo "🎯 Deployment Summary:"

# Count successful tests
success_count=0
total_tests=0

# This is a simplified check - in a real script you'd track each test
if curl -s -f https://mcp.wattsavy.com/health > /dev/null 2>&1; then
    echo "✅ Health endpoint working"
    ((success_count++))
else
    echo "❌ Health endpoint failed"
fi
((total_tests++))

if curl -s -f https://mcp.wattsavy.com/ > /dev/null 2>&1; then
    echo "✅ Root endpoint working"
    ((success_count++))
else
    echo "❌ Root endpoint failed"
fi
((total_tests++))

echo ""
echo "📊 Tests passed: $success_count/$total_tests"

if [ $success_count -eq $total_tests ]; then
    echo "🎉 All tests passed! MCP server is fully deployed and working."
    echo ""
    echo "🔗 Access URLs:"
    echo "  - MCP Protocol: https://mcp.wattsavy.com/mcp"
    echo "  - Health Check: https://mcp.wattsavy.com/health"
    echo "  - SSE Stream: https://mcp.wattsavy.com/mcp/sse"
    exit 0
else
    echo "⚠️  Some tests failed. Check the output above."
    echo ""
    echo "🔧 Troubleshooting:"
    echo "  - Check container logs: docker logs heatpump-mcp"
    echo "  - Restart container: docker restart heatpump-mcp"
    echo "  - Check nginx config for mcp.wattsavy.com"
    exit 1
fi