from __future__ import annotations

import os
from datetime import datetime
import logging

from flask import request
from flask_restx import Namespace, Resource, fields
from itsdangerous import URLSafeTimedSerializer, BadSignature, BadTimeSignature, SignatureExpired
from werkzeug.security import check_password_hash, generate_password_hash

from models import Specialist, User, db
from schemas import AuthLoginSchema, AuthRegisterSchema, validate_load

ns = Namespace("auth", description="Регистрация и авторизация по email/паролю")
audit_log = logging.getLogger("taskbee.audit.auth")

register_model = ns.model(
    "AuthRegister",
    {
        "name": fields.String(required=True),
        "email": fields.String(required=True),
        "password": fields.String(required=True),
        "role": fields.String(required=True, enum=["customer", "executor"]),
    },
)

login_model = ns.model(
    "AuthLogin",
    {
        "email": fields.String(required=True),
        "password": fields.String(required=True),
    },
)


def _serializer() -> URLSafeTimedSerializer:
    secret = os.environ.get("AUTH_SECRET_KEY", "taskbee-dev-secret-change-me")
    return URLSafeTimedSerializer(secret_key=secret, salt="taskbee-auth")


def _issue_token(user: User) -> str:
    return _serializer().dumps({"uid": user.id, "email": user.email, "role": user.role})


def _read_bearer() -> str | None:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    return auth.split(" ", 1)[1].strip()


def _current_user() -> User | None:
    token = _read_bearer()
    if not token:
        return None
    max_age = int(os.environ.get("AUTH_TOKEN_TTL_SECONDS", str(60 * 60 * 24 * 7)))
    try:
        payload = _serializer().loads(token, max_age=max_age)
    except (BadSignature, BadTimeSignature, SignatureExpired):
        return None
    uid = payload.get("uid")
    if not uid:
        return None
    return User.query.get(uid)


def _user_dict(u: User) -> dict:
    return {
        "id": u.id,
        "name": u.name,
        "email": u.email,
        "role": u.role,
        "created_at": u.created_at.isoformat() if isinstance(u.created_at, datetime) else None,
    }


@ns.route("/register")
class AuthRegister(Resource):
    @ns.expect(register_model)
    def post(self):
        payload, errors = validate_load(AuthRegisterSchema(), request.get_json(force=True, silent=True))
        if errors:
            return {"error": "validation", "details": errors}, 422

        if User.query.filter_by(email=payload["email"]).first():
            audit_log.warning("register_failed email_exists email=%s", payload["email"])
            return {"error": "validation", "details": {"email": ["email уже занят"]}}, 422

        user = User(
            name=payload["name"].strip(),
            email=payload["email"].strip().lower(),
            password_hash=generate_password_hash(payload["password"]),
            role=payload["role"],
        )
        db.session.add(user)
        db.session.flush()

        if user.role == User.ROLE_EXECUTOR and not Specialist.query.filter_by(user_id=user.id).first():
            db.session.add(Specialist(user_id=user.id, bio="Новый исполнитель", rating_avg=0))

        db.session.commit()
        audit_log.info("register_success uid=%s role=%s email=%s", user.id, user.role, user.email)

        token = _issue_token(user)
        return {"data": {"token": token, "user": _user_dict(user)}}, 201


@ns.route("/login")
class AuthLogin(Resource):
    @ns.expect(login_model)
    def post(self):
        payload, errors = validate_load(AuthLoginSchema(), request.get_json(force=True, silent=True))
        if errors:
            return {"error": "validation", "details": errors}, 422

        email = payload["email"].strip().lower()
        user = User.query.filter_by(email=email).first()
        if not user or not user.password_hash:
            audit_log.warning("login_failed unknown_user email=%s", email)
            return {"error": "unauthorized", "message": "Неверный email или пароль"}, 401

        if not check_password_hash(user.password_hash, payload["password"]):
            audit_log.warning("login_failed bad_password uid=%s email=%s", user.id, email)
            return {"error": "unauthorized", "message": "Неверный email или пароль"}, 401

        token = _issue_token(user)
        audit_log.info("login_success uid=%s role=%s email=%s", user.id, user.role, user.email)
        return {"data": {"token": token, "user": _user_dict(user)}}, 200


@ns.route("/me")
class AuthMe(Resource):
    def get(self):
        user = _current_user()
        if not user:
            return {"error": "unauthorized", "message": "Требуется авторизация"}, 401
        return {"data": _user_dict(user)}, 200
