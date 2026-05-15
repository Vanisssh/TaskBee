from __future__ import annotations

import json

import api.v1.discovery as discovery_module


class FakeRedis:
    def __init__(self):
        self.storage: dict[str, str] = {}

    def set(self, key: str, value: str):
        self.storage[key] = value
        return True

    def expire(self, key: str, _seconds: int):
        return key in self.storage

    def keys(self, pattern: str):
        if pattern == "discovery:service:*":
            return list(self.storage.keys())
        return []

    def get(self, key: str):
        return self.storage.get(key)

    def exists(self, key: str):
        return key in self.storage


def test_discovery_register_services_and_renew_with_redis_fallback(client, monkeypatch):
    fake_redis = FakeRedis()

    monkeypatch.setattr(discovery_module, "consul_available", lambda: False)
    monkeypatch.setattr(discovery_module, "get_redis", lambda: fake_redis)

    payload = {"id": "generator-test", "address": "generator:8000", "tags": ["data-generator", "matching"]}
    register = client.post("/api/v1/discovery/register", json=payload)
    assert register.status_code == 200
    assert register.get_json()["status"] == "registered_redis"

    services = client.get("/api/v1/discovery/services")
    assert services.status_code == 200
    rows = services.get_json()
    assert any(r["id"] == "generator-test" for r in rows)
    assert json.loads(fake_redis.get("discovery:service:generator-test"))["address"] == "generator:8000"

    renew = client.post("/api/v1/discovery/renew", json={"id": "generator-test"})
    assert renew.status_code == 200
    assert renew.get_json()["status"] == "renewed_redis"
