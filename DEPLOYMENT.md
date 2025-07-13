# MCP Server Deployment Guide

## 🚀 Deployment Status: Ready for Production

The enhanced MCP server with 2025-03-26 protocol compliance has been committed and pushed to the repository. Follow this guide to deploy the updated server.

## 📋 Pre-Deployment Checklist

### ✅ Code Changes Committed
- [x] Enhanced MCP server with 2025-03-26 protocol support
- [x] Updated manifest files (`mcp.json`, VS Code config)
- [x] Improved tool metadata and error handling
- [x] Added comprehensive documentation
- [x] All changes pushed to `main` branch (commit: `5c3d862`)

### ✅ Validation Completed
- [x] Python syntax validation passed
- [x] JSON configuration files validated
- [x] MCP protocol compliance tests created
- [x] Documentation updated

## 🏗️ Deployment Options

### Option 1: Docker Deployment (Recommended)

```bash
# 1. SSH to your AWS EC2 instance
ssh your-ec2-instance

# 2. Navigate to project directory
cd /path/to/HeatPumpHQ

# 3. Pull latest changes
git pull origin main

# 4. Build updated Docker image
cd mcp-server
docker build -t heatpump-mcp:latest .

# 5. Stop existing container (if running)
docker stop heatpump-mcp || true

# 6. Run updated container
docker run -d \
  --name heatpump-mcp \
  --restart unless-stopped \
  -p 3002:3002 \
  -e API_BASE_URL=https://api.wattsavy.com \
  -e LOG_LEVEL=INFO \
  heatpump-mcp:latest

# 7. Verify deployment
docker logs heatpump-mcp
curl http://localhost:3002/health
```

### Option 2: Direct Python Deployment

```bash
# 1. SSH to your deployment server
ssh your-server

# 2. Navigate and update code
cd /path/to/HeatPumpHQ/mcp-server
git pull origin main

# 3. Install/update dependencies
uv sync  # or pip install -r requirements.txt

# 4. Set environment variables
export API_BASE_URL=https://api.wattsavy.com
export LOG_LEVEL=INFO

# 5. Stop existing process and start new one
pkill -f server_http.py  # Stop existing
nohup python server_http.py > mcp_server.log 2>&1 &

# 6. Verify deployment
curl http://localhost:3002/health
tail -f mcp_server.log
```

## 🔧 Environment Configuration

### Required Environment Variables
```bash
# Production API endpoint
export API_BASE_URL=https://api.wattsavy.com

# Optional: Logging level
export LOG_LEVEL=INFO

# Optional: HTTP server configuration
export MCP_HTTP_HOST=0.0.0.0
export MCP_HTTP_PORT=3002
export MCP_ALLOWED_ORIGINS=*
```

### Production Environment File
Create `/path/to/HeatPumpHQ/mcp-server/.env.production`:
```
API_BASE_URL=https://api.wattsavy.com
LOG_LEVEL=INFO
MCP_HTTP_HOST=0.0.0.0
MCP_HTTP_PORT=3002
MCP_ALLOWED_ORIGINS=*
```

## 🧪 Post-Deployment Verification

### 1. Health Check
```bash
curl http://localhost:3002/health
# Expected: {"status":"healthy","server":"HeatPumpHQ MCP HTTP Server",...}
```

### 2. MCP Protocol Test
```bash
curl -X POST http://localhost:3002/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2025-03-26",
      "clientInfo": {"name": "Test Client", "version": "1.0.0"}
    }
  }'
# Expected: Protocol version 2025-03-26 with enhanced capabilities
```

### 3. Tools Listing Test
```bash
curl -X POST http://localhost:3002/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
  }'
# Expected: 4 tools with 2025-03-26 annotations
```

### 4. Functional Test
```bash
curl -X POST http://localhost:3002/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "quick_sizer",
      "arguments": {
        "zip_code": "10001",
        "square_feet": 2000,
        "build_year": 2020
      }
    }
  }'
# Expected: Heat pump sizing calculation results
```

## 🌐 External Access Configuration

### Nginx Reverse Proxy (if needed)
```nginx
# Add to your Nginx configuration
location /mcp {
    proxy_pass http://localhost:3002;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_cache_bypass $http_upgrade;
}

location /mcp/sse {
    proxy_pass http://localhost:3002/mcp/sse;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_cache off;
    proxy_buffering off;
}
```

### Firewall Configuration
```bash
# Allow MCP server port (if needed)
sudo ufw allow 3002/tcp
```

## 📊 Monitoring & Logs

### Log Locations
```bash
# Docker deployment
docker logs heatpump-mcp

# Direct deployment
tail -f mcp_server.log
journalctl -u heatpump-mcp  # if using systemd
```

### Performance Monitoring
```bash
# Check server responsiveness
curl -w "@-" -o /dev/null -s http://localhost:3002/health <<< "
     time_namelookup:  %{time_namelookup}\n
        time_connect:  %{time_connect}\n
     time_appconnect:  %{time_appconnect}\n
    time_pretransfer:  %{time_pretransfer}\n
       time_redirect:  %{time_redirect}\n
  time_starttransfer:  %{time_starttransfer}\n
                     ----------\n
          time_total:  %{time_total}\n
"
```

## 🚨 Troubleshooting

### Common Issues

**1. Port Already in Use**
```bash
sudo lsof -i :3002
sudo kill -9 <PID>
```

**2. Permission Denied**
```bash
sudo chown -R $USER:$USER /path/to/HeatPumpHQ/mcp-server
chmod +x server_http.py
```

**3. Module Import Errors**
```bash
cd /path/to/HeatPumpHQ/mcp-server
pip install -r requirements.txt
# or
uv sync
```

**4. API Connection Issues**
```bash
# Test backend API connectivity
curl https://api.wattsavy.com/health
# Verify firewall and network settings
```

## 🎯 Success Criteria

✅ **Deployment Successful When:**
- Health check returns HTTP 200
- MCP initialize method returns protocol version 2025-03-26
- All 4 tools list with proper annotations
- Quick sizer tool executes successfully
- Logs show no errors

## 📞 Next Steps

1. **Deploy using preferred method above**
2. **Run post-deployment verification tests**
3. **Update any client configurations if needed**
4. **Monitor logs for initial traffic**
5. **Test with Claude Code/Desktop to verify compatibility**

---

**🤖 Enhanced MCP Server Features:**
- ✅ 2025-03-26 Protocol Compliance
- ✅ Enhanced Tool Metadata
- ✅ Standardized Error Handling  
- ✅ Multiple Transport Support
- ✅ Production-Ready Deployment