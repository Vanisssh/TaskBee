from flask import request
from flask_restx import Namespace, Resource, fields

from models import User, db
from schemas import UserCreateSchema, validate_load

ns = Namespace("users", description="Пользователи (клиенты)")

user_model = ns.model(
    "UserCreate",
    {
        "name": fields.String(required=True),
        "email": fields.String(required=True),
        "password_hash": fields.String(description="заглушка, без хеширования в учебном проекте"),
    },
)


@ns.route("")
class UserList(Resource):
    @ns.doc("list_users")
    def get(self):
        rows = User.query.order_by(User.id).all()
        return {"data": [{"id": u.id, "name": u.name, "email": u.email} for u in rows]}

    @ns.expect(user_model)
    @ns.response(201, "Created")
    def post(self):
        payload, errors = validate_load(UserCreateSchema(), request.get_json(force=True, silent=True))
        if errors:
            return {"error": "validation", "details": errors}, 422
        if User.query.filter_by(email=payload["email"]).first():
            return {"error": "validation", "details": {"email": ["email уже занят"]}}, 422
        u = User(
            name=payload["name"],
            email=payload["email"],
            password_hash=payload.get("password_hash"),
        )
        db.session.add(u)
        db.session.commit()
        return {"data": {"id": u.id, "name": u.name, "email": u.email}}, 201


@ns.route("/<int:uid>")
@ns.param("uid", "ID пользователя")
class UserItem(Resource):
    def get(self, uid: int):
        u = User.query.get(uid)
        if not u:
            return {"error": "not_found", "message": "Пользователь не найден"}, 404
        return {"data": {"id": u.id, "name": u.name, "email": u.email}}
