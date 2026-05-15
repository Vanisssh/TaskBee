from __future__ import annotations

from decimal import Decimal

from models import Specialist, User, db
from schemas import AuthRegisterSchema, validate_load


def test_auth_register_schema_role_validation():
    payload, errors = validate_load(
        AuthRegisterSchema(),
        {"name": "Test", "email": "test@mail.com", "password": "secret123", "role": "invalid"},
    )
    assert payload is None
    assert errors is not None
    assert "role" in errors


def test_create_executor_with_specialist_profile(app):
    with app.app_context():
        user = User(name="Exec", email="exec@mail.com", password_hash="hash", role=User.ROLE_EXECUTOR)
        db.session.add(user)
        db.session.flush()
        spec = Specialist(user_id=user.id, bio="Executor profile", rating_avg=Decimal("0.00"))
        db.session.add(spec)
        db.session.commit()

        saved = User.query.filter_by(email="exec@mail.com").first()
        assert saved is not None
        assert saved.role == User.ROLE_EXECUTOR
        assert saved.specialist is not None
