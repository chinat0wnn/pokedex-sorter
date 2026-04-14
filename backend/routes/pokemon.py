"""
Routes for Pokémon data management.
Handles loading from PokéAPI, progress polling, and listing.
"""
from flask import Blueprint, jsonify, g
from logger import get_logger
from services.pokemon_service import (
    start_loading,
    get_progress,
    get_all,
    is_ready,
)

pokemon_bp = Blueprint("pokemon", __name__)
logger = get_logger("pokemon")


def _get_request_id() -> str:
    """Safely retrieve the current request ID."""
    return getattr(g, "request_id", "no-req")


@pokemon_bp.route("/load", methods=["POST"])
def load():
    """Trigger background loading of all 151 Pokémon from PokeAPI."""
    req_id = _get_request_id()
    logger.info("Pokémon load triggered", extra={
        "request_id": req_id,
        "data": {"event": "pokemon_load_trigger"},
    })
    start_loading()
    return jsonify({"message": "Loading started"}), 202


@pokemon_bp.route("/progress", methods=["GET"])
def progress():
    """Poll loading progress."""
    return jsonify(get_progress())


@pokemon_bp.route("/", methods=["GET"])
def list_pokemon():
    """Return all cached Pokémon. 404 if not ready yet."""
    req_id = _get_request_id()
    if not is_ready():
        logger.debug("Pokémon list requested but not loaded yet", extra={
            "request_id": req_id,
            "data": {"event": "pokemon_not_ready"},
        })
        return jsonify({"error": "Pokémon not loaded yet. POST /api/pokemon/load first."}), 404

    pokemon = get_all()
    logger.debug(f"Returning {len(pokemon)} Pokémon", extra={
        "request_id": req_id,
        "data": {"event": "pokemon_list", "count": len(pokemon)},
    })
    return jsonify(pokemon)
