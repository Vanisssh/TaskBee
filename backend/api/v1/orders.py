from flask import request
from flask_restx import Namespace, Resource, fields

from api.serializers import order_to_dict
from models import Order, Service, Specialist, User, db
from schemas import OrderCreateSchema, OrderUpdateSchema, validate_load

ns = Namespace("orders", description="Заказы на услуги")

ord_create = ns.model(
    "OrderCreate",
    {
        "client_id": fields.Integer(required=True),
        "service_id": fields.Integer(required=True),
        "address": fields.String(),
        "description": fields.String(),
    },
)


@ns.route("")
class OrderList(Resource):
    @ns.doc("list_orders", params={"status": "Фильтр по статусу"})
    def get(self):
        q = Order.query
        st = request.args.get("status")
        if st:
            q = q.filter_by(status=st)
        rows = q.order_by(Order.created_at.desc()).all()
        return {"data": [order_to_dict(o) for o in rows]}

    @ns.expect(ord_create)
    @ns.response(201, "Created")
    def post(self):
        payload, errors = validate_load(OrderCreateSchema(), request.get_json(force=True, silent=True))
        if errors:
            return {"error": "validation", "details": errors}, 422
        if not User.query.get(payload["client_id"]):
            return {"error": "validation", "details": {"client_id": ["клиент не найден"]}}, 422
        if not Service.query.get(payload["service_id"]):
            return {"error": "validation", "details": {"service_id": ["услуга не найдена"]}}, 422
        o = Order(
            client_id=payload["client_id"],
            service_id=payload["service_id"],
            status=Order.STATUS_NEW,
            address=payload.get("address"),
            description=payload.get("description"),
        )
        db.session.add(o)
        db.session.commit()
        o = Order.query.get(o.id)
        return {"data": order_to_dict(o)}, 201


@ns.route("/<int:oid>")
@ns.param("oid", "ID заказа")
class OrderItem(Resource):
    def get(self, oid: int):
        o = Order.query.get(oid)
        if not o:
            return {"error": "not_found", "message": "Заказ не найден"}, 404
        return {"data": order_to_dict(o)}

    def put(self, oid: int):
        o = Order.query.get(oid)
        if not o:
            return {"error": "not_found", "message": "Заказ не найден"}, 404
        payload, errors = validate_load(OrderUpdateSchema(), request.get_json(force=True, silent=True), partial=True)
        if errors:
            return {"error": "validation", "details": errors}, 422
        if "specialist_id" in payload:
            sid = payload["specialist_id"]
            if sid is not None and not Specialist.query.get(sid):
                return {"error": "validation", "details": {"specialist_id": ["исполнитель не найден"]}}, 422
            o.specialist_id = sid
        if "status" in payload:
            o.status = payload["status"]
        if "address" in payload:
            o.address = payload["address"]
        if "description" in payload:
            o.description = payload["description"]
        db.session.commit()
        return {"data": order_to_dict(o)}

    patch = put

    def delete(self, oid: int):
        o = Order.query.get(oid)
        if not o:
            return {"error": "not_found", "message": "Заказ не найден"}, 404
        db.session.delete(o)
        db.session.commit()
        return "", 204
