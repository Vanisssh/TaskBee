"""Flask-приложение TaskBee (ИС быстрого поиска и заказа профессиональных услуг)."""

import os

import redis
from flask import Flask
from sqlalchemy import text

from config import database_uri
from models import db
from routes import bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    app.register_blueprint(bp, url_prefix="/api/v1")

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


# Gunicorn: gunicorn --bind 0.0.0.0:5000 app:app
app = create_app()
