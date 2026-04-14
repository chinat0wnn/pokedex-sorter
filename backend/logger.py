"""
Centralized logging module for the Pokédex Sorter application.

Provides:
  - JSON-formatted file logs (machine-readable)
  - Colored console output (developer-friendly)
  - Separate log files per concern (app, sorting, errors)
  - get_logger(name) factory for module-level loggers

Usage:
    from logger import setup_logging, get_logger
    setup_logging(app)            # call once in app.py
    logger = get_logger("sorting") # in any module
"""
import json
import logging
import os
import sys
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler

from config import LOG_DIR, LOG_LEVEL, LOG_MAX_BYTES, LOG_BACKUP_COUNT, LOG_DATE_FORMAT
from config import LOG_FILE_APP, LOG_FILE_SORTING, LOG_FILE_ERROR


# ─── ANSI Color Codes ────────────────────────────────────────────────
class _Colors:
    RESET   = "\033[0m"
    GREY    = "\033[38;5;245m"
    BLUE    = "\033[38;5;75m"
    GREEN   = "\033[38;5;114m"
    YELLOW  = "\033[38;5;221m"
    RED     = "\033[38;5;203m"
    BOLD    = "\033[1m"
    CYAN    = "\033[38;5;87m"

_LEVEL_COLORS = {
    "DEBUG":    _Colors.GREY,
    "INFO":     _Colors.GREEN,
    "WARNING":  _Colors.YELLOW,
    "ERROR":    _Colors.RED,
    "CRITICAL": _Colors.RED + _Colors.BOLD,
}

# Check if the terminal supports Unicode
_SUPPORTS_UNICODE = sys.stdout and hasattr(sys.stdout, "encoding") and sys.stdout.encoding and "utf" in sys.stdout.encoding.lower()

_LEVEL_ICONS_UNICODE = {
    "DEBUG":    "●",
    "INFO":     "●",
    "WARNING":  "▲",
    "ERROR":    "✖",
    "CRITICAL": "✖",
}

_LEVEL_ICONS_ASCII = {
    "DEBUG":    "*",
    "INFO":     "*",
    "WARNING":  "!",
    "ERROR":    "x",
    "CRITICAL": "X",
}

_LEVEL_ICONS = _LEVEL_ICONS_UNICODE if _SUPPORTS_UNICODE else _LEVEL_ICONS_ASCII


# ─── JSON Formatter (for file logs) ──────────────────────────────────
class JsonFormatter(logging.Formatter):
    """Formats each log record as a single JSON line."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # Merge any extra structured data passed via `extra={"data": {...}}`
        if hasattr(record, "data") and isinstance(record.data, dict):
            log_entry.update(record.data)

        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, ensure_ascii=False)


# ─── Colored Console Formatter ───────────────────────────────────────
class ColoredFormatter(logging.Formatter):
    """Pretty, colored output for the terminal."""

    def format(self, record: logging.LogRecord) -> str:
        C = _Colors
        level = record.levelname
        color = _LEVEL_COLORS.get(level, C.RESET)
        icon  = _LEVEL_ICONS.get(level, "●")

        ts = datetime.fromtimestamp(record.created).strftime(LOG_DATE_FORMAT)

        # Request ID (if present)
        req_id = getattr(record, "request_id", None)
        req_tag = f" {C.CYAN}[req:{req_id}]{C.RESET}" if req_id else ""

        # Level badge
        level_badge = f"{color}{C.BOLD}{icon} {level:<8}{C.RESET}"

        # Logger name
        name_tag = f"{C.BLUE}{record.name}{C.RESET}"

        # Message
        msg = record.getMessage()

        line = f"{C.GREY}{ts}{C.RESET} {level_badge}{req_tag} {name_tag} → {msg}"

        if record.exc_info and record.exc_info[0] is not None:
            line += "\n" + self.formatException(record.exc_info)

        return line


# ─── Setup Functions ─────────────────────────────────────────────────
def _create_file_handler(
    filename: str,
    level: int = logging.INFO,
    formatter: logging.Formatter | None = None,
) -> RotatingFileHandler:
    """Create a rotating file handler with JSON formatting."""
    filepath = os.path.join(LOG_DIR, filename)
    handler = RotatingFileHandler(
        filepath,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    handler.setLevel(level)
    handler.setFormatter(formatter or JsonFormatter())
    return handler


def setup_logging(app=None):
    """
    Initialize the logging system. Call once at application startup.

    Args:
        app: Flask application instance (optional). If provided, the Flask
             logger is also wired into the system.
    """
    os.makedirs(LOG_DIR, exist_ok=True)

    # ── Root logger ──────────────────────────────────────────────
    root = logging.getLogger()
    root.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    # Avoid duplicate handlers on reload
    root.handlers.clear()

    json_fmt = JsonFormatter()

    # 1) app.log — everything INFO+
    root.addHandler(_create_file_handler(LOG_FILE_APP, logging.INFO, json_fmt))

    # 2) error.log — WARNING+ only
    root.addHandler(_create_file_handler(LOG_FILE_ERROR, logging.WARNING, json_fmt))

    # 3) Console — colored output (force UTF-8 on Windows)
    try:
        import io
        console_stream = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    except (AttributeError, TypeError):
        console_stream = sys.stdout
    console = logging.StreamHandler(console_stream)
    console.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    console.setFormatter(ColoredFormatter())
    root.addHandler(console)

    # ── Sorting-specific logger ──────────────────────────────────
    sorting_logger = logging.getLogger("sorting")
    sorting_logger.addHandler(
        _create_file_handler(LOG_FILE_SORTING, logging.DEBUG, json_fmt)
    )

    # ── Wire Flask logger ────────────────────────────────────────
    if app is not None:
        app.logger.handlers.clear()
        # Flask logger inherits from root, so it already gets all handlers.
        # We just ensure the level is correct.
        app.logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    # ── Quiet noisy third-party loggers ──────────────────────────
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    root.info("Logging system initialized", extra={
        "data": {
            "event": "logging_init",
            "log_level": LOG_LEVEL,
            "log_dir": LOG_DIR,
            "files": [LOG_FILE_APP, LOG_FILE_SORTING, LOG_FILE_ERROR],
        }
    })


def get_logger(name: str) -> logging.Logger:
    """
    Get a named logger. Use this in every module instead of print().

    Examples:
        logger = get_logger("sorting")
        logger = get_logger("pokemon")
        logger = get_logger("app")
    """
    return logging.getLogger(name)
