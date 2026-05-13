"""
Flask middleware for request logging and Request ID tracking.

Adds a unique Request ID to every HTTP request and logs entry/exit
with method, path, status code, and duration.
"""
import time
import uuid
from collections import defaultdict

from flask import Flask, g, request, jsonify
from logger import get_logger
from config import RATE_LIMIT_PER_MINUTE

logger = get_logger("http")

_requests: dict[str, list[float]] = defaultdict(list)


def register_middleware(app: Flask):
    """Register before/after request hooks on the Flask app."""

    @app.before_request
    def _before():
        ip = request.remote_addr or "unknown"
        now = time.time()
        window = 60.0

        # Remove requests fora da janela
        _requests[ip] = [t for t in _requests[ip] if now - t < window]

        if len(_requests[ip]) >= RATE_LIMIT_PER_MINUTE:
            return jsonify({"detail": "Muitas requisições. Tente novamente em 1 minuto."}), 429

        _requests[ip].append(now)

        g.request_id = uuid.uuid4().hex[:8]
        g.request_start = time.perf_counter()
        logger.info(
            f"► {request.method} {request.path}",
            extra={
                "request_id": g.request_id,
                "data": {
                    "event": "request_start",
                    "request_id": g.request_id,
                    "method": request.method,
                    "path": request.path,
                    "remote_addr": request.remote_addr,
                },
            },
        )

    @app.after_request
    def _after(response):
        duration_ms = (time.perf_counter() - g.request_start) * 1000
        logger.info(
            f"◄ {response.status_code} {request.method} {request.path} ({duration_ms:.0f}ms)",
            extra={
                "request_id": g.request_id,
                "data": {
                    "event": "request_end",
                    "request_id": g.request_id,
                    "method": request.method,
                    "path": request.path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration_ms, 2),
                },
            },
        )
        # Inject Request ID into response headers
        response.headers["X-Request-ID"] = g.request_id
        return response
