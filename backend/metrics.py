"""Метрики наблюдаемости для backend и микросервисной интеграции."""

from __future__ import annotations

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests handled by backend",
    ["method", "endpoint", "status"],
)

HTTP_REQUEST_LATENCY_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10),
)

MATCHING_RPC_REQUESTS_TOTAL = Counter(
    "matching_rpc_requests_total",
    "Number of matching recommendation requests",
    ["source"],
)

MATCHING_CANDIDATE_COUNT = Histogram(
    "matching_candidate_count",
    "Number of candidates per matching request",
    buckets=(1, 2, 3, 5, 8, 10, 15, 20, 30),
)

MATCHING_TOP_SCORE = Histogram(
    "matching_top_score",
    "Best candidate score returned by matching service",
    buckets=(0.0, 0.2, 0.4, 0.6, 0.8, 1.0),
)

GENERATOR_STATUS_CHECKS_TOTAL = Counter(
    "generator_status_checks_total",
    "Backend checks to generator status endpoint",
    ["reachable"],
)

GENERATOR_REACHABLE = Gauge(
    "generator_reachable",
    "Current availability of generator service (1 reachable, 0 unreachable)",
)


def observe_http_request(method: str, endpoint: str, status: int, latency_seconds: float) -> None:
    HTTP_REQUESTS_TOTAL.labels(method, endpoint, str(status)).inc()
    HTTP_REQUEST_LATENCY_SECONDS.labels(method, endpoint).observe(latency_seconds)


def export_metrics() -> tuple[bytes, str]:
    payload = generate_latest()
    return payload, CONTENT_TYPE_LATEST
