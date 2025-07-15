# Use Python 3.11 slim image for efficiency
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Add FastAPI and uvicorn for HTTP server
RUN pip install --no-cache-dir fastapi uvicorn

# Copy MCP server code
COPY . .

# Ensure src directory is included
COPY src/ ./src/

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash mcp \
    && chown -R mcp:mcp /app

USER mcp

# Expose HTTP port
EXPOSE 3002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:3002/health || exit 1

# Run HTTP server
CMD ["python", "server_http.py"]