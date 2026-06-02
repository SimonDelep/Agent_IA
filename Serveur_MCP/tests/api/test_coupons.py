def test_validate_trail20_valid(client):
    r = client.post(
        "/coupons/validate",
        json={"code": "TRAIL20", "client_id": "CL-004", "order_subtotal": 200.0},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["valid"] is True
    assert data["discount_amount"] == 40.0


def test_validate_summit10_invalid(client):
    r = client.post(
        "/coupons/validate",
        json={"code": "SUMMIT10", "client_id": "CL-004", "order_subtotal": 100.0},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["valid"] is False


def test_validate_vip15_non_gold(client):
    r = client.post(
        "/coupons/validate",
        json={"code": "VIP15", "client_id": "CL-002", "order_subtotal": 150.0},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["valid"] is False
    assert "gold" in data["message"].lower()


def test_validate_vip15_gold(client):
    r = client.post(
        "/coupons/validate",
        json={"code": "VIP15", "client_id": "CL-012", "order_subtotal": 150.0},
    )
    assert r.status_code == 200
    assert r.json()["valid"] is True
