# HeatPumpHQ MCP Server

An MCP (Model Context Protocol) server that provides access to HeatPumpHQ's heat pump calculation APIs. This server exposes tools for quick sizing, bill estimation, cold climate checking, and project cost estimation through the Model Context Protocol.

## Features

### Available Tools

1. **quick_sizer** - Calculate required BTU capacity for heat pumps
   - Input: ZIP code, square footage, build year
   - Output: Heating/cooling loads, climate zone, recommendations

2. **bill_estimator** - Estimate electricity costs and ROI
   - Input: ZIP code, heating/cooling loads, current system, home size
   - Output: Cost analysis, payback period, savings estimates

3. **cold_climate_check** - Verify heat pump performance in cold climates
   - Input: ZIP code, system capacity, backup heating type
   - Output: Climate analysis, design temperature data, performance metrics

4. **project_cost_estimator** - Calculate installation costs
   - Input: ZIP code, home size, building age, system type, complexity, contractor experience
   - Output: Cost breakdown, rebate information, financing options

### Available Resources

- `heatpump://api-status` - Check HeatPumpHQ API health status
- `heatpump://endpoints` - List all available tools and their descriptions

## Installation

### Prerequisites
- Python 3.8+
- uv (recommended) or pip
- Running HeatPumpHQ backend API (local or remote)

### Setup

1. **Install dependencies using uv (recommended):**
   ```bash
   cd mcp-server
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -r requirements.txt
   ```

2. **Or install using pip:**
   ```bash
   cd mcp-server
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env to set your HeatPumpHQ API URL
   ```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# HeatPump API Configuration
HEATPUMP_API_URL=http://localhost:8000
# For production, use: https://your-api-domain.com

# Optional: API authentication if your backend requires it
# API_KEY=your_api_key_here
```

## Usage

### Development Mode

Run the MCP server in development mode:

```bash
cd mcp-server
uv run mcp dev server.py
```

### Installation in Claude Desktop

To install this MCP server in Claude Desktop:

```bash
cd mcp-server
uv run mcp install server.py
```

### Manual Configuration

Add this to your Claude Desktop configuration file:

```json
{
  "mcpServers": {
    "heatpump": {
      "command": "python",
      "args": ["/path/to/HeatPumpHQ/mcp-server/server.py"],
      "env": {
        "HEATPUMP_API_URL": "http://localhost:8000"
      }
    }
  }
}
```

## Example Usage

Once connected to an MCP client (like Claude Desktop), you can use these tools:

### Quick Sizing Example
```
Can you help me size a heat pump for my 2000 sq ft home built in 2010 in ZIP code 02101?
```

The MCP server will call the `quick_sizer` tool with:
- zip_code: "02101"
- square_feet: 2000
- build_year: 2010

### Bill Estimation Example
```
What would be the cost savings of switching from a gas furnace to a heat pump for a 1500 sq ft home in Denver (80202) with 40,000 BTU heating load and 30,000 BTU cooling load?
```

The MCP server will call the `bill_estimator` tool with the provided parameters.

## API Integration

This MCP server integrates with the HeatPumpHQ backend API endpoints:

- `POST /api/quick-sizer/calculate`
- `POST /api/bill-estimator/calculate`
- `POST /api/cold-climate/check`
- `POST /api/project-cost/calculate`
- `GET /health` (for status checks)

## Development

### Project Structure

```
mcp-server/
├── server.py           # Main MCP server implementation
├── requirements.txt    # Python dependencies
├── pyproject.toml     # Project configuration
├── .env.example       # Environment variables template
└── README.md          # This file
```

### Testing

Test the server locally:

```bash
# Start the HeatPumpHQ backend (in another terminal)
cd ../backend
uvicorn main:app --reload --port 8000

# Test the MCP server
cd mcp-server
python server.py
```

## Error Handling

The MCP server includes comprehensive error handling:

- **API Connection Errors**: Gracefully handles backend API unavailability
- **Input Validation**: Uses Pydantic models to validate all inputs
- **Timeout Handling**: 30-second timeout for API requests
- **Structured Errors**: Returns meaningful error messages to MCP clients

## Contributing

1. Follow the existing code style and patterns
2. Add comprehensive docstrings for new tools
3. Include input validation using Pydantic models
4. Test with both local and remote HeatPumpHQ API instances
5. Update this README for any new features

## License

This MCP server follows the same license as the main HeatPumpHQ project.