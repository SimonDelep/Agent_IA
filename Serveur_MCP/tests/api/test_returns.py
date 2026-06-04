def test_create_return_duplicate_pending(client):
    r = client.post(
        "/returns",
        json={
            "order_id": "NTG-2026-000201",
            "product_id": "NTG-SHOE-001",
            "reason": "test_doublon",
        },
    )
    assert r.status_code == 409


def test_create_return_outside_window(client):
    r = client.post(
        "/returns",
        json={
            "order_id": "NTG-2026-000212",
            "product_id": "NTG-SLEEP-001",
            "reason": "hors_delai",
        },
    )
    assert r.status_code == 409
    assert "expir" in r.json()["detail"].lower()


def test_create_return_new_order(client):
    r = client.post(
        "/returns",
        json={
            "order_id": "NTG-2026-000202",
            "product_id": "NTG-JKT-001",
            "reason": "taille_incorrecte",
            "notes": "Test API",
        },
    )
    assert r.status_code == 201
    data = r.json()
    assert data["status"] == "pending"
    assert data["return_id"].startswith("RET-")


def test_get_return(client):
    r = client.get("/returns/RET-2026-001")
    assert r.status_code == 200
    assert r.json()["status"] == "pending"
