from __future__ import annotations

import os
import random

from locust import HttpUser, between, task

MATCHER_API_KEY = os.environ.get("MATCHER_API_KEY", "taskbee-matcher-key")


class TaskBeeResearchUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self._specialists = []
        self._refresh_specialists()

    def _refresh_specialists(self):
        response = self.client.get("/api/v1/specialists", name="/api/v1/specialists")
        if not response.ok:
            return
        payload = response.json() or {}
        self._specialists = payload.get("data") or []

    def _build_matching_payload(self):
        if not self._specialists:
            self._refresh_specialists()
        sampled = (self._specialists or [])[: min(10, len(self._specialists))]
        candidates = []
        budget = random.randint(1200, 6000)
        for s in sampled:
            candidates.append(
                {
                    "specialist_id": s.get("id"),
                    "rating": float(s.get("rating_avg", 0)),
                    "response_time_min": random.randint(2, 40),
                    "active_orders": random.randint(0, 8),
                    "category_match": random.choice([True, True, False]),
                    "price": round(budget * random.uniform(0.75, 1.25), 2),
                    "location": {
                        "lat": round(55.75 + random.uniform(-0.2, 0.2), 6),
                        "lon": round(37.61 + random.uniform(-0.2, 0.2), 6),
                    },
                }
            )
        return {
            "order": {
                "order_id": 0,
                "budget": budget,
                "category": "taskbee-services",
                "client_location": {"lat": 55.7522, "lon": 37.6156},
            },
            "candidates": candidates or [{"specialist_id": 0, "rating": 4.0}],
        }

    @task(3)
    def get_summary_metrics(self):
        self.client.get("/api/v1/stats/summary", name="/api/v1/stats/summary")

    @task(2)
    def get_recent_orders(self):
        self.client.get("/api/v1/orders", name="/api/v1/orders")

    @task(1)
    def get_discovery_services(self):
        self.client.get("/api/v1/discovery/services", name="/api/v1/discovery/services")

    @task(2)
    def matching_recommendation(self):
        payload = self._build_matching_payload()
        headers = {"X-API-Key": MATCHER_API_KEY}
        self.client.post("/api/v1/matching/recommendations", json=payload, headers=headers, name="/api/v1/matching/recommendations")

    @task(1)
    def generator_status(self):
        self.client.get("/api/v1/generator/status", name="/api/v1/generator/status")
