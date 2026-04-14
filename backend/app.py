"""
Pokédex Sort Visualizer — Flask Application Entry Point.
"""
import os
import psutil
from flask import Flask
from flask_cors import CORS

from config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG
from logger import setup_logging, get_logger
from middleware import register_middleware
from routes.pokemon import pokemon_bp
from routes.sort import sort_bp

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ─── Initialize logging system ───────────────────────────────────────
setup_logging(app)
logger = get_logger("app")

# ─── Register middleware (request ID + request logging) ──────────────
register_middleware(app)

# ─── Register blueprints ─────────────────────────────────────────────
app.register_blueprint(pokemon_bp, url_prefix="/api/pokemon")
app.register_blueprint(sort_bp,    url_prefix="/api/sort")

if __name__ == "__main__":
    process = psutil.Process(os.getpid())
    mem_mb = process.memory_info().rss / 1024 / 1024
    logger.info(
        f"Starting Pokédex Sorter Web Application",
        extra={
            "data": {
                "event":  "app_startup",
                "host":   FLASK_HOST,
                "port":   FLASK_PORT,
                "debug":  FLASK_DEBUG,
                "initial_memory_mb": round(mem_mb, 2),
                "pid":    os.getpid(),
            }
        },
    )
    app.run(debug=FLASK_DEBUG, host=FLASK_HOST, port=FLASK_PORT)
