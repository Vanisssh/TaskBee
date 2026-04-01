"""REST API v1 — CRUD для категорий, услуг, заказов, отзывов."""

from flask import Blueprint, jsonify, request

from models import Order, Review, Service, ServiceCategory, Specialist, User, db

bp = Blueprint("api", __name__)


def _json_error(message: str, code: int = 400):
    return jsonify({"message": message}), code


@bp.route("/categories", methods=["GET"])
def list_categories():
    rows = ServiceCategory.query.order_by(ServiceCategory.name).all()
    return jsonify({"data": [{"id": c.id, "name": c.name, "slug": c.slug} for c in rows]})


@bp.route("/categories", methods=["POST"])
def create_category():
    data = request.get_json(silent=True) or {}
    if not data.get("name") or not data.get("slug"):
        return _json_error("name и slug обязательны", 422)
    if ServiceCategory.query.filter_by(slug=data["slug"]).first():
        return _json_error("slug уже занят", 422)
    c = ServiceCategory(name=data["name"], slug=data["slug"])
    db.session.add(c)
    db.session.commit()
    return jsonify({"data": {"id": c.id, "name": c.name, "slug": c.slug}}), 201


@bp.route("/categories/<int:cid>", methods=["GET"])
def get_category(cid: int):
    c = ServiceCategory.query.get_or_404(cid)
    services = [{"id": s.id, "name": s.name, "description": s.description} for s in c.services]
    return jsonify({"data": {"id": c.id, "name": c.name, "slug": c.slug, "services": services}})


@bp.route("/categories/<int:cid>", methods=["PUT", "PATCH"])
def update_category(cid: int):
    c = ServiceCategory.query.get_or_404(cid)
    data = request.get_json(silent=True) or {}
    if "name" in data:
        c.name = data["name"]
    if "slug" in data:
        existing = ServiceCategory.query.filter(ServiceCategory.slug == data["slug"], ServiceCategory.id != cid).first()
        if existing:
            return _json_error("slug уже занят", 422)
        c.slug = data["slug"]
    db.session.commit()
    return jsonify({"data": {"id": c.id, "name": c.name, "slug": c.slug}})


@bp.route("/categories/<int:cid>", methods=["DELETE"])
def delete_category(cid: int):
    c = ServiceCategory.query.get_or_404(cid)
    db.session.delete(c)
    db.session.commit()
    return "", 204


@bp.route("/services", methods=["GET"])
def list_services():
    q = Service.query
    cat = request.args.get("category_id", type=int)
    if cat:
        q = q.filter_by(service_category_id=cat)
    rows = q.order_by(Service.name).all()
    out = []
    for s in rows:
        out.append(
            {
                "id": s.id,
                "service_category_id": s.service_category_id,
                "name": s.name,
                "description": s.description,
                "category": {"id": s.category.id, "name": s.category.name, "slug": s.category.slug} if s.category else None,
            }
        )
    return jsonify({"data": out})


@bp.route("/services", methods=["POST"])
def create_service():
    data = request.get_json(silent=True) or {}
    if not data.get("service_category_id") or not data.get("name"):
        return _json_error("service_category_id и name обязательны", 422)
    if not ServiceCategory.query.get(data["service_category_id"]):
        return _json_error("категория не найдена", 422)
    s = Service(
        service_category_id=data["service_category_id"],
        name=data["name"],
        description=data.get("description"),
    )
    db.session.add(s)
    db.session.commit()
    s = Service.query.get(s.id)
    return (
        jsonify(
            {
                "data": {
                    "id": s.id,
                    "service_category_id": s.service_category_id,
                    "name": s.name,
                    "description": s.description,
                    "category": {"id": s.category.id, "name": s.category.name, "slug": s.category.slug},
                }
            }
        ),
        201,
    )


@bp.route("/services/<int:sid>", methods=["GET"])
def get_service(sid: int):
    s = Service.query.get_or_404(sid)
    return jsonify(
        {
            "data": {
                "id": s.id,
                "service_category_id": s.service_category_id,
                "name": s.name,
                "description": s.description,
                "category": {"id": s.category.id, "name": s.category.name, "slug": s.category.slug},
            }
        }
    )


@bp.route("/services/<int:sid>", methods=["PUT", "PATCH"])
def update_service(sid: int):
    s = Service.query.get_or_404(sid)
    data = request.get_json(silent=True) or {}
    if "service_category_id" in data:
        if not ServiceCategory.query.get(data["service_category_id"]):
            return _json_error("категория не найдена", 422)
        s.service_category_id = data["service_category_id"]
    if "name" in data:
        s.name = data["name"]
    if "description" in data:
        s.description = data["description"]
    db.session.commit()
    return jsonify(
        {
            "data": {
                "id": s.id,
                "service_category_id": s.service_category_id,
                "name": s.name,
                "description": s.description,
                "category": {"id": s.category.id, "name": s.category.name, "slug": s.category.slug},
            }
        }
    )


@bp.route("/services/<int:sid>", methods=["DELETE"])
def delete_service(sid: int):
    s = Service.query.get_or_404(sid)
    db.session.delete(s)
    db.session.commit()
    return "", 204


