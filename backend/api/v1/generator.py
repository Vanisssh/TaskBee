from __future__ import annotations

import logging
import os
from typing import Any

import requests
from flask_restx import Namespace, Resource

log = logging.getLogger("taskbee.generator_proxy")

ns = Namespace("generator", description="Статус фонового генератора данных (микросервис generator)")

GENERATOR_STATS_URL = os.environ.get("GENERATOR_STATS_URL", "http://generator:8000/stats")


@ns.route("/status")
class GeneratorStatus(Resource):
    @ns.doc("generator_status", description="Прокси к GET http://generator:8000/stats для панели мониторинга")
    def get(self) -> tuple[dict[str, Any], int]:
        try:
            r = requests.get(GENERATOR_STATS_URL, timeout=2)
            if not r.ok:
                return {
                    "data": {"reachable": False, "http_status": r.status_code, "detail": r.text[:200]},
                }, 200
            body = r.json()
            return {"data": {"reachable": True, "generator": body}}, 200
        except Exception as e:
            log.info("Generator stats unreachable: %s", e)
            return {"data": {"reachable": False, "detail": str(e)}}, 200
