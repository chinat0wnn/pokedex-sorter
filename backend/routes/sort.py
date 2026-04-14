import random
import os
import psutil
from flask import Blueprint, jsonify, request, current_app
from algorithms.sorting import run_algorithm, ALGORITHMS, COMPLEXITIES
from services.pokemon_service import get_all, is_ready

sort_bp = Blueprint("sort", __name__)


def _get_process_metrics():
    """Returns memory in MB and CPU percentage of the current process."""
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    cpu_percent = process.cpu_percent(interval=None)  # Call first to clear
    cpu_percent = process.cpu_percent(interval=0.01)  # Small interval to get actual reading
    mem_mb = mem_info.rss / 1024 / 1024
    return cpu_percent, mem_mb


def _get_shuffled_array() -> list[dict]:
    arr = get_all()
    random.shuffle(arr)
    return arr


@sort_bp.route("/algorithms", methods=["GET"])
def list_algorithms():
    """List available algorithms with complexity info."""
    return jsonify(
        [{"id": k, **v} for k, v in COMPLEXITIES.items()]
    )


@sort_bp.route("/<algorithm>", methods=["POST"])
def sort_with_algorithm(algorithm: str):
    """
    Run a sorting algorithm and return animation steps.

    Body (JSON, optional):
      {
        "array": [ {"id": int, "name": str, "img": str}, ... ]
      }
    If `array` is omitted, uses the cached Pokémon (shuffled).
    """
    if algorithm not in ALGORITHMS:
        return jsonify({
            "error": f"Unknown algorithm '{algorithm}'.",
            "valid": list(ALGORITHMS.keys()),
        }), 400

    body = request.get_json(silent=True) or {}
    arr = body.get("array")

    if arr is None:
        if not is_ready():
            return jsonify({
                "error": "Pokémon not loaded. POST /api/pokemon/load first."
            }), 400
        arr = _get_shuffled_array()

    if not isinstance(arr, list) or len(arr) == 0:
        return jsonify({"error": "'array' must be a non-empty list."}), 400

    try:
        pre_cpu, pre_mem = _get_process_metrics()
        result = run_algorithm(algorithm, arr)
        post_cpu, post_mem = _get_process_metrics()

        stats = result.get("stats", {})
        compares = stats.get("compares", 0)
        swaps = stats.get("swaps", 0)
        writes = stats.get("writes", 0)
        total_steps = result.get("total_steps", 0)

        current_app.logger.info(
            f"Algorithm: {algorithm.upper()} | "
            f"Items: {len(arr)} | "
            f"Compares: {compares} | Swaps: {swaps} | Writes: {writes} | Total Steps: {total_steps} | "
            f"CPU Usage: pre={pre_cpu}%, post={post_cpu}% | "
            f"Memory Usage: pre={pre_mem:.2f}MB, post={post_mem:.2f}MB"
        )
    except Exception as exc:
        current_app.logger.error(f"Error sorting with {algorithm}: {str(exc)}")
        return jsonify({"error": str(exc)}), 500

    return jsonify(result)


@sort_bp.route("/compare", methods=["POST"])
def compare_algorithms():
    """
    Run ALL algorithms on the SAME shuffled array and return stats for comparison.

    Body (JSON, optional):
      { "array": [...] }
    """
    body = request.get_json(silent=True) or {}
    arr = body.get("array")

    if arr is None:
        if not is_ready():
            return jsonify({
                "error": "Pokémon not loaded. POST /api/pokemon/load first."
            }), 400
        arr = _get_shuffled_array()

    if not isinstance(arr, list) or len(arr) == 0:
        return jsonify({"error": "'array' must be a non-empty list."}), 400

    results = {}

    pre_cpu, pre_mem = _get_process_metrics()

    for name in ALGORITHMS:
        r = run_algorithm(name, list(arr))        # copy so each algo gets same input
        results[name] = {
            "complexity": r["complexity"],
            "stats":      r["stats"],
            "total_steps": r["total_steps"],
        }

    post_cpu, post_mem = _get_process_metrics()
    current_app.logger.info(
        f"Algorithm: ALL (Compare) | "
        f"Items: {len(arr)} | "
        f"CPU Usage: pre={pre_cpu}%, post={post_cpu}% | "
        f"Memory Usage: pre={pre_mem:.2f}MB, post={post_mem:.2f}MB"
    )

    return jsonify({
        "n": len(arr),
        "results": results,
    })
