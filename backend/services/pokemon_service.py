import requests
import threading
import time

_cache: list[dict] = []
_cache_lock = threading.Lock()
_loading = False
_load_progress = {"loaded": 0, "total": 151, "done": False, "error": None}

POKEAPI_BASE = "https://pokeapi.co/api/v2/pokemon"


def _fetch_single(poke_id: int) -> dict:
    try:
        res = requests.get(f"{POKEAPI_BASE}/{poke_id}", timeout=10)
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
        return {"id": poke_id, "name": f"pokemon-{poke_id}", "img": ""}


def _load_all_pokemon():
    global _loading
    _load_progress["loaded"] = 0
    _load_progress["done"] = False
    _load_progress["error"] = None

    result = []
    for i in range(1, 152):
        pokemon = _fetch_single(i)
        result.append(pokemon)
        _load_progress["loaded"] = i
        time.sleep(0.02)  # light throttle to be kind to PokeAPI

    with _cache_lock:
        _cache.clear()
        _cache.extend(result)

    _load_progress["done"] = True
    _loading = False


def start_loading():
    global _loading
    if not _loading and not _load_progress["done"]:
        _loading = True
        t = threading.Thread(target=_load_all_pokemon, daemon=True)
        t.start()


def get_progress() -> dict:
    return {
        "loaded": _load_progress["loaded"],
        "total": _load_progress["total"],
        "done": _load_progress["done"],
        "error": _load_progress["error"],
    }


def get_all() -> list[dict]:
    with _cache_lock:
        return list(_cache)


def is_ready() -> bool:
    return _load_progress["done"] and len(_cache) == 151
