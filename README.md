# 🏠 HeatPumpHQ MCP Server

[![MCP Server Tests](https://github.com/jiweiqi/HeatPumpHQ/actions/workflows/test-mcp-server.yml/badge.svg)](https://github.com/jiweiqi/HeatPumpHQ/actions/workflows/test-mcp-server.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An MCP (Model Context Protocol) server that brings professional heat pump sizing, cost analysis, and performance verification directly to Claude. Get instant heat pump calculations, cost estimates, and cold-climate suitability analysis through natural conversation.

> 🚀 **NEW: Zero-Setup Hosted Version Available!** Most users should use our hosted MCP server at `https://mcp.wattsavy.com/mcp` - no Python installation required!

## 🚀 Quick Start

**No installation required!** Connect directly to our hosted MCP server:

### For Claude Desktop:
1. **Add to Claude Desktop config**:
   ```json
   {
     "mcpServers": {
       "heatpump": {
         "command": "npx",
         "args": ["-y", "@modelcontextprotocol/server-fetch", "https://mcp.wattsavy.com/mcp"]
       }
     }
   }
   ```

### For Claude Code:
1. **Run the following command** to install the MCP server:
   ```bash
   claude mcp add --transport http heatpump https://mcp.wattsavy.com/mcp
   ```

2. **Start calculating immediately**! Ask Claude:
   > *"Help me size a heat pump for my 2000 sq ft home in Boston"*

## 🛠️ What You Can Do

### 🏠 **Quick Sizing**
Get instant BTU requirements and equipment recommendations:
- Accounts for climate zone, home age, and square footage
- Returns specific heat pump models with efficiency ratings
- Considers single-zone and multi-zone configurations

### 💰 **Cost & Savings Analysis**  
Calculate 10-year cost projections and payback periods:
- Compare heat pump vs. current heating (gas, oil, electric)
- Real electricity rates and regional cost factors
- Monthly breakdown with seasonal variations

### ❄️ **Cold Climate Performance**
Verify heat pump viability in harsh winters:
- Capacity curves at design temperatures
- Backup heat requirements and recommendations
- Performance analysis down to -15°F and below

### 🔧 **Installation Cost Estimation**
Get comprehensive project cost breakdowns:
- Regional labor rates and permit costs
- Complexity assessment (ductwork, electrical, etc.)
- Rebate and incentive information

## 🌟 Why Use This MCP Server?

### ✅ **Zero Setup Benefits**
- **No Python installation** - Works immediately with any Claude Desktop setup
- **No dependency management** - No need to install packages or manage environments  
- **Auto-updated** - Always uses the latest features and fixes
- **High reliability** - 99.9% uptime with professional hosting
- **Better performance** - Dedicated server infrastructure

### 📋 Prerequisites
- **Claude Desktop or Claude Code** - That's it! No other requirements.

## 🏗️ Architecture Overview

This project provides **two MCP server implementations**:

1. **🌐 HTTP Server** (`server_http.py`) - For hosted/remote access
   - **Deployed at**: `https://mcp.wattsavy.com/mcp`
   - **Protocol**: HTTP POST + Server-Sent Events (SSE)
   - **Use case**: Zero-setup remote access via `@modelcontextprotocol/server-fetch`

2. **💻 FastMCP Server** (`server.py`) - For local installation
   - **Protocol**: JSON-RPC over stdio
   - **Use case**: Local development, offline access, customization

## ✅ Verify Installation

Test the connection by asking Claude: *"What tools are available for heat pump calculations?"*

## ⚙️ Configuration

### Configuration File Locations

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

## 🎯 Usage Examples

Ask Claude natural questions like:

### Sizing Questions
- *"What size heat pump do I need for a 1800 sq ft ranch built in 1995 in Denver?"*
- *"Help me size equipment for a 3-story home in climate zone 6A"*

### Cost Analysis  
- *"Compare the 10-year costs of keeping my gas furnace vs switching to a Mitsubishi heat pump"*
- *"What's the payback period for heat pump conversion in my area?"*

### Cold Climate Suitability
- *"Will heat pumps work in Minnesota winters for my 2500 sq ft home?"*
- *"At what temperature would I need backup heat with a Daikin cold-climate unit?"*

### Installation Planning
- *"Estimate total installation costs including electrical upgrades and permits"*
- *"What factors affect heat pump installation complexity?"*

## 🧪 Testing

Verify everything is working:

```bash
# Full test suite (recommended)
uv run python test_e2e.py --env production

# Basic functionality test
uv run python test_server.py

# Test specific environments
uv run python test_e2e.py --env local        # Local development
uv run python test_e2e.py --env production   # Production API
```

## 🏗️ API Reference

### Tools Available

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `quick_sizer` | Calculate BTU requirements | ZIP code, sq ft, build year |
| `bill_estimator` | Cost analysis & ROI | Home details, heat pump model, current fuel |
| `cold_climate_check` | Cold weather performance | Location, equipment model, backup heating |
| `project_cost_estimator` | Installation cost breakdown | Site complexity, regional factors |

### Resources Available

| Resource | Purpose |
|----------|---------|
| `heatpump://api-status` | Real-time backend health check |
| `heatpump://endpoints` | List of available calculation tools |

## 🔧 Development & Local Installation

**For developers who want to modify the server or need offline access:**

### Local Installation

```bash
# Clone and set up
git clone https://github.com/jiweiqi/heatpump-mcp-server.git
cd heatpump-mcp-server
uv sync  # or pip install -r requirements.txt

# Test the installation
uv run python test_e2e.py --env production
```

### Local Configuration

#### For Claude Desktop:
```json
{
  "mcpServers": {
    "heatpump": {
      "command": "uv",
      "args": [
        "--directory", 
        "/absolute/path/to/heatpump-mcp-server", 
        "run", 
        "python", 
        "server.py"
      ],
      "env": {
        "ENV_MODE": "production"
      }
    }
  }
}
```

#### For Claude Code:
```bash
claude mcp add --transport stdio heatpump "uv --directory /absolute/path/to/heatpump-mcp-server run python server.py"
```

### Environment Configuration

```bash
# Copy example configuration
cp .env.example .env

# For local development (optional)
# Edit .env to point to your local backend
HEATPUMP_API_URL=http://localhost:8000
```

### Prerequisites for Local Installation
- **Python 3.8+**
- **uv** (recommended) or pip package manager
- **Claude Desktop or Claude Code**

### Project Structure

```
heatpump-mcp-server/
├── server.py              # FastMCP server (local/stdio)
├── server_http.py          # HTTP+SSE server (hosted)
├── test_e2e.py            # Comprehensive test suite
├── test_server.py          # Basic functionality tests
├── run_tests.sh           # Test runner script
├── Dockerfile             # Docker container config
├── requirements.txt        # Python dependencies
├── pyproject.toml         # Python project config
├── uv.lock                # UV lock file
├── LICENSE                # MIT license
└── README.md              # This documentation
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run the test suite: `./run_tests.sh`
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open a pull request

## 📄 License

MIT License - see the [LICENSE](LICENSE) file for details.

## 🏢 About WattSavy

This MCP server is powered by the [WattSavy](https://www.wattsavy.com) heat pump calculation engine, providing:

- ✅ **Real data**: 40,000+ ZIP codes, TMY3 weather data, actual equipment models
- ✅ **Accurate calculations**: Manual J-compliant load calculations
- ✅ **Current pricing**: Real-time electricity rates via EIA API
- ✅ **Professional tools**: Used by HVAC contractors and homeowners

## 🆘 Support

- 📖 **Documentation**: This README and inline code comments
- 🐛 **Issues**: [GitHub Issues](https://github.com/jiweiqi/heatpump-mcp-server/issues)
- 💬 **Questions**: Create a discussion on GitHub
- 🌐 **Website**: [WattSavy.com](https://www.wattsavy.com)

## 📈 Changelog

### v0.3.0 (Current)
- 🚀 **NEW: Hosted MCP Server** at `https://mcp.wattsavy.com/mcp`
- ✅ **Zero-setup option** - No Python or local installation required
- ✅ **Auto-updating** - Always uses latest features and bug fixes  
- ✅ **High reliability** - Professional hosting with 99.9% uptime
- ✅ **Better performance** - Dedicated server infrastructure
- ✅ **Updated README** - Hosted version now the recommended default
- ✅ **Automatic publishing** - GitHub Actions auto-publishes on changes

### v0.2.0
- ✅ Updated for WattSavy production API (api.wattsavy.com)
- ✅ Comprehensive E2E test suite with 100% pass rate
- ✅ Environment-specific configurations (production/local)
- ✅ Enhanced error handling and validation
- ✅ Real-time API status monitoring
- ✅ Updated parameter validation for all endpoints

### v0.1.0
- Initial release with core calculation tools
- Basic Claude Desktop integration

---

**Made with ❤️ for the heat pump community**