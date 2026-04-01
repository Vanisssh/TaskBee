
from decimal import Decimal

from flask import request
from flask_restx import Namespace, Resource, fields
from api.serializers import specialist_to_dict
from models import Order, Service, Specialist, User, db
from schemas import SpecialistCreateSchema, SpecialistUpdateSchema, validate_load

ns = Namespace("specialists", description="Исполнители (специалисты), поиск по рейтингу и категории")

spec_create = ns.model(
    "SpecialistCreate",
    {
        "user_id": fields.Integer(required=True),
        "bio": fields.String(),
        "rating_avg": fields.Float(default=0, description="0–5, денормализованный рейтинг"),
    },
)


@ns.route("")
class SpecialistList(Resource):
    def get(self):
        rows = Specialist.query.order_by(Specialist.rating_avg.desc()).all()
        return {"data": [specialist_to_dict(s) for s in rows]}

    @ns.expect(spec_create)
    @ns.response(201, "Created")
    def post(self):
        payload, errors = validate_load(SpecialistCreateSchema(), request.get_json(force=True, silent=True))
        if errors:
            return {"error": "validation", "details": errors}, 422
        if Specialist.query.filter_by(user_id=payload["user_id"]).first():
            return {"error": "validation", "details": {"user_id": ["профиль исполнителя уже есть"]}}, 422
        if not User.query.get(payload["user_id"]):
            return {"error": "validation", "details": {"user_id": ["пользователь не найден"]}}, 422
        ra = payload.get("rating_avg")
        if ra is not None:
            ra = Decimal(str(ra))
        else:
            ra = Decimal("0")
        s = Specialist(user_id=payload["user_id"], bio=payload.get("bio"), rating_avg=ra)
        db.session.add(s)
        db.session.commit()
        s = Specialist.query.get(s.id)
        return {"data": specialist_to_dict(s)}, 201


@ns.route("/<int:sid>")
@ns.param("sid", "ID исполнителя")
class SpecialistItem(Resource):
    def get(self, sid: int):
        s = Specialist.query.get(sid)
        if not s:
            return {"error": "not_found", "message": "Исполнитель не найден"}, 404
        return {"data": specialist_to_dict(s)}

    def put(self, sid: int):
        s = Specialist.query.get(sid)
        if not s:
            return {"error": "not_found", "message": "Исполнитель не найден"}, 404
        payload, errors = validate_load(SpecialistUpdateSchema(), request.get_json(force=True, silent=True), partial=True)
        if errors:
            return {"error": "validation", "details": errors}, 422
        if "bio" in payload:
            s.bio = payload["bio"]
        if "rating_avg" in payload and payload["rating_avg"] is not None:
            s.rating_avg = Decimal(str(payload["rating_avg"]))
        db.session.commit()
        return {"data": specialist_to_dict(s)}

    patch = put

    def delete(self, sid: int):
        s = Specialist.query.get(sid)
        if not s:
            return {"error": "not_found", "message": "Исполнитель не найден"}, 404
        db.session.delete(s)
        db.session.commit()
        return "", 204


@ns.route("/search")
class SpecialistSearch(Resource):
    @ns.doc(
        "search_specialists",
        description="Поиск исполнителей для быстрого подбора: мин. рейтинг, опционально категория услуг",
        params={
            "min_rating": "Минимальный средний рейтинг (0–5)",
            "category_id": "Только те, кто работал по услугам этой категории",
            "limit": "Макс. число записей (по умолчанию 20, макс. 100)",
        },
    )
    def get(self):
        min_rating = request.args.get("min_rating", type=float)
        category_id = request.args.get("category_id", type=int)
        limit = min(request.args.get("limit", default=20, type=int) or 20, 100)

        q = Specialist.query.join(User).order_by(Specialist.rating_avg.desc())
        if min_rating is not None:
            if not 0 <= min_rating <= 5:
                return {"error": "validation", "details": {"min_rating": ["должен быть от 0 до 5"]}}, 422
            q = q.filter(Specialist.rating_avg >= min_rating)

        if category_id:
            subq = (
                db.session.query(Order.specialist_id)
                .join(Service, Order.service_id == Service.id)
                .filter(
                    Service.service_category_id == category_id,
                    Order.specialist_id.isnot(None),
                )
                .distinct()
            )
            q = q.filter(Specialist.id.in_(subq))

        rows = q.limit(limit).all()
        return {
            "data": [specialist_to_dict(s) for s in rows],
            "meta": {"count": len(rows), "limit": limit},
        }