@bp.route("/orders", methods=["GET"])
def list_orders():
    q = Order.query
    st = request.args.get("status")
    if st:
        q = q.filter_by(status=st)
    rows = q.order_by(Order.created_at.desc()).all()
    out = []
    for o in rows:
        out.append(_order_dict(o))
    return jsonify({"data": out})


def _order_dict(o: Order):
    return {
        "id": o.id,
        "client_id": o.client_id,
        "service_id": o.service_id,
        "specialist_id": o.specialist_id,
        "status": o.status,
        "address": o.address,
        "description": o.description,
        "created_at": o.created_at.isoformat() if o.created_at else None,
        "service": {"id": o.service.id, "name": o.service.name} if o.service else None,
        "client": {"id": o.client.id, "name": o.client.name} if o.client else None,
        "specialist": {"id": o.specialist.id, "user_id": o.specialist.user_id, "rating_avg": float(o.specialist.rating_avg)}
        if o.specialist
        else None,
    }


@bp.route("/orders", methods=["POST"])
def create_order():
    data = request.get_json(silent=True) or {}
    if not data.get("client_id") or not data.get("service_id"):
        return _json_error("client_id и service_id обязательны", 422)
    if not User.query.get(data["client_id"]):
        return _json_error("клиент не найден", 422)
    if not Service.query.get(data["service_id"]):
        return _json_error("услуга не найдена", 422)
    o = Order(
        client_id=data["client_id"],
        service_id=data["service_id"],
        status=Order.STATUS_NEW,
        address=data.get("address"),
        description=data.get("description"),
    )
    db.session.add(o)
    db.session.commit()
    o = Order.query.get(o.id)
    return jsonify({"data": _order_dict(o)}), 201


@bp.route("/orders/<int:oid>", methods=["GET"])
def get_order(oid: int):
    o = Order.query.get_or_404(oid)
    return jsonify({"data": _order_dict(o)})


@bp.route("/orders/<int:oid>", methods=["PUT", "PATCH"])
def update_order(oid: int):
    o = Order.query.get_or_404(oid)
    data = request.get_json(silent=True) or {}
    if "specialist_id" in data:
        sid = data["specialist_id"]
        if sid is not None and not Specialist.query.get(sid):
            return _json_error("исполнитель не найден", 422)
        o.specialist_id = sid
    if "status" in data:
        o.status = data["status"]
    if "address" in data:
        o.address = data["address"]
    if "description" in data:
        o.description = data["description"]
    db.session.commit()
    return jsonify({"data": _order_dict(o)})


@bp.route("/orders/<int:oid>", methods=["DELETE"])
def delete_order(oid: int):
    o = Order.query.get_or_404(oid)
    db.session.delete(o)
    db.session.commit()
    return "", 204


@bp.route("/reviews", methods=["GET"])
def list_reviews():
    rows = Review.query.order_by(Review.created_at.desc()).all()
    out = []
    for r in rows:
        out.append(_review_dict(r))
    return jsonify({"data": out})


def _review_dict(r: Review):
    return {
        "id": r.id,
        "order_id": r.order_id,
        "user_id": r.user_id,
        "rating": r.rating,
        "comment": r.comment,
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "order": {"id": r.order.id, "service_id": r.order.service_id} if r.order else None,
        "user": {"id": r.user.id, "name": r.user.name} if r.user else None,
    }


@bp.route("/reviews", methods=["POST"])
def create_review():
    data = request.get_json(silent=True) or {}
    for f in ("order_id", "user_id", "rating"):
        if f not in data:
            return _json_error(f"{f} обязателен", 422)
    o = Order.query.get(data["order_id"])
    if not o:
        return _json_error("заказ не найден", 422)
    if o.status != Order.STATUS_COMPLETED:
        return _json_error("Отзыв можно оставить только по выполненному заказу.", 422)
    if not User.query.get(data["user_id"]):
        return _json_error("пользователь не найден", 422)
    r = Review(
        order_id=data["order_id"],
        user_id=data["user_id"],
        rating=int(data["rating"]),
        comment=data.get("comment"),
    )
    db.session.add(r)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return _json_error("отзыв уже существует или ошибка БД", 422)
    r = Review.query.get(r.id)
    return jsonify({"data": _review_dict(r)}), 201


@bp.route("/reviews/<int:rid>", methods=["GET"])
def get_review(rid: int):
    r = Review.query.get_or_404(rid)
    return jsonify({"data": _review_dict(r)})


@bp.route("/reviews/<int:rid>", methods=["PUT", "PATCH"])
def update_review(rid: int):
    r = Review.query.get_or_404(rid)
    data = request.get_json(silent=True) or {}
    if "rating" in data:
        r.rating = int(data["rating"])
    if "comment" in data:
        r.comment = data["comment"]
    db.session.commit()
    return jsonify({"data": _review_dict(r)})


@bp.route("/reviews/<int:rid>", methods=["DELETE"])
def delete_review(rid: int):
    r = Review.query.get_or_404(rid)
    db.session.delete(r)
    db.session.commit()
    return "", 204
