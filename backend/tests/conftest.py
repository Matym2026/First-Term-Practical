import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  
from app.db import Base, get_db
from app.main import app
from app.services import s3


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture(autouse=True)
def setup_db():
    """Crea las tablas antes de cada test y las borra después."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def fake_s3(monkeypatch):
    """Reemplaza las funciones de S3 por versiones falsas (sin AWS)."""
    monkeypatch.setattr(
        s3,
        "generate_upload_url",
        lambda key, content_type, kind="video": {
            "upload_url": "https://fake-s3/upload",
            "object_key": key,
            "expires_in": 900,
        },
    )
    monkeypatch.setattr(
        s3,
        "generate_download_url",
        lambda key, kind="video": {"url": "https://fake-s3/download", "expires_in": 3600},
    )
    monkeypatch.setattr(s3, "delete_object", lambda key, kind="video": None)



def register_and_login(client, username="matias", email="matias@test.com"):
    """Registra un usuario y devuelve sus headers con el token."""
    client.post(
        "/users/register",
        json={"username": username, "email": email, "password": "MiClave123"},
    )
    res = client.post("/users/login", json={"email": email, "password": "MiClave123"})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_video(client, headers, user_id=1, name="prueba.mp4"):
    """Crea un video y devuelve la respuesta."""
    return client.post(
        "/videos",
        json={
            "title": "Mi video",
            "description": "Prueba",
            "filename": name,
            "s3_key": f"videos/{user_id}/{name}",
        },
        headers=headers,
    )