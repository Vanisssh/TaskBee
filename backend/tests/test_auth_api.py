from __future__ import annotations


def test_auth_register_login_and_me(client):
    register_payload = {
        "name": "Ирина Исполнитель",
        "email": "irina.executor@mail.com",
        "password": "strongpass1",
        "role": "executor",
    }
    reg = client.post("/api/v1/auth/register", json=register_payload)
    assert reg.status_code == 201
    reg_data = reg.get_json()["data"]
    assert reg_data["user"]["role"] == "executor"
    assert reg_data["token"]

    login = client.post(
        "/api/v1/auth/login",
        json={"email": register_payload["email"], "password": register_payload["password"]},
    )
    assert login.status_code == 200
    token = login.get_json()["data"]["token"]
    assert token

    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    me_data = me.get_json()["data"]
    assert me_data["email"] == register_payload["email"]
    assert me_data["role"] == "executor"

    specialists = client.get("/api/v1/specialists")
    assert specialists.status_code == 200
    rows = specialists.get_json()["data"]
    assert any(
        (row.get("user") or {}).get("email") == register_payload["email"]
        for row in rows
    )
