from __future__ import annotations

import os

import pytest

os.environ.setdefault("TEST_DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("ENABLE_SELF_DISCOVERY", "0")
os.environ.setdefault("RATELIMIT_STORAGE_URL", "memory://")

from app import create_app  # noqa: E402
from models import db  # noqa: E402


@pytest.fixture()
def app():
    flask_app = create_app()
    flask_app.config.update(TESTING=True)
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()
