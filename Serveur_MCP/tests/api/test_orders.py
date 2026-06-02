def test_get_order_livree(client):
    r = client.get("/orders/NTG-2026-000201")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "livree"
    assert len(data["items"]) >= 1


def test_cancel_order_en_preparation(client):
    r = client.post(
        "/orders/NTG-2026-000203/cancel",
        json={"reason": "Test annulation"},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "annulee"


def test_cancel_order_expediee_forbidden(client):
    r = client.post("/orders/NTG-2026-000202/cancel", json={})
    assert r.status_code == 409
    assert "impossible" in r.json()["detail"].lower()


def test_list_orders_by_client(client):
    r = client.get("/orders", params={"client_id": "CL-004"})
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
