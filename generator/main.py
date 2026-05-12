from __future__ import annotations

import logging
import os
import random
import time
import uuid

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("taskbee-generator")

BACKEND_BASE = os.environ.get("BACKEND_URL", "http://backend:5000")
DISCOVERY_URL = os.environ.get("DISCOVERY_URL", f"{BACKEND_BASE}/api/v1/discovery")
MATCHING_URL = os.environ.get("MATCHING_URL", f"{BACKEND_BASE}/api/v1/matching/recommendations")
GENERATOR_API_KEY = os.environ.get("GENERATOR_API_KEY", "")
GENERATOR_INTERVAL = int(os.environ.get("GENERATOR_INTERVAL_SECONDS", "8"))
SERVICE_PORT = int(os.environ.get("SERVICE_PORT", "8000"))
SERVICE_ID = os.environ.get("SERVICE_ID", f"generator-{os.environ.get('HOSTNAME', 'local')}")
SERVICE_ADDRESS = os.environ.get("SERVICE_ADDRESS", f"generator:{SERVICE_PORT}")


def _headers() -> dict[str, str]:
    headers = {"Content-Type": "application/json", "X-Request-ID": str(uuid.uuid4())}
    if GENERATOR_API_KEY:
        headers["X-API-Key"] = GENERATOR_API_KEY
    return headers


def register_service() -> None:
    payload = {"id": SERVICE_ID, "address": SERVICE_ADDRESS, "tags": ["data-generator", "matching"]}
    try:
        requests.post(f"{DISCOVERY_URL}/register", json=payload, timeout=3)
        log.info("Registered in discovery as %s", SERVICE_ID)
    except Exception as exc:
        log.warning("Discovery registration failed: %s", exc)


def renew_service() -> None:
    try:
        requests.post(f"{DISCOVERY_URL}/renew", json={"id": SERVICE_ID}, timeout=3)
    except Exception as exc:
        log.debug("Discovery renew failed: %s", exc)


def _first_id(path: str) -> int | None:
    resp = requests.get(f"{BACKEND_BASE}{path}", timeout=5)
    resp.raise_for_status()
    rows = (resp.json() or {}).get("data", [])
    if not rows:
        return None
    return rows[0].get("id")


def _get(path: str) -> list[dict]:
    resp = requests.get(f"{BACKEND_BASE}{path}", timeout=5)
    resp.raise_for_status()
    return (resp.json() or {}).get("data", [])


def _post(path: str, payload: dict) -> dict:
    resp = requests.post(f"{BACKEND_BASE}{path}", json=payload, timeout=5)
    if resp.status_code not in (200, 201):
        return {}
    return (resp.json() or {}).get("data", {})


def _get_specialists() -> list[dict]:
    return _get("/api/v1/specialists")


def ensure_seed_data() -> None:
    categories = _get("/api/v1/categories")
    if not categories:
        _post("/api/v1/categories", {"name": "Быстрые услуги", "slug": "quick-services"})
        categories = _get("/api/v1/categories")
    category_id = categories[0]["id"]

    services = _get("/api/v1/services")
    if not services:
        _post(
            "/api/v1/services",
            {
                "service_category_id": category_id,
                "name": "Интеллектуальный подбор исполнителя",
                "description": "Тестовый сервис для микросервисного матчинга",
            },
        )

    users = _get("/api/v1/users")
    if not users:
        _post("/api/v1/users", {"name": "Тестовый клиент", "email": "client@taskbee.local"})
        for idx in range(1, 6):
            _post(
                "/api/v1/users",
                {"name": f"Исполнитель {idx}", "email": f"specialist{idx}@taskbee.local"},
            )

    specialists = _get_specialists()
    if not specialists:
        users = _get("/api/v1/users")
        for idx, user in enumerate(users[1:6], start=1):
            _post(
                "/api/v1/specialists",
                {
                    "user_id": user["id"],
                    "bio": f"Профиль исполнителя {idx}",
                    "rating_avg": round(random.uniform(3.8, 4.9), 2),
                },
            )


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
def create_order() -> dict:
    client_id = _first_id("/api/v1/users")
    service_id = _first_id("/api/v1/services")
    if not client_id or not service_id:
        raise RuntimeError("Для генерации нужны записи users/services в БД")

    payload = {
        "client_id": client_id,
        "service_id": service_id,
        "address": random.choice(["Москва, ЦАО", "Москва, ЮАО", "Санкт-Петербург, Центр"]),
        "description": random.choice(
            [
                "Нужен срочный подбор специалиста",
                "Требуется исполнитель на вечер",
                "Ищу исполнителя с высоким рейтингом",
            ]
        ),
    }
    resp = requests.post(f"{BACKEND_BASE}/api/v1/orders", json=payload, timeout=5)
    resp.raise_for_status()
    return (resp.json() or {}).get("data", {})


def _candidate_from_specialist(spec: dict, order_budget: float) -> dict:
    user = spec.get("user") or {}
    random.seed(f"{spec.get('id')}:{user.get('email')}:{time.time() // 60}")
    return {
        "specialist_id": spec.get("id"),
        "rating": float(spec.get("rating_avg", 0)),
        "response_time_min": random.randint(2, 45),
        "active_orders": random.randint(0, 8),
        "category_match": random.choice([True, True, True, False]),
        "price": round(order_budget * random.uniform(0.7, 1.35), 2),
        "location": {
            "lat": round(55.75 + random.uniform(-0.2, 0.2), 6),
            "lon": round(37.61 + random.uniform(-0.2, 0.2), 6),
        },
    }


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
def request_matching(order: dict) -> dict:
    specialists = _get_specialists()
    if not specialists:
        raise RuntimeError("Нет специалистов для подбора")
    budget = random.randint(1200, 6000)
    candidates = [_candidate_from_specialist(s, budget) for s in specialists][:10]
    payload = {
        "order": {
            "order_id": order.get("id"),
            "budget": budget,
            "category": "taskbee-services",
            "client_location": {
                "lat": round(55.75 + random.uniform(-0.1, 0.1), 6),
                "lon": round(37.61 + random.uniform(-0.1, 0.1), 6),
            },
        },
        "candidates": candidates,
    }
    resp = requests.post(MATCHING_URL, json=payload, headers=_headers(), timeout=10)
    resp.raise_for_status()
    data = (resp.json() or {}).get("data", {})
    return data


def assign_best_match(order_id: int, best_match: dict | None) -> None:
    if not best_match:
        return
    specialist_id = best_match.get("specialist_id")
    if not specialist_id:
        return
    payload = {"specialist_id": specialist_id, "status": "assigned"}
    requests.patch(f"{BACKEND_BASE}/api/v1/orders/{order_id}", json=payload, timeout=5)


def run_loop() -> None:
    register_service()
    ensure_seed_data()
    last_renew = 0.0
    while True:
        now = time.time()
        if now - last_renew > 20:
            renew_service()
            last_renew = now
        try:
            order = create_order()
            result = request_matching(order)
            assign_best_match(order["id"], result.get("best_match"))
            best = result.get("best_match") or {}
            log.info(
                "Order #%s processed, best specialist=%s score=%s source=%s",
                order.get("id"),
                best.get("specialist_id"),
                best.get("score"),
                (result.get("meta") or {}).get("source"),
            )
        except Exception as exc:
            log.error("Generator iteration failed: %s", exc)
        time.sleep(GENERATOR_INTERVAL)


if __name__ == "__main__":
    run_loop()
