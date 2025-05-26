"""
Configuration settings for the Mini Data Transformer.
"""

import secrets
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = BASE_DIR / "config"

# API settings
API_HOST = "0.0.0.0"
API_PORT = 8000
API_TITLE = "Mini Data Transformer"
API_DESCRIPTION = "A lightweight, pluggable data transformation system"
API_VERSION = "1.0.0"  # Application version
API_VERSIONS = {
    "v1": "1.0.0",  # API version
}
CURRENT_API_VERSION = "v1"  # Current active API version

# Authentication settings
SECRET_KEY = secrets.token_urlsafe(32)  # Generate a random secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Logging settings
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# File settings
ALLOWED_EXTENSIONS = {".csv"}

# In-memory user storage
users_db = {}
