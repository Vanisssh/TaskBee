"""Flask-приложение TaskBee (ИС быстрого поиска и заказа профессиональных услуг)."""

from __future__ import annotations

import logging
import os
import time

import redis
import requests
import threading
from flask import Flask, g, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy import text
from werkzeug.exceptions import HTTPException

from api import create_api_blueprint
from config import database_uri
from models import db

logger = logging.getLogger("taskbee")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    origins_raw = os.environ.get("CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
    origins = [o.strip() for o in origins_raw.split(",") if o.strip()]
    CORS(app, origins=origins, supports_credentials=True)

    db.init_app(app)

    storage_uri = os.environ.get("RATELIMIT_STORAGE_URL", "redis://redis:6379/1")
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        storage_uri=storage_uri,
        default_limits=["100 per minute"],
        headers_enabled=True,
    )

    @limiter.request_filter
    def _exempt_light_routes() -> bool:
        p = request.path or ""
        if p in ("/health", "/db-check", "/redis-check"):
            return True
        if p.startswith("/api/docs") or p.startswith("/swaggerui"):
            return True
        return False

    api_bp, _restx_api = create_api_blueprint()
    app.register_blueprint(api_bp)

    @app.before_request
    def _request_timer_start() -> None:
        g._t0 = time.perf_counter()

    @app.after_request
    def _log_request(response):
        elapsed_ms = (time.perf_counter() - getattr(g, "_t0", time.perf_counter())) * 1000
        logger.info("%s %s → %s (%.2f ms)", request.method, request.path, response.status_code, elapsed_ms)
        return response

    @app.errorhandler(400)
    def _bad_request(e):
        msg = getattr(e, "description", None) or str(e)
        return jsonify({"error": "bad_request", "message": msg}), 400

    @app.errorhandler(404)
    def _not_found(e):
        return jsonify({"error": "not_found", "message": "Ресурс не найден"}), 404

    @app.errorhandler(429)
    def _rate_limit(e):
        return jsonify({"error": "rate_limit", "message": "Слишком много запросов с этого IP"}), 429

    @app.errorhandler(HTTPException)
    def _http_exception(e):
        return jsonify({"error": e.name.lower().replace(" ", "_"), "message": e.description}), e.code

    @app.errorhandler(Exception)
    def _unhandled(e):
        logger.exception("Unhandled error: %s", e)
        return jsonify({"error": "internal", "message": "Внутренняя ошибка сервера"}), 500

    @app.route("/health")
    def health():
        return {"status": "ok", "service": "taskbee-backend"}

    @app.route("/db-check")
    def db_check():
        try:
            db.session.execute(text("SELECT 1"))
            return "DB connected!", 200
        except Exception as e:
            return f"Error: {e!s}", 500

    @app.route("/redis-check")
    def redis_check():
        host = os.environ.get("REDIS_HOST", "redis")
        port = int(os.environ.get("REDIS_PORT", "6379"))
        try:
            r = redis.Redis(host=host, port=port, socket_connect_timeout=2)
            r.ping()
            return {"redis": "ok"}, 200
        except Exception as e:
            return {"redis": "error", "detail": str(e)}, 503

    return app


app = create_app()


# Attempt to register this backend with Consul 
def _register_with_consul():
    try:
        import time
        time.sleep(2)
        consul_url = "http://consul:8500/v1/agent/service/register"
        service_id = f"backend-{os.getenv('HOSTNAME', 'backend')}"
        payload = {
            "ID": service_id,
            "Name": "taskbee-backend",
            "Address": "backend",
            "Port": 5000,
            "Tags": ["api", "v1"],
            "Check": {"HTTP": f"http://backend:5000/health", "Interval": "10s"},
        }
        r = requests.put(consul_url, json=payload, timeout=2)
        if r.status_code in (200, 204):
            logger.info("Registered service with Consul: %s", service_id)
        else:
            logger.warning("Consul registration returned %s: %s", r.status_code, r.text)
    except Exception as e:
        logger.info("Consul not available or registration failed: %s", e)

threading.Thread(target=_register_with_consul, daemon=True).start()
