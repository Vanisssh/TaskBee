"""Агрегированная статистика по платформе (дашборд / аналитика заявок)."""

from flask_restx import Namespace, Resource
from sqlalchemy import func

from models import Order, Review, Service, ServiceCategory, Specialist, User, db

ns = Namespace("stats", description="Сводные метрики TaskBee")


@ns.route("/summary")
class StatsSummary(Resource):
    @ns.doc(
        "stats_summary",
        description="Количество заказов по статусам, справочники, средний рейтинг исполнителей (для мониторинга спроса)",
    )
    def get(self):
        order_rows = db.session.query(Order.status, func.count(Order.id)).group_by(Order.status).all()
        orders_by_status = {status: cnt for status, cnt in order_rows}

        rev_avg = db.session.query(func.avg(Review.rating)).scalar()
        spec_avg = db.session.query(func.avg(Specialist.rating_avg)).scalar()

        return {
            "data": {
                "orders_by_status": orders_by_status,
                "total_orders": sum(orders_by_status.values()),
                "total_users": User.query.count(),
                "total_specialists": Specialist.query.count(),
                "total_service_categories": ServiceCategory.query.count(),
                "total_services": Service.query.count(),
                "total_reviews": Review.query.count(),
                "avg_review_rating": float(rev_avg) if rev_avg is not None else None,
                "avg_specialist_rating": float(spec_avg) if spec_avg is not None else None,
            }
        }
