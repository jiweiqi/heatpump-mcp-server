# HeatPumpHQ Remote MCP Server

A WebSocket-based Model Context Protocol (MCP) server that provides remote access to HeatPumpHQ's heat pump calculation APIs. Enables AI assistants like Claude Code to access heat pump tools without local installation.

## 🌐 Remote Access

**Production WebSocket URL**: `wss://mcp.wattsavy.com/mcp`

### Quick Setup for Claude Code/Cursor

Add this MCP server configuration to your client:

```json
{
  "name": "HeatPumpHQ",
  "type": "websocket",
  "url": "wss://mcp.wattsavy.com/mcp",
  "description": "Heat pump sizing, cost estimation, and performance analysis tools"
}
```

## 🛠️ Available Tools

### 1. **quick_sizer**
Calculate required BTU capacity for heat pump based on home characteristics.

**Parameters:**
- `zip_code` (string): 5-digit US ZIP code
- `square_feet` (integer): Home square footage (100-10000)
- `build_year` (integer): Year home was built (1900-2025)

### 2. **bill_estimator**
Estimate electricity costs and ROI for heat pump vs current heating system.

**Parameters:**
- `zip_code`, `square_feet`, `build_year` (same as above)
- `heat_pump_model` (string): e.g., "Mitsubishi MXZ-3C24NA"
- `current_heating_fuel` (string): gas, electric, oil, propane
- `gas_price_per_therm` (number, optional)
- `electricity_rate_override` (number, optional)

### 3. **cold_climate_check**
Verify heat pump performance at design temperatures for cold climates.

**Parameters:**
- `zip_code`, `square_feet`, `build_year`, `heat_pump_model` (same as above)
- `existing_backup_heat` (string, optional): electric_strip, gas_furnace, oil_boiler, none

### 4. **project_cost_estimator**
Estimate total project costs for heat pump installation.

**Parameters:**
- `zip_code`, `square_feet`, `build_year`, `heat_pump_model` (same as above)
- `existing_heating_type` (string): gas_furnace, electric_baseboard, oil_boiler, etc.
- `ductwork_condition` (string): good, fair, poor, none
- `home_stories` (integer): 1-4
- `insulation_quality` (string): excellent, good, fair, poor
- `air_sealing` (string): excellent, good, fair, poor

## 🔧 Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MCP Client    │    │   EC2 Instance   │    │  Backend API    │
│   (Claude.ai)   │    │                  │    │  (FastAPI)      │
│                 │    │  ┌─────────────┐ │    │                 │
│  WSS Connection │────┼──│ MCP Server  │─┼────│  Port 8000      │
│                 │    │  │ Port 3001   │ │    │                 │
│                 │    │  └─────────────┘ │    │                 │
│                 │    │                  │    │                 │
│                 │    │  ┌─────────────┐ │    │                 │
│                 │    │  │    Nginx    │ │    │                 │
│                 │    │  │ Port 80/443 │ │    │                 │
│                 │    │  └─────────────┘ │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Components:
- **MCP WebSocket Server**: Custom transport implementing JSON-RPC 2.0 over WebSocket
- **Nginx Proxy**: Handles WSS termination and WebSocket upgrades  
- **Cloudflare DNS**: `mcp.wattsavy.com` → EC2 instance
- **Backend API**: Existing FastAPI server with heat pump calculation logic

## 🔒 Security Features

- **Origin Validation**: Only allowed origins can connect
- **HTTPS/WSS Only**: Secure WebSocket connections required
- **JSON-RPC 2.0**: Standardized message format per MCP specification
- **Optional Authentication**: Bearer token support for production use
- **Rate Limiting**: Built-in connection limits and timeouts

## 📋 MCP Protocol Compliance

Implements MCP 2025 specification with custom WebSocket transport:
- ✅ JSON-RPC 2.0 message format
- ✅ Standard MCP initialization handshake
- ✅ Tool discovery via `tools/list`
- ✅ Tool execution via `tools/call`
- ✅ Resource access via `resources/list`
- ✅ Proper error handling and validation

