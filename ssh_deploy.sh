#!/bin/bash

# SSH deployment script for MCP server
# Usage: ./ssh_deploy.sh [ssh_key_path] [ec2_host]

SSH_KEY="${1:-~/.ssh/heatpump-key-1752365764.pem}"
EC2_HOST="${2:-ubuntu@44.222.72.185}"

echo "🚀 Deploying MCP Server via SSH..."
echo "📍 SSH Key: $SSH_KEY"
echo "🌐 EC2 Host: $EC2_HOST"
echo ""

# Check if SSH key exists
if [ ! -f "$SSH_KEY" ]; then
    echo "❌ SSH key not found: $SSH_KEY"
    echo "💡 Please update the SSH_KEY path in this script"
    exit 1
fi

# Deploy via SSH
echo "📤 Executing deployment on EC2..."
ssh -i "$SSH_KEY" "$EC2_HOST" << 'EOF'
    set -e
    
    echo "🚀 Starting MCP Server deployment on EC2..."
    echo "📍 Current directory: $(pwd)"
    echo "🕐 Time: $(date)"
    
    # Navigate to project directory
    cd /home/ubuntu/HeatPumpHQ || { echo "❌ Project directory not found"; exit 1; }
    
    echo "📥 Pulling latest changes..."
    git fetch origin
    git reset --hard origin/main
    
    # Navigate to mcp-server directory
    cd mcp-server
    
    echo "🏗️  Building Docker image..."
    docker build -t heatpump-mcp:latest . || { echo "❌ Docker build failed"; exit 1; }
    
    echo "🔄 Stopping existing container..."
    docker stop heatpump-mcp 2>/dev/null || echo "No existing container to stop"
    docker rm heatpump-mcp 2>/dev/null || echo "No existing container to remove"
    
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
        heatpump-mcp:latest || { echo "❌ Container start failed"; exit 1; }
    
    echo "⏳ Waiting for container to be healthy..."
    timeout 60 bash -c 'until docker ps | grep heatpump-mcp | grep -q "(healthy)"; do sleep 2; echo "Waiting..."; done' || {
        echo "❌ Container failed to become healthy"
        echo "🔍 Container logs:"
        docker logs heatpump-mcp --tail 20
        exit 1
    }
    
    echo "✅ Container is healthy!"
    echo "🔍 Container status:"
    docker ps | grep heatpump-mcp
    
    echo "🔍 Testing local endpoints..."
    echo "Health endpoint:"
    curl -s http://localhost:3002/health || echo "Health endpoint failed"
    
    echo -e "\n✅ Deployment successful!"
    echo "🌐 MCP server should be accessible at https://mcp.wattsavy.com"
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SSH deployment completed successfully!"
    echo "🔍 Running verification..."
    echo ""
    
    # Wait a moment for the service to be fully ready
    sleep 5
    
    # Run verification
    ./verify_deployment.sh
else
    echo "❌ SSH deployment failed!"
    exit 1
fi