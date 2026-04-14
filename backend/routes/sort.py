"""
Routes for sorting algorithms.
Provides endpoints to run individual algorithms and compare all of them.
"""
import os
import random
import time

import psutil
from flask import Blueprint, jsonify, request, g

from algorithms.sorting import run_algorithm, ALGORITHMS, COMPLEXITIES
from logger import get_logger
from services.pokemon_service import get_all, is_ready

sort_bp = Blueprint("sort", __name__)
logger = get_logger("sorting")


def _get_request_id() -> str:
    """Safely retrieve the current request ID."""
    return getattr(g, "request_id", "no-req")


def _get_process_metrics() -> tuple[float, float]:
    """Returns (cpu_percent, memory_mb) of the current process."""
    process = psutil.Process(os.getpid())
    mem_mb = process.memory_info().rss / 1024 / 1024
    _ = process.cpu_percent(interval=None)  # prime the counter
    cpu = process.cpu_percent(interval=0.01)
    return cpu, mem_mb


def _get_shuffled_array() -> list[dict]:
    arr = get_all()
    random.shuffle(arr)
    return arr


@sort_bp.route("/algorithms", methods=["GET"])
def list_algorithms():
    """List available algorithms with complexity info."""
    logger.debug("Listing available algorithms", extra={
        "request_id": _get_request_id(),
        "data": {"event": "list_algorithms"},
    })
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
    req_id = _get_request_id()

    if algorithm not in ALGORITHMS:
        logger.warning(f"Unknown algorithm requested: '{algorithm}'", extra={
            "request_id": req_id,
            "data": {"event": "sort_invalid_algorithm", "algorithm": algorithm},
        })
        return jsonify({
            "error": f"Unknown algorithm '{algorithm}'.",
            "valid": list(ALGORITHMS.keys()),
        }), 400

    body = request.get_json(silent=True) or {}
    arr = body.get("array")

    if arr is None:
        if not is_ready():
            logger.warning("Sort requested but Pokémon not loaded", extra={
                "request_id": req_id,
                "data": {"event": "sort_no_data", "algorithm": algorithm},
            })
            return jsonify({
                "error": "Pokémon not loaded. POST /api/pokemon/load first."
            }), 400
        arr = _get_shuffled_array()

    if not isinstance(arr, list) or len(arr) == 0:
        return jsonify({"error": "'array' must be a non-empty list."}), 400

    try:
        pre_cpu, pre_mem = _get_process_metrics()
        t_start = time.perf_counter()

        result = run_algorithm(algorithm, arr)

        duration_ms = (time.perf_counter() - t_start) * 1000
        post_cpu, post_mem = _get_process_metrics()

        stats = result.get("stats", {})

        logger.info(
            f"SORT COMPLETE | {algorithm.upper()} | "
            f"{len(arr)} items | "
            f"{stats.get('compares', 0)} compares | "
            f"{stats.get('swaps', 0)} swaps | "
            f"{stats.get('writes', 0)} writes | "
            f"{duration_ms:.1f}ms",
            extra={
                "request_id": req_id,
                "data": {
                    "event":       "sort_complete",
                    "algorithm":   algorithm,
                    "items":       len(arr),
                    "compares":    stats.get("compares", 0),
                    "swaps":       stats.get("swaps", 0),
                    "writes":      stats.get("writes", 0),
                    "total_ops":   stats.get("total", 0),
                    "total_steps": result.get("total_steps", 0),
                    "duration_ms": round(duration_ms, 2),
                    "cpu_pre":     pre_cpu,
                    "cpu_post":    post_cpu,
                    "mem_pre_mb":  round(pre_mem, 2),
                    "mem_post_mb": round(post_mem, 2),
                },
            },
        )
    except Exception as exc:
        logger.error(
            f"SORT FAILED | {algorithm} | {exc}",
            exc_info=True,
            extra={
                "request_id": req_id,
                "data": {
                    "event":     "sort_error",
                    "algorithm": algorithm,
                    "error":     str(exc),
                },
            },
        )
        return jsonify({"error": str(exc)}), 500

    return jsonify(result)


@sort_bp.route("/compare", methods=["POST"])
def compare_algorithms():
    """
    Run ALL algorithms on the SAME shuffled array and return stats for comparison.

    Body (JSON, optional):
      { "array": [...] }
    """
    req_id = _get_request_id()

    body = request.get_json(silent=True) or {}
    arr = body.get("array")

    if arr is None:
        if not is_ready():
            logger.warning("Compare requested but Pokémon not loaded", extra={
                "request_id": req_id,
                "data": {"event": "compare_no_data"},
            })
            return jsonify({
                "error": "Pokémon not loaded. POST /api/pokemon/load first."
            }), 400
        arr = _get_shuffled_array()

    if not isinstance(arr, list) or len(arr) == 0:
        return jsonify({"error": "'array' must be a non-empty list."}), 400

    results = {}
    pre_cpu, pre_mem = _get_process_metrics()
    t_start = time.perf_counter()

    for name in ALGORITHMS:
        r = run_algorithm(name, list(arr))  # copy so each algo gets same input
        results[name] = {
            "complexity":  r["complexity"],
            "stats":       r["stats"],
            "total_steps": r["total_steps"],
        }

    duration_ms = (time.perf_counter() - t_start) * 1000
    post_cpu, post_mem = _get_process_metrics()

    logger.info(
        f"COMPARE COMPLETE | {len(ALGORITHMS)} algorithms | "
        f"{len(arr)} items | {duration_ms:.1f}ms",
        extra={
            "request_id": req_id,
            "data": {
                "event":        "compare_complete",
                "algorithms":   list(ALGORITHMS.keys()),
                "items":        len(arr),
                "duration_ms":  round(duration_ms, 2),
                "cpu_pre":      pre_cpu,
                "cpu_post":     post_cpu,
                "mem_pre_mb":   round(pre_mem, 2),
                "mem_post_mb":  round(post_mem, 2),
            },
        },
    )

    return jsonify({
        "n": len(arr),
        "results": results,
    })