## 🚀 Deployment

### For End Users (Client Setup)

1. **Add to Claude Code/Cursor config:**
   ```json
   {
     "mcp": {
       "servers": {
         "heatpump": {
           "command": "websocket",
           "args": ["wss://mcp.wattsavy.com/mcp"]
         }
       }
     }
   }
   ```

2. **Test connection:**
   ```javascript
   // In Claude Code or MCP client
   await mcp.listTools(); // Should return 4 heat pump tools
   ```

### For Server Deployment (Maintainers)

1. **Deploy to EC2:**
   ```bash
   # From project root
   cd backend
   docker-compose up -d --build
   ```

2. **Verify services:**
   ```bash
   # Check MCP server
   curl -i -N -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Key: test" \
     http://mcp.wattsavy.com/mcp

   # Check backend API
   curl https://api.wattsavy.com/health
   ```

3. **Monitor logs:**
   ```bash
   docker logs heatpump-mcp -f
   docker logs heatpump-nginx -f
   ```

## 🧪 Testing

### Local Testing
```bash
# Test WebSocket server locally
cd mcp-server
python websocket_server.py

# Test with wscat
npm install -g wscat
wscat -c ws://localhost:3001
```

### Production Testing
```bash
# Test remote connection
wscat -c wss://mcp.wattsavy.com/mcp

# Send MCP initialization
{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
```

## 💡 Usage Examples

### Quick Home Sizing
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "quick_sizer",
    "arguments": {
      "zip_code": "10001",
      "square_feet": 1500,
      "build_year": 2000
    }
  }
}
```

### Cold Climate Analysis
```json
{
  "jsonrpc": "2.0", 
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "cold_climate_check",
    "arguments": {
      "zip_code": "55104",
      "square_feet": 2000,
      "build_year": 1995,
      "heat_pump_model": "Mitsubishi MXZ-4C36NA"
    }
  }
}
```

## 🔧 Configuration

### Environment Variables
- `MCP_WS_HOST`: WebSocket server host (default: 0.0.0.0)
- `MCP_WS_PORT`: WebSocket server port (default: 3001)
- `HEATPUMP_API_URL`: Backend API URL (default: http://backend:8000)
- `MCP_ALLOWED_ORIGINS`: Comma-separated allowed origins
- `MCP_AUTH_TOKEN`: Optional authentication token
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

### Performance Tuning
- Max message size: 1MB
- Connection timeout: 60 seconds
- Ping interval: 20 seconds
- Max concurrent connections: Limited by Docker resources

## 📊 Benefits vs Local Installation

| Feature | Remote MCP | Local MCP |
|---------|------------|-----------|
| Installation | ✅ Zero setup | ❌ Requires Python/deps |
| Maintenance | ✅ Auto-updated | ❌ Manual updates |
| Performance | ✅ Dedicated server | ⚠️ Varies by local machine |
| Security | ✅ Controlled environment | ⚠️ Local network exposure |
| Reliability | ✅ 99.9% uptime | ⚠️ Depends on local machine |
| Latency | ⚠️ Network dependent | ✅ Local processing |

## 🆘 Troubleshooting

### Connection Issues
- **CORS errors**: Check allowed origins configuration
- **SSL/TLS errors**: Verify Cloudflare SSL settings
- **Timeout errors**: Check network connectivity and EC2 health

### Tool Execution Issues  
- **API errors**: Verify backend API is running (`curl https://api.wattsavy.com/health`)
- **Invalid parameters**: Check tool schemas and validation rules
- **Rate limiting**: Reduce request frequency

### Server Issues
- **Container not starting**: Check Docker logs and resource limits
- **WebSocket upgrade failures**: Verify Nginx configuration
- **DNS resolution**: Verify `mcp.wattsavy.com` points to correct IP

## 📞 Support

For issues or feature requests:
- **Repository**: https://github.com/your-org/HeatPumpHQ
- **Issues**: Create GitHub issue with logs and error details
- **API Status**: https://api.wattsavy.com/health
- **Server Status**: `wss://mcp.wattsavy.com/mcp` connection test