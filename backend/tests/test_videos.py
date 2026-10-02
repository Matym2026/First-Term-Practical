from tests.conftest import create_video, register_and_login


def test_create_video(client):
    headers = register_and_login(client)
    res = create_video(client, headers)
    assert res.status_code == 201
    assert res.json()["owner_id"] == 1
    assert res.json()["views"] == 0


def test_create_video_without_token(client):
    res = client.post(
        "/videos",
        json={"title": "x", "filename": "x.mp4", "s3_key": "videos/1/x.mp4"},
    )
    assert res.status_code == 401


def test_create_video_invalid_s3_key(client):
    headers = register_and_login(client)
    res = client.post(
        "/videos",
        json={"title": "x", "filename": "x.mp4", "s3_key": "videos/99/x.mp4"},
        headers=headers,
    )
    assert res.status_code == 400


def test_create_video_duplicate_key(client):
    headers = register_and_login(client)
    create_video(client, headers)
    res = create_video(client, headers)
    assert res.status_code == 409


def test_list_videos(client):
    headers = register_and_login(client)
    create_video(client, headers, name="a.mp4")
    create_video(client, headers, name="b.mp4")
    res = client.get("/videos")
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_get_video(client):
    headers = register_and_login(client)
    video_id = create_video(client, headers).json()["id"]
    res = client.get(f"/videos/{video_id}")
    assert res.status_code == 200
    assert res.json()["title"] == "Mi video"


def test_get_video_not_found(client):
    res = client.get("/videos/999")
    assert res.status_code == 404


def test_update_video(client):
    headers = register_and_login(client)
    video_id = create_video(client, headers).json()["id"]
    res = client.put(f"/videos/{video_id}", json={"title": "Nuevo"}, headers=headers)
    assert res.status_code == 200
    assert res.json()["title"] == "Nuevo"
    assert res.json()["description"] == "Prueba"  # no cambió


def test_update_video_not_owner(client):
    owner = register_and_login(client)
    other = register_and_login(client, "maria", "maria@test.com")
    video_id = create_video(client, owner).json()["id"]
    res = client.put(f"/videos/{video_id}", json={"title": "Hack"}, headers=other)
    assert res.status_code == 403


def test_delete_video(client):
    headers = register_and_login(client)
    video_id = create_video(client, headers).json()["id"]
    res = client.delete(f"/videos/{video_id}", headers=headers)
    assert res.status_code == 204
    assert client.get(f"/videos/{video_id}").status_code == 404


def test_delete_video_not_owner(client):
    owner = register_and_login(client)
    other = register_and_login(client, "maria", "maria@test.com")
    video_id = create_video(client, owner).json()["id"]
    res = client.delete(f"/videos/{video_id}", headers=other)
    assert res.status_code == 403


def test_upload_url(client):
    headers = register_and_login(client)
    res = client.post(
        "/videos/upload-url",
        json={"filename": "mi video.mp4", "content_type": "video/mp4", "kind": "video"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["upload_url"] == "https://fake-s3/upload"
    assert data["object_key"].startswith("videos/1/")
    assert data["expires_in"] == 900


def test_upload_url_invalid_content_type(client):
    headers = register_and_login(client)
    res = client.post(
        "/videos/upload-url",
        json={"filename": "doc.pdf", "content_type": "application/pdf", "kind": "video"},
        headers=headers,
    )
    assert res.status_code == 422


def test_download_url(client):
    headers = register_and_login(client)
    video_id = create_video(client, headers).json()["id"]
    res = client.get(f"/videos/{video_id}/download-url")
    assert res.status_code == 200
    assert res.json()["video_id"] == video_id
    assert res.json()["url"] == "https://fake-s3/download"