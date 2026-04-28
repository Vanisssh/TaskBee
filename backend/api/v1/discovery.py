from __future__ import annotations

import json
import logging
import os
from typing import Any

import redis
import requests
from flask import request
from flask_restx import Namespace, Resource, fields

log = logging.getLogger("taskbee.discovery")

ns = Namespace("discovery", description="Service discovery (Consul or Redis-backed)")

service_model = ns.model("ServiceRegister", {"id": fields.String(required=True), "address": fields.String(required=True), "tags": fields.List(fields.String)})

# Helper to get redis client

def get_redis():
    host = os.environ.get("REDIS_HOST", "redis")
    port = int(os.environ.get("REDIS_PORT", "6379"))
    return redis.Redis(host=host, port=port, socket_connect_timeout=2, decode_responses=True)


def consul_available() -> bool:
    try:
        r = requests.get("http://consul:8500/v1/status/leader", timeout=1)
        return r.status_code == 200
    except Exception:
        return False


@ns.route("/register")
class Register(Resource):
    @ns.expect(service_model)
    def post(self):
        payload = request.json or {}
        service_id = payload.get("id")
        address = payload.get("address")
        tags = payload.get("tags", [])
        if not service_id or not address:
            return {"error": "id and address required"}, 400

        # Try Consul first
        if consul_available():
            try:
                host, port = address.split(":")
                consul_url = "http://consul:8500/v1/agent/service/register"
                body = {
                    "ID": service_id,
                    "Name": service_id,
                    "Address": host,
                    "Port": int(port),
                    "Tags": tags,
                    "Check": {"HTTP": f"http://{address}/health", "Interval": "10s"},
                }
                r = requests.put(consul_url, json=body, timeout=2)
                if r.status_code not in (200, 204):
                    log.warning("Consul register returned %s %s", r.status_code, r.text)
                    return {"error": "consul_register_failed"}, 502
                return {"status": "registered_consul"}, 200
            except Exception as e:
                log.exception("Consul registration failed: %s", e)
                return {"error": "consul_register_exception", "detail": str(e)}, 502

        # Fallback to Redis TTL registration
        try:
            rdb = get_redis()
            key = f"discovery:service:{service_id}"
            rdb.set(key, json.dumps({"id": service_id, "address": address, "tags": tags}))
            rdb.expire(key, 60)
            return {"status": "registered_redis"}, 200
        except Exception as e:
            log.exception("Redis registration failed: %s", e)
            return {"error": "redis_register_failed", "detail": str(e)}, 500


@ns.route("/services")
class ServicesList(Resource):
    def get(self):
        tag = request.args.get("tag")

        # If consul available, query agent/services
        if consul_available():
            try:
                r = requests.get("http://consul:8500/v1/agent/services", timeout=2)
                svc_map = r.json()
                results: list[dict[str, Any]] = []
                for sid, info in svc_map.items():
                    entry = {
                        "id": sid,
                        "name": info.get("Service"),
                        "address": f"{info.get('Address')}:{info.get('Port')}",
                        "tags": info.get("Tags", []),
                    }
                    results.append(entry)
                if tag:
                    results = [s for s in results if tag in (s.get("tags") or [])]
                return results, 200
            except Exception as e:
                log.exception("Consul list failed: %s", e)
                # fallthrough to redis

        # Redis fallback: scan keys
        try:
            rdb = get_redis()
            keys = rdb.keys("discovery:service:*")
            results = []
            for k in keys:
                raw = rdb.get(k)
                if not raw:
                    continue
                try:
                    obj = json.loads(raw)
                except Exception:
                    continue
                if tag and tag not in (obj.get("tags") or []):
                    continue
                results.append({"id": obj.get("id"), "address": obj.get("address"), "tags": obj.get("tags", [])})
            return results, 200
        except Exception as e:
            log.exception("Redis list failed: %s", e)
            return {"error": "discovery_unavailable", "detail": str(e)}, 503


@ns.route("/renew")
class Renew(Resource):
    def post(self):
        payload = request.json or {}
        service_id = payload.get("id")
        if not service_id:
            return {"error": "id required"}, 400

        # If consul is used, try to mark service check as passing (best-effort)
        if consul_available():
            try:
                check_id = f"service:{service_id}"
                r = requests.put(f"http://consul:8500/v1/agent/check/pass/{check_id}", timeout=2)
                if r.status_code in (200, 204):
                    return {"status": "renewed_consul"}, 200
            except Exception as e:
                log.info("Consul renew failed: %s", e)
                # fallthrough to redis

        # Redis fallback: refresh TTL
        try:
            rdb = get_redis()
            key = f"discovery:service:{service_id}"
            if not rdb.exists(key):
                return {"error": "not_registered"}, 404
            rdb.expire(key, 60)
            return {"status": "renewed_redis"}, 200
        except Exception as e:
            log.exception("Redis renew failed: %s", e)
            return {"error": "renew_failed", "detail": str(e)}, 500
