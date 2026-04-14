import logging
import os
import psutil
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_cors import CORS
from routes.pokemon import pokemon_bp
from routes.sort import sort_bp

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# --- Setup Logging ---
if not os.path.exists('logs'):
    os.makedirs('logs')
handler = RotatingFileHandler('logs/sorting_activity.log', maxBytes=2000000, backupCount=5)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

app.register_blueprint(pokemon_bp, url_prefix="/api/pokemon")
app.register_blueprint(sort_bp,    url_prefix="/api/sort")

if __name__ == "__main__":
    app.logger.info(f"Starting Pokédex Sorter Web Application - Initial Memory Usage: {psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024:.2f} MB")
    app.run(debug=True, host="0.0.0.0", port=5000)
