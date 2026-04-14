from flask import Blueprint, jsonify
from services.pokemon_service import (
    start_loading,
    get_progress,
    get_all,
    is_ready,
)

pokemon_bp = Blueprint("pokemon", __name__)


@pokemon_bp.route("/load", methods=["POST"])
def load():
    """Trigger background loading of all 151 Pokémon from PokeAPI."""
    start_loading()
    return jsonify({"message": "Loading started"}), 202


@pokemon_bp.route("/progress", methods=["GET"])
def progress():
    """Poll loading progress."""
    return jsonify(get_progress())


@pokemon_bp.route("/", methods=["GET"])
def list_pokemon():
    """Return all cached Pokémon. 404 if not ready yet."""
    if not is_ready():
        return jsonify({"error": "Pokémon not loaded yet. POST /api/pokemon/load first."}), 404
    return jsonify(get_all())
