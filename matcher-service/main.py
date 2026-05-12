from __future__ import annotations

import json
import logging
import math
import os
import threading
import time
import uuid
from typing import Any

import pika
import requests
from flask import Flask

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("matcher-service")

RABBITMQ_URL = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/%2F")
DISCOVERY_URL = os.environ.get("DISCOVERY_URL", "http://backend:5000/api/v1/discovery")
SERVICE_PORT = int(os.environ.get("SERVICE_PORT", "8001"))
SERVICE_ID = os.environ.get("SERVICE_ID", f"matcher-{os.environ.get('HOSTNAME', 'local')}")
SERVICE_ADDRESS = os.environ.get("SERVICE_ADDRESS", f"matcher-service:{SERVICE_PORT}")

app = Flask(__name__)


@app.get("/health")
def health():
    return {"status": "ok", "service": "matcher-service"}, 200


def _distance_km(a: dict[str, Any], b: dict[str, Any]) -> float:
    lat1, lon1 = float(a.get("lat", 0)), float(a.get("lon", 0))
    lat2, lon2 = float(b.get("lat", 0)), float(b.get("lon", 0))
    return math.sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) * 111


def _score_candidate(order: dict[str, Any], cand: dict[str, Any]) -> dict[str, Any]:
    client_location = order.get("client_location") or {}
    specialist_location = cand.get("location") or {}
    distance_km = _distance_km(client_location, specialist_location)

    rating_norm = max(0.0, min(float(cand.get("rating", 0.0)) / 5.0, 1.0))
    response_norm = 1.0 - max(0.0, min(float(cand.get("response_time_min", 60)) / 60.0, 1.0))
    workload_norm = 1.0 - max(0.0, min(float(cand.get("active_orders", 10)) / 10.0, 1.0))
    category_norm = 1.0 if bool(cand.get("category_match", True)) else 0.0
    distance_norm = 1.0 - max(0.0, min(distance_km / 50.0, 1.0))

    budget = float(order.get("budget", 0))
    price = float(cand.get("price", 0))
    if budget <= 0:
        price_norm = 0.5
    elif price <= budget:
        price_norm = 1.0
    else:
        overflow = min((price - budget) / max(budget, 1.0), 1.0)
        price_norm = max(0.0, 1.0 - overflow)

    score = (
        0.30 * rating_norm
        + 0.20 * distance_norm
        + 0.15 * response_norm
        + 0.15 * workload_norm
        + 0.10 * category_norm
        + 0.10 * price_norm
    )

    return {
        "specialist_id": cand.get("specialist_id"),
        "score": round(score, 4),
        "details": {
            "distance_km": round(distance_km, 2),
            "rating_norm": round(rating_norm, 3),
            "response_norm": round(response_norm, 3),
            "workload_norm": round(workload_norm, 3),
            "category_norm": round(category_norm, 3),
            "price_norm": round(price_norm, 3),
        },
    }


def compute_recommendation(payload: dict[str, Any]) -> dict[str, Any]:
    order = payload.get("order") or {}
    candidates = payload.get("candidates") or []
    ranked = [_score_candidate(order, cand) for cand in candidates]
    ranked.sort(key=lambda x: x["score"], reverse=True)
    return {
        "best_match": ranked[0] if ranked else None,
        "ranking": ranked,
        "meta": {"model": "weighted-v1", "candidate_count": len(ranked)},
    }


def _register() -> None:
    payload = {
        "id": SERVICE_ID,
        "address": SERVICE_ADDRESS,
        "tags": ["matching", "rabbitmq", "intelligent-selection"],
    }
    try:
        requests.post(f"{DISCOVERY_URL}/register", json=payload, timeout=3)
    except Exception as exc:
        log.warning("Discovery register failed: %s", exc)


def _renew_loop() -> None:
    while True:
        try:
            requests.post(f"{DISCOVERY_URL}/renew", json={"id": SERVICE_ID}, timeout=3)
        except Exception as exc:
            log.debug("Discovery renew failed: %s", exc)
        time.sleep(20)


def _consume_loop() -> None:
    params = pika.URLParameters(RABBITMQ_URL)
    while True:
        try:
            conn = pika.BlockingConnection(params)
            ch = conn.channel()
            ch.queue_declare(queue="matcher.requests", durable=True)
            ch.basic_qos(prefetch_count=1)

            def _callback(channel, method, props, body):
                request_id = props.headers.get("X-Request-ID") if props.headers else str(uuid.uuid4())
                try:
                    payload = json.loads(body.decode("utf-8"))
                    result = compute_recommendation(payload)
                    result.setdefault("meta", {})
                    result["meta"]["request_id"] = request_id
                except Exception as exc:
                    result = {"error": "invalid_payload", "message": str(exc), "meta": {"request_id": request_id}}
                if props.reply_to:
                    channel.basic_publish(
                        exchange="",
                        routing_key=props.reply_to,
                        body=json.dumps(result).encode("utf-8"),
                        properties=pika.BasicProperties(correlation_id=props.correlation_id),
                    )
                channel.basic_ack(delivery_tag=method.delivery_tag)

            ch.basic_consume(queue="matcher.requests", on_message_callback=_callback)
            log.info("Matcher consumer started on queue matcher.requests")
            ch.start_consuming()
        except Exception as exc:
            log.warning("RabbitMQ connection/consume error: %s. Retry in 3s...", exc)
            time.sleep(3)


if __name__ == "__main__":
    _register()
    threading.Thread(target=_renew_loop, daemon=True).start()
    threading.Thread(target=_consume_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=SERVICE_PORT)
