from flask import request
from flask_restx import Namespace, Resource, fields

from api.serializers import review_to_dict
from models import Order, Review, User, db
from schemas import ReviewCreateSchema, ReviewUpdateSchema, validate_load

ns = Namespace("reviews", description="Отзывы на заказы")

rev_create = ns.model(
    "ReviewCreate",
    {
        "order_id": fields.Integer(required=True),
        "user_id": fields.Integer(required=True),
        "rating": fields.Integer(required=True, min=1, max=5),
        "comment": fields.String(),
    },
)


@ns.route("")
class ReviewList(Resource):
    def get(self):
        rows = Review.query.order_by(Review.created_at.desc()).all()
        return {"data": [review_to_dict(r) for r in rows]}

    @ns.expect(rev_create)
    @ns.response(201, "Created")
    def post(self):
        payload, errors = validate_load(ReviewCreateSchema(), request.get_json(force=True, silent=True))
        if errors:
            return {"error": "validation", "details": errors}, 422
        o = Order.query.get(payload["order_id"])
        if not o:
            return {"error": "validation", "details": {"order_id": ["заказ не найден"]}}, 422
        if o.status != Order.STATUS_COMPLETED:
            return {"error": "validation", "message": "Отзыв можно оставить только по выполненному заказу."}, 422
        if not User.query.get(payload["user_id"]):
            return {"error": "validation", "details": {"user_id": ["пользователь не найден"]}}, 422
        r = Review(
            order_id=payload["order_id"],
            user_id=payload["user_id"],
            rating=int(payload["rating"]),
            comment=payload.get("comment"),
        )
        db.session.add(r)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            return {"error": "validation", "message": "отзыв уже существует или ошибка БД"}, 422
        r = Review.query.get(r.id)
        return {"data": review_to_dict(r)}, 201


@ns.route("/<int:rid>")
@ns.param("rid", "ID отзыва")
class ReviewItem(Resource):
    def get(self, rid: int):
        r = Review.query.get(rid)
        if not r:
            return {"error": "not_found", "message": "Отзыв не найден"}, 404
        return {"data": review_to_dict(r)}

    def put(self, rid: int):
        r = Review.query.get(rid)
        if not r:
            return {"error": "not_found", "message": "Отзыв не найден"}, 404
        payload, errors = validate_load(ReviewUpdateSchema(), request.get_json(force=True, silent=True), partial=True)
        if errors:
            return {"error": "validation", "details": errors}, 422
        if "rating" in payload:
            r.rating = int(payload["rating"])
        if "comment" in payload:
            r.comment = payload["comment"]
        db.session.commit()
        return {"data": review_to_dict(r)}

    patch = put

    def delete(self, rid: int):
        r = Review.query.get(rid)
        if not r:
            return {"error": "not_found", "message": "Отзыв не найден"}, 404
        db.session.delete(r)
        db.session.commit()
        return "", 204
