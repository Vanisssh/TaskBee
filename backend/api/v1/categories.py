from flask import request
from flask_restx import Namespace, Resource, fields

from models import ServiceCategory, db
from schemas import CategoryCreateSchema, CategoryUpdateSchema, validate_load

ns = Namespace("categories", description="Категории услуг")

cat_model = ns.model(
    "Category",
    {"id": fields.Integer(), "name": fields.String(), "slug": fields.String()},
)
cat_create = ns.model(
    "CategoryCreate",
    {"name": fields.String(required=True), "slug": fields.String(required=True)},
)


@ns.route("")
class CategoryList(Resource):
    @ns.doc("list_categories")
    def get(self):
        rows = ServiceCategory.query.order_by(ServiceCategory.name).all()
        return {"data": [{"id": c.id, "name": c.name, "slug": c.slug} for c in rows]}

    @ns.expect(cat_create)
    @ns.doc("create_category")
    @ns.response(201, "Created")
    @ns.response(422, "Validation error")
    def post(self):
        payload, errors = validate_load(CategoryCreateSchema(), request.get_json(force=True, silent=True))
        if errors:
            return {"error": "validation", "details": errors}, 422
        if ServiceCategory.query.filter_by(slug=payload["slug"]).first():
            return {"error": "validation", "details": {"slug": ["slug уже занят"]}}, 422
        c = ServiceCategory(name=payload["name"], slug=payload["slug"])
        db.session.add(c)
        db.session.commit()
        return {"data": {"id": c.id, "name": c.name, "slug": c.slug}}, 201


@ns.route("/<int:cid>")
@ns.param("cid", "ID категории")
class CategoryItem(Resource):
    def get(self, cid: int):
        c = ServiceCategory.query.get(cid)
        if not c:
            return {"error": "not_found", "message": "Категория не найдена"}, 404
        services = [{"id": s.id, "name": s.name, "description": s.description} for s in c.services]
        return {"data": {"id": c.id, "name": c.name, "slug": c.slug, "services": services}}

    @ns.response(422, "Validation error")
    def put(self, cid: int):
        c = ServiceCategory.query.get(cid)
        if not c:
            return {"error": "not_found", "message": "Категория не найдена"}, 404
        payload, errors = validate_load(CategoryUpdateSchema(), request.get_json(force=True, silent=True), partial=True)
        if errors:
            return {"error": "validation", "details": errors}, 422
        if "name" in payload:
            c.name = payload["name"]
        if "slug" in payload:
            existing = ServiceCategory.query.filter(ServiceCategory.slug == payload["slug"], ServiceCategory.id != cid).first()
            if existing:
                return {"error": "validation", "details": {"slug": ["slug уже занят"]}}, 422
            c.slug = payload["slug"]
        db.session.commit()
        return {"data": {"id": c.id, "name": c.name, "slug": c.slug}}

    patch = put

    def delete(self, cid: int):
        c = ServiceCategory.query.get(cid)
        if not c:
            return {"error": "not_found", "message": "Категория не найдена"}, 404
        db.session.delete(c)
        db.session.commit()
        return "", 204
