"""
Centralized application configuration.
All magic values and settings live here.
"""
import os

# ─── Paths ────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")

# ─── Logging ──────────────────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", 5 * 1024 * 1024))  # 5 MB
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 5))
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Log file names
LOG_FILE_APP = "app.log"
LOG_FILE_SORTING = "sorting.log"
LOG_FILE_ERROR = "error.log"

# ─── Flask ────────────────────────────────────────────────────────────
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "true").lower() == "true"

# ─── PokéAPI ─────────────────────────────────────────────────────────
POKEAPI_BASE = os.getenv("POKEAPI_BASE", "https://pokeapi.co/api/v2/pokemon")
POKEAPI_TIMEOUT = int(os.getenv("POKEAPI_TIMEOUT", 10))
POKEAPI_TOTAL = 151
POKEAPI_THROTTLE = 0.02  # seconds between requests
