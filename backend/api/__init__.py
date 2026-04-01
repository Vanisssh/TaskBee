"""REST API: Flask-RESTx + Blueprint (ЛР3)."""

from __future__ import annotations

from flask import Blueprint
from flask_restx import Api


def create_api_blueprint() -> tuple[Blueprint, Api]:
    bp = Blueprint("rest_api", __name__, url_prefix="/api")
    api = Api(
        bp,
        version="1.0",
        title="TaskBee API",
        description=(
            "RESTful API платформы быстрого поиска и заказа профессиональных услуг. "
            "Docker, PostgreSQL, Redis, валидация Marshmallow."
        ),
        doc="/docs/",
        doc_swagger_ui_title="TaskBee — Swagger UI",
    )

    from api.v1 import register_namespaces

    register_namespaces(api)

    return bp, api
