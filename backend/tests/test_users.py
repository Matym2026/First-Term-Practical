from tests.conftest import register_and_login


def test_register(client):
    res = client.post(
        "/users/register",
        json={"username": "matias", "email": "matias@test.com", "password": "MiClave123"},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "matias@test.com"
    assert "password" not in data
    assert "password_hash" not in data


def test_register_duplicate(client):
    body = {"username": "matias", "email": "matias@test.com", "password": "MiClave123"}
    client.post("/users/register", json=body)
    res = client.post("/users/register", json=body)
    assert res.status_code == 409


def test_register_invalid_data(client):
    res = client.post(
        "/users/register",
        json={"username": "ab", "email": "no-es-email", "password": "123"},
    )
    assert res.status_code == 422


def test_login(client):
    client.post(
        "/users/register",
        json={"username": "matias", "email": "matias@test.com", "password": "MiClave123"},
    )
    res = client.post(
        "/users/login", json={"email": "matias@test.com", "password": "MiClave123"}
    )
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_wrong_password(client):
    client.post(
        "/users/register",
        json={"username": "matias", "email": "matias@test.com", "password": "MiClave123"},
    )
    res = client.post(
        "/users/login", json={"email": "matias@test.com", "password": "incorrecta1"}
    )
    assert res.status_code == 401


def test_me(client):
    headers = register_and_login(client)
    res = client.get("/users/me", headers=headers)
    assert res.status_code == 200
    assert res.json()["username"] == "matias"


def test_me_without_token(client):
    res = client.get("/users/me")
    assert res.status_code == 401