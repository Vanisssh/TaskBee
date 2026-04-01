"""ORM-модели TaskBee: ИС быстрого поиска и заказа профессиональных услуг."""

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    specialist = db.relationship("Specialist", back_populates="user", uselist=False)
    orders_as_client = db.relationship("Order", back_populates="client", foreign_keys="Order.client_id")
    reviews = db.relationship("Review", back_populates="user")


class ServiceCategory(db.Model):
    __tablename__ = "service_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)

    services = db.relationship("Service", back_populates="category")


class Service(db.Model):
    __tablename__ = "services"

    id = db.Column(db.Integer, primary_key=True)
    service_category_id = db.Column(db.Integer, db.ForeignKey("service_categories.id", ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)

    category = db.relationship("ServiceCategory", back_populates="services")
    orders = db.relationship("Order", back_populates="service")


class Specialist(db.Model):
    __tablename__ = "specialists"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    bio = db.Column(db.Text, nullable=True)
    rating_avg = db.Column(db.Numeric(3, 2), default=0, nullable=False)

    user = db.relationship("User", back_populates="specialist")
    orders = db.relationship("Order", back_populates="specialist")


class Order(db.Model):
    __tablename__ = "orders"

    STATUS_NEW = "new"
    STATUS_ASSIGNED = "assigned"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey("services.id", ondelete="CASCADE"), nullable=False)
    specialist_id = db.Column(db.Integer, db.ForeignKey("specialists.id", ondelete="SET NULL"), nullable=True)
    status = db.Column(db.String(32), default=STATUS_NEW, nullable=False, index=True)
    address = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    client = db.relationship("User", back_populates="orders_as_client", foreign_keys=[client_id])
    service = db.relationship("Service", back_populates="orders")
    specialist = db.relationship("Specialist", back_populates="orders")
    review = db.relationship("Review", back_populates="order", uselist=False)


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    rating = db.Column(db.SmallInteger, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    order = db.relationship("Order", back_populates="review")
    user = db.relationship("User", back_populates="reviews")

    __table_args__ = (UniqueConstraint("order_id", "user_id", name="uq_reviews_order_user"),)
