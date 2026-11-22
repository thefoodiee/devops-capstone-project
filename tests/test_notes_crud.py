def test_notes_crud_api(client):
    # Register & Login
    client.post("/api/auth/register", json={
        "username": "cruduser",
        "email": "crud@example.com",
        "password": "password123"
    })

    # 1. Create Note
    res = client.post("/api/notes", json={
        "title": "Ansible Automation",
        "content": "Playbooks and Roles",
        "category": "Ansible",
        "is_pinned": False
    })
    assert res.status_code == 201
    note_id = res.get_json()["note"]["id"]

    # 2. Get Notes List
    res = client.get("/api/notes")
    assert res.status_code == 200
    data = res.get_json()
    assert data["count"] == 1
    assert data["notes"][0]["title"] == "Ansible Automation"

    # 3. Get Single Note
    res = client.get(f"/api/notes/{note_id}")
    assert res.status_code == 200
    assert res.get_json()["note"]["category"] == "Ansible"

    # 4. Update Note
    res = client.put(f"/api/notes/{note_id}", json={
        "title": "Ansible Automation v2",
        "category": "DevOps",
        "is_pinned": True
    })
    assert res.status_code == 200
    updated = res.get_json()["note"]
    assert updated["title"] == "Ansible Automation v2"
    assert updated["is_pinned"] is True
    assert updated["category"] == "DevOps"

    # 5. Toggle Pin
    res = client.post(f"/api/notes/{note_id}/pin")
    assert res.status_code == 200
    assert res.get_json()["is_pinned"] is False

    # 6. Delete Note
    res = client.delete(f"/api/notes/{note_id}")
    assert res.status_code == 200

    # Verify Note is gone
    res = client.get(f"/api/notes/{note_id}")
    assert res.status_code == 404

def test_notes_search_and_filter(client):
    client.post("/api/auth/register", json={
        "username": "searchuser",
        "email": "search@example.com",
        "password": "password123"
    })

    client.post("/api/notes", json={"title": "Terraform VPC", "content": "AWS VPC Subnets", "category": "Terraform"})
    client.post("/api/notes", json={"title": "Docker Multi-stage", "content": "Lean images", "category": "Docker"})
    client.post("/api/notes", json={"title": "Kubernetes Ingress", "content": "Routing traffic", "category": "Kubernetes"})

    # Filter by category
    res = client.get("/api/notes?category=Terraform")
    assert res.status_code == 200
    assert res.get_json()["count"] == 1
    assert res.get_json()["notes"][0]["title"] == "Terraform VPC"

    # Search keyword
    res = client.get("/api/notes?search=traffic")
    assert res.status_code == 200
    assert res.get_json()["count"] == 1
    assert res.get_json()["notes"][0]["title"] == "Kubernetes Ingress"
