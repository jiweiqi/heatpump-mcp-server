#!/bin/bash
set -e

echo "🚀 Deploying HeatPumpHQ MCP Server..."
echo "📍 Location: $(pwd)"
echo "🕐 Time: $(date)"
echo "=" * 60

# Step 1: Pull latest changes
echo "📥 Pulling latest changes..."
git fetch origin
git reset --hard origin/main

# Step 2: Navigate to mcp-server directory
cd mcp-server

# Step 3: Build Docker image
echo "🏗️  Building Docker image..."
docker build -t heatpump-mcp:latest . || {
    echo "❌ Docker build failed"
    exit 1
}

# Step 4: Stop and remove existing container
echo "🔄 Stopping existing container..."
docker stop heatpump-mcp 2>/dev/null || echo "No existing container to stop"
docker rm heatpump-mcp 2>/dev/null || echo "No existing container to remove"

# Step 5: Start new container
echo "🚀 Starting new container..."
docker run -d \
    --name heatpump-mcp \
    --restart unless-stopped \
    -p 3002:3002 \
    -e API_BASE_URL=https://api.wattsavy.com \
    -e LOG_LEVEL=INFO \
    -e MCP_HTTP_HOST=0.0.0.0 \
    -e MCP_HTTP_PORT=3002 \
    -e MCP_ALLOWED_ORIGINS="*" \
    --health-cmd="curl -f http://localhost:3002/health || exit 1" \
    --health-interval=30s \
    --health-timeout=10s \
    --health-retries=3 \
    heatpump-mcp:latest || {
    echo "❌ Container start failed"
    exit 1
}

# Step 6: Wait for container to be healthy
echo "⏳ Waiting for container to be healthy..."
timeout 60 bash -c 'until docker ps | grep heatpump-mcp | grep -q "(healthy)"; do sleep 2; done' || {
    echo "❌ Container failed to become healthy"
    echo "🔍 Container logs:"
    docker logs heatpump-mcp --tail 20
    exit 1
}

# Step 7: Verify deployment
echo "✅ Container is healthy!"
echo "🔍 Container status:"
docker ps | grep heatpump-mcp

echo "🔍 Testing endpoints..."
echo "  Health endpoint:"
curl -s http://localhost:3002/health | head -c 200
echo ""

echo "  Root endpoint:"
curl -s http://localhost:3002/ | head -c 200
echo ""

echo "✅ Deployment successful!"
echo "🌐 MCP server should be accessible at:"
echo "  - Local: http://localhost:3002"
echo "  - External: https://mcp.wattsavy.com"
echo ""
echo "💡 To check logs: docker logs heatpump-mcp"
echo "💡 To restart: docker restart heatpump-mcp"