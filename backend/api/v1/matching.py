from __future__ import annotations

import json
import logging
import os
import uuid

import pika
from flask import request
from flask_restx import Namespace, Resource, fields
from tenacity import retry, stop_after_attempt, wait_exponential

from metrics import MATCHING_CANDIDATE_COUNT, MATCHING_RPC_REQUESTS_TOTAL, MATCHING_TOP_SCORE

log = logging.getLogger("taskbee.matching")

ns = Namespace("matching", description="Интеллектуальный подбор исполнителей через RabbitMQ")

request_model = ns.model(
    "MatchingRequest",
    {
        "order": fields.Raw(
            required=True,
            description="Данные заказа: category, budget, client_location и т.д.",
        ),
        "candidates": fields.List(
            fields.Raw,
            required=True,
            description="Кандидаты на подбор со служебными метриками",
        ),
    },
)


def _rabbitmq_url() -> str:
    return os.environ.get("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/%2F")


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=5))
def _rpc_recommendation(payload: dict, timeout_s: float = 8.0) -> dict:
    """RPC-запрос к matcher-service через RabbitMQ."""
    params = pika.URLParameters(_rabbitmq_url())
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    ch.queue_declare(queue="matcher.requests", durable=True)

    result: dict = {}
    corr_id = str(uuid.uuid4())
    callback_queue = ch.queue_declare(queue="", exclusive=True).method.queue

    def _on_response(_ch, _method, props, body):
        if props.correlation_id == corr_id:
            nonlocal result
            try:
                result = json.loads(body.decode("utf-8"))
            except Exception:
                result = {"error": "invalid_matcher_response"}
            _ch.stop_consuming()

    ch.basic_consume(queue=callback_queue, on_message_callback=_on_response, auto_ack=True)
    ch.basic_publish(
        exchange="",
        routing_key="matcher.requests",
        body=json.dumps(payload).encode("utf-8"),
        properties=pika.BasicProperties(
            reply_to=callback_queue,
            correlation_id=corr_id,
            delivery_mode=2,
            headers={"X-Request-ID": request.headers.get("X-Request-ID", corr_id)},
        ),
    )
    conn.process_data_events(time_limit=timeout_s)
    if not result:
        conn.close()
        raise TimeoutError("matcher timeout")
    conn.close()
    return result


def _fallback_recommendation(payload: dict, reason: str) -> dict:
    """Fallback при недоступности брокера/микросервиса."""
    candidates = payload.get("candidates") or []
    if not candidates:
        return {
            "best_match": None,
            "ranking": [],
            "meta": {"source": "fallback", "reason": reason},
        }

    ranking = sorted(
        (
            {
                "specialist_id": c.get("specialist_id"),
                "score": round(float(c.get("rating", 0)) / 5.0, 4),
                "details": {"rating": float(c.get("rating", 0))},
            }
            for c in candidates
        ),
        key=lambda x: x["score"],
        reverse=True,
    )

    return {
        "best_match": ranking[0] if ranking else None,
        "ranking": ranking,
        "meta": {"source": "fallback", "reason": reason},
    }


@ns.route("/recommendations")
class MatchingRecommendations(Resource):
    @ns.expect(request_model)
    def post(self):
        payload = request.get_json(force=True, silent=True) or {}
        order = payload.get("order") or {}
        candidates = payload.get("candidates") or []
        if not isinstance(order, dict):
            return {"error": "validation", "details": {"order": ["must be an object"]}}, 422
        if not isinstance(candidates, list) or not candidates:
            return {"error": "validation", "details": {"candidates": ["must be non-empty list"]}}, 422

        api_key = os.environ.get("MATCHER_API_KEY")
        header_key = request.headers.get("X-API-Key")
        if api_key and header_key != api_key:
            return {"error": "forbidden", "message": "Invalid API key"}, 403

        MATCHING_CANDIDATE_COUNT.observe(len(candidates))
        try:
            result = _rpc_recommendation({"order": order, "candidates": candidates})
            result.setdefault("meta", {})
            result["meta"]["source"] = "matcher-service"
            MATCHING_RPC_REQUESTS_TOTAL.labels("matcher-service").inc()
            best_match = result.get("best_match") or {}
            score = best_match.get("score")
            if isinstance(score, (int, float)):
                MATCHING_TOP_SCORE.observe(float(score))
            return {"data": result}, 200
        except Exception as exc:
            log.warning("Matcher RPC unavailable: %s", exc)
            MATCHING_RPC_REQUESTS_TOTAL.labels("fallback").inc()
            return {"data": _fallback_recommendation(payload, str(exc))}, 200


@ns.route("/health")
class MatchingHealth(Resource):
    def get(self):
        return {
            "status": "ok",
            "service": "matching-api",
            "broker": _rabbitmq_url(),
        }, 200
