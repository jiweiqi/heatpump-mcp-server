# Use Python 3.11 slim image for efficiency
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml and README first for better caching
COPY pyproject.toml README.md ./

# Install Python dependencies using uv
RUN pip install --no-cache-dir uv && \
    uv pip install --system .

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
CMD ["python", "src/server_http.py"]