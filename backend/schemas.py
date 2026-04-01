"""Marshmallow-схемы валидации (ЛР3) для TaskBee."""

from __future__ import annotations

from marshmallow import Schema, ValidationError, fields, validate


class CategoryCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    slug = fields.Str(required=True, validate=validate.Length(min=1, max=255))


class CategoryUpdateSchema(Schema):
    name = fields.Str(validate=validate.Length(min=1, max=255))
    slug = fields.Str(validate=validate.Length(min=1, max=255))


class ServiceCreateSchema(Schema):
    service_category_id = fields.Int(required=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    description = fields.Str(load_default=None, allow_none=True)


class ServiceUpdateSchema(Schema):
    service_category_id = fields.Int()
    name = fields.Str(validate=validate.Length(min=1, max=255))
    description = fields.Str(allow_none=True)


class OrderCreateSchema(Schema):
    client_id = fields.Int(required=True)
    service_id = fields.Int(required=True)
    address = fields.Str(load_default=None, allow_none=True)
    description = fields.Str(load_default=None, allow_none=True)


class OrderUpdateSchema(Schema):
    specialist_id = fields.Int(allow_none=True)
    status = fields.Str(
        validate=validate.OneOf(["new", "assigned", "in_progress", "completed", "cancelled"]),
        allow_none=True,
    )
    address = fields.Str(allow_none=True)
    description = fields.Str(allow_none=True)


class ReviewCreateSchema(Schema):
    order_id = fields.Int(required=True)
    user_id = fields.Int(required=True)
    rating = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    comment = fields.Str(load_default=None, allow_none=True)


class ReviewUpdateSchema(Schema):
    rating = fields.Int(validate=validate.Range(min=1, max=5))
    comment = fields.Str(allow_none=True)


class UserCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    email = fields.Email(required=True)
    password_hash = fields.Str(load_default=None, allow_none=True)


class SpecialistCreateSchema(Schema):
    user_id = fields.Int(required=True)
    bio = fields.Str(load_default=None, allow_none=True)
    rating_avg = fields.Decimal(load_default=0, places=2, validate=validate.Range(min=0, max=5))


class SpecialistUpdateSchema(Schema):
    bio = fields.Str(allow_none=True)
    rating_avg = fields.Decimal(places=2, validate=validate.Range(min=0, max=5))


def validate_load(schema: Schema, data: dict | None, *, partial: bool = False):
    """Возвращает (payload|None, errors|None)."""
    try:
        return schema.load(data or {}, partial=partial), None
    except ValidationError as e:
        return None, e.messages
