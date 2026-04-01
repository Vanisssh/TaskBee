"""Сериализация моделей в JSON для ответов API."""

from __future__ import annotations

from models import Order, Review, Service, Specialist


def order_to_dict(o: Order) -> dict:
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
        "specialist": {
            "id": o.specialist.id,
            "user_id": o.specialist.user_id,
            "rating_avg": float(o.specialist.rating_avg),
        }
        if o.specialist
        else None,
    }


def review_to_dict(r: Review) -> dict:
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


def specialist_to_dict(s: Specialist) -> dict:
    return {
        "id": s.id,
        "user_id": s.user_id,
        "bio": s.bio,
        "rating_avg": float(s.rating_avg),
        "user": {"id": s.user.id, "name": s.user.name, "email": s.user.email} if s.user else None,
    }


def service_to_dict(s: Service) -> dict:
    return {
        "id": s.id,
        "service_category_id": s.service_category_id,
        "name": s.name,
        "description": s.description,
        "category": {"id": s.category.id, "name": s.category.name, "slug": s.category.slug} if s.category else None,
    }
