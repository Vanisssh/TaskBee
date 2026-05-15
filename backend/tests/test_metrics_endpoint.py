from __future__ import annotations


def test_metrics_endpoint_exports_prometheus_format(client):
    health = client.get("/health")
    assert health.status_code == 200

    response = client.get("/metrics")
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "http_requests_total" in body
    assert "http_request_duration_seconds_bucket" in body
