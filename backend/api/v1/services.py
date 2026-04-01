from flask import request
from flask_restx import Namespace, Resource, fields

from api.serializers import service_to_dict
from models import Service, ServiceCategory, db
from schemas import ServiceCreateSchema, ServiceUpdateSchema, validate_load

ns = Namespace("services", description="Услуги")

svc_create = ns.model(
    "ServiceCreate",
    {
        "service_category_id": fields.Integer(required=True),
        "name": fields.String(required=True),
        "description": fields.String(),
    },
)


@ns.route("")
class ServiceList(Resource):
    @ns.doc("list_services", params={"category_id": "Фильтр по категории"})
    def get(self):
        q = Service.query
        cat = request.args.get("category_id", type=int)
        if cat:
            q = q.filter_by(service_category_id=cat)
        rows = q.order_by(Service.name).all()
        return {"data": [service_to_dict(s) for s in rows]}

    @ns.expect(svc_create)
    @ns.response(201, "Created")
    def post(self):
        payload, errors = validate_load(ServiceCreateSchema(), request.get_json(force=True, silent=True))
        if errors:
            return {"error": "validation", "details": errors}, 422
        if not ServiceCategory.query.get(payload["service_category_id"]):
            return {"error": "validation", "details": {"service_category_id": ["категория не найдена"]}}, 422
        s = Service(
            service_category_id=payload["service_category_id"],
            name=payload["name"],
            description=payload.get("description"),
        )
        db.session.add(s)
        db.session.commit()
        s = Service.query.get(s.id)
        return {"data": service_to_dict(s)}, 201


@ns.route("/<int:sid>")
@ns.param("sid", "ID услуги")
class ServiceItem(Resource):
    def get(self, sid: int):
        s = Service.query.get(sid)
        if not s:
            return {"error": "not_found", "message": "Услуга не найдена"}, 404
        return {"data": service_to_dict(s)}

    def put(self, sid: int):
        s = Service.query.get(sid)
        if not s:
            return {"error": "not_found", "message": "Услуга не найдена"}, 404
        payload, errors = validate_load(ServiceUpdateSchema(), request.get_json(force=True, silent=True), partial=True)
        if errors:
            return {"error": "validation", "details": errors}, 422
        if "service_category_id" in payload:
            if not ServiceCategory.query.get(payload["service_category_id"]):
                return {"error": "validation", "details": {"service_category_id": ["категория не найдена"]}}, 422
            s.service_category_id = payload["service_category_id"]
        if "name" in payload:
            s.name = payload["name"]
        if "description" in payload:
            s.description = payload["description"]
        db.session.commit()
        return {"data": service_to_dict(s)}

    patch = put

    def delete(self, sid: int):
        s = Service.query.get(sid)
        if not s:
            return {"error": "not_found", "message": "Услуга не найдена"}, 404
        db.session.delete(s)
        db.session.commit()
        return "", 204
