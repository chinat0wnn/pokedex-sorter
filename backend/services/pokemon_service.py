"""
Service layer for fetching and caching Pokémon data from PokeAPI.
Runs the fetch in a background thread with progress tracking.
"""
import requests
import threading
import time

from config import POKEAPI_BASE, POKEAPI_TIMEOUT, POKEAPI_TOTAL, POKEAPI_THROTTLE
from logger import get_logger

logger = get_logger("pokemon")

_cache: list[dict] = []
_cache_lock = threading.Lock()
_loading = False
_load_progress = {"loaded": 0, "total": POKEAPI_TOTAL, "done": False, "error": None}


def _fetch_single(poke_id: int) -> dict:
    """Fetch a single Pokémon by ID from PokéAPI."""
    try:
        res = requests.get(f"{POKEAPI_BASE}/{poke_id}", timeout=POKEAPI_TIMEOUT)
        res.raise_for_status()
        data = res.json()
        sprite = (
            data["sprites"]["front_default"]
            or data["sprites"]["other"]["official-artwork"]["front_default"]
            or ""
        )
        return {
            "id": data["id"],
            "name": data["name"],
            "img": sprite,
        }
    except Exception as e:
        logger.warning(
            f"Failed to fetch Pokémon #{poke_id}: {e}",
            extra={
                "data": {
                    "event":   "pokemon_fetch_error",
                    "poke_id": poke_id,
                    "error":   str(e),
                },
            },
        )
        return {"id": poke_id, "name": f"pokemon-{poke_id}", "img": ""}


def _load_all_pokemon():
    """Background task: fetch all 151 Pokémon sequentially."""
    global _loading

    _load_progress["loaded"] = 0
    _load_progress["done"] = False
    _load_progress["error"] = None

    logger.info(f"Starting Pokémon load ({POKEAPI_TOTAL} total)", extra={
        "data": {"event": "pokemon_load_start", "total": POKEAPI_TOTAL},
    })

    t_start = time.perf_counter()
    result = []

    for i in range(1, POKEAPI_TOTAL + 1):
        pokemon = _fetch_single(i)
        result.append(pokemon)
        _load_progress["loaded"] = i

        # Log progress every 25 Pokémon
        if i % 25 == 0 or i == POKEAPI_TOTAL:
            elapsed = time.perf_counter() - t_start
            logger.info(
                f"Load progress: {i}/{POKEAPI_TOTAL} ({i / POKEAPI_TOTAL * 100:.0f}%) — {elapsed:.1f}s elapsed",
                extra={
                    "data": {
                        "event":      "pokemon_load_progress",
                        "loaded":     i,
                        "total":      POKEAPI_TOTAL,
                        "elapsed_s":  round(elapsed, 1),
                    },
                },
            )

        time.sleep(POKEAPI_THROTTLE)  # be kind to PokéAPI

    with _cache_lock:
        _cache.clear()
        _cache.extend(result)

    _load_progress["done"] = True
    _loading = False

    total_time = time.perf_counter() - t_start
    logger.info(
        f"Pokémon load complete — {len(result)} loaded in {total_time:.1f}s",
        extra={
            "data": {
                "event":       "pokemon_load_complete",
                "count":       len(result),
                "duration_s":  round(total_time, 1),
            },
        },
    )


def start_loading():
    """Start the background loading thread (if not already running)."""
    global _loading
    if not _loading and not _load_progress["done"]:
        _loading = True
        logger.info("Spawning background loader thread", extra={
            "data": {"event": "pokemon_thread_start"},
        })
        t = threading.Thread(target=_load_all_pokemon, daemon=True)
        t.start()


def get_progress() -> dict:
    return {
        "loaded": _load_progress["loaded"],
        "total":  _load_progress["total"],
        "done":   _load_progress["done"],
        "error":  _load_progress["error"],
    }


def get_all() -> list[dict]:
    with _cache_lock:
        return list(_cache)


def is_ready() -> bool:
    return _load_progress["done"] and len(_cache) == POKEAPI_TOTAL
