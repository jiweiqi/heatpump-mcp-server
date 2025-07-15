"""
Configuration management for HeatPumpHQ MCP Server
"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables
env_mode = os.getenv('ENV_MODE', 'default')
if env_mode == 'production' and os.path.exists('.env.production'):
    load_dotenv('.env.production')
elif env_mode == 'local' and os.path.exists('.env.local'):
    load_dotenv('.env.local')
elif os.path.exists('.env.local'):
    load_dotenv('.env.local')
else:
    load_dotenv()

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=getattr(logging, log_level))

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", os.getenv("HEATPUMP_API_URL", "https://api.wattsavy.com"))
API_KEY = os.getenv("API_KEY")  # Optional
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))

# Server configuration
SERVER_NAME = "HeatPumpHQ"