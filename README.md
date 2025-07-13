# 🏠 HeatPumpHQ MCP Server

[![MCP Server Tests](https://github.com/jiweiqi/HeatPumpHQ/actions/workflows/test-mcp-server.yml/badge.svg)](https://github.com/jiweiqi/HeatPumpHQ/actions/workflows/test-mcp-server.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An MCP (Model Context Protocol) server that brings professional heat pump sizing, cost analysis, and performance verification directly to Claude. Get instant heat pump calculations, cost estimates, and cold-climate suitability analysis through natural conversation.

## 🚀 Quick Start

### For Claude Desktop Users

1. **Install the server**:
   ```bash
   git clone https://github.com/jiweiqi/heatpump-mcp-server.git
   cd heatpump-mcp-server
   uv sync  # or pip install -r requirements.txt
   ```

2. **Add to Claude Desktop config**:
   ```json
   {
     "mcpServers": {
       "heatpump": {
         "command": "uv",
         "args": ["--directory", "/path/to/heatpump-mcp-server", "run", "python", "server.py"]
       }
     }
   }
   ```

3. **Start calculating**! Ask Claude:
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

## 📋 Prerequisites

- **Python 3.8+**
- **uv** (recommended) or pip package manager
- **Claude Desktop** (for easiest usage)

## 📦 Installation

### Option 1: Using uv (Recommended)

```bash
# Clone and set up
git clone https://github.com/jiweiqi/heatpump-mcp-server.git
cd heatpump-mcp-server
uv sync

# Test the installation
uv run python test_e2e.py --env production
```

### Option 2: Using pip

```bash
# Clone and set up
git clone https://github.com/jiweiqi/heatpump-mcp-server.git
cd heatpump-mcp-server
pip install -r requirements.txt

# Test the installation
python test_e2e.py --env production
```

## ⚙️ Configuration

### Claude Desktop Setup

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

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

### Environment Configuration

The server automatically uses the production WattSavy API. For local development:

```bash
# Copy example configuration
cp .env.example .env

# For local development (optional)
# Edit .env to point to your local backend
HEATPUMP_API_URL=http://localhost:8000
```

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

## 🔧 Development

### Project Structure

```
heatpump-mcp-server/
├── server.py              # Main MCP server implementation
├── test_e2e.py            # Comprehensive test suite
├── test_server.py          # Basic functionality tests
├── run_tests.sh           # Test runner script
├── requirements.txt        # Dependencies
├── pyproject.toml         # Python project config
├── .env.example           # Environment template
├── .env.production        # Production environment
├── .env.local             # Local development environment
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

### v0.2.0 (Current)
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