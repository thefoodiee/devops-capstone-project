def test_health_check_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert "version" in data
    assert "timestamp" in data

def test_prometheus_metrics_endpoint(client):
    res = client.get("/metrics")
    assert res.status_code == 200
    text = res.get_data(as_text=True)
    assert "notes_http_requests_total" in text
    assert "notes_http_request_duration_seconds" in text

def test_custom_404_handling(client):
    res = client.get("/nonexistent-page")
    assert res.status_code == 404
    assert b"Page Not Found" in res.data

    res_api = client.get("/api/nonexistent")
    assert res_api.status_code == 404
    assert res_api.get_json()["error"] == "Resource not found"

def test_stats_endpoint(client):
    client.post("/api/auth/register", json={
        "username": "statsuser",
        "email": "stats@example.com",
        "password": "password123"
    })
    client.post("/api/notes", json={"title": "N1", "content": "C1", "category": "DevOps", "is_pinned": True})
    client.post("/api/notes", json={"title": "N2", "content": "C2", "category": "DevOps", "is_pinned": False})

    res = client.get("/api/stats")
    assert res.status_code == 200
    data = res.get_json()
    assert data["total_notes"] == 2
    assert data["pinned_notes"] == 1
    assert data["categories"]["DevOps"] == 2
