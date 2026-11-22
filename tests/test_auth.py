def test_web_register_and_login(client):
    # Register
    res = client.post("/register", data={
        "username": "newuser",
        "email": "new@example.com",
        "password": "mypassword",
        "confirm_password": "mypassword"
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Account created successfully" in res.data

    # Logout
    res = client.get("/logout", follow_redirects=True)
    assert b"logged out" in res.data

    # Login
    res = client.post("/login", data={
        "username": "newuser",
        "password": "mypassword"
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Welcome back" in res.data

def test_web_login_invalid_credentials(client):
    res = client.post("/login", data={
        "username": "nonexistent",
        "password": "wrong"
    }, follow_redirects=True)
    assert b"Invalid username or password" in res.data

def test_api_auth_register(client):
    res = client.post("/api/auth/register", json={
        "username": "apiuser",
        "email": "api@example.com",
        "password": "apipassword"
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data["success"] is True
    assert data["user"]["username"] == "apiuser"

def test_api_auth_register_validation(client):
    # Short password
    res = client.post("/api/auth/register", json={
        "username": "validname",
        "email": "valid@example.com",
        "password": "123"
    })
    assert res.status_code == 400

    # Invalid email
    res = client.post("/api/auth/register", json={
        "username": "validname",
        "email": "bademail",
        "password": "validpassword"
    })
    assert res.status_code == 400

def test_api_auth_login(client):
    client.post("/api/auth/register", json={
        "username": "loginuser",
        "email": "login@example.com",
        "password": "securepassword"
    })
    res = client.post("/api/auth/login", json={
        "username": "loginuser",
        "password": "securepassword"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["user"]["username"] == "loginuser"
