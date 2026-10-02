from tests.conftest import create_video, register_and_login


def setup_video(client):
    headers = register_and_login(client)
    video_id = create_video(client, headers).json()["id"]
    return headers, video_id


def test_create_comment(client):
    headers, video_id = setup_video(client)
    res = client.post(
        f"/videos/{video_id}/comments", json={"content": "Excelente"}, headers=headers
    )
    assert res.status_code == 201
    assert res.json()["content"] == "Excelente"
    assert res.json()["user_id"] == 1


def test_create_comment_without_token(client):
    _, video_id = setup_video(client)
    res = client.post(f"/videos/{video_id}/comments", json={"content": "Hola"})
    assert res.status_code == 401


def test_create_comment_video_not_found(client):
    headers = register_and_login(client)
    res = client.post("/videos/999/comments", json={"content": "Hola"}, headers=headers)
    assert res.status_code == 404


def test_create_comment_empty(client):
    headers, video_id = setup_video(client)
    res = client.post(
        f"/videos/{video_id}/comments", json={"content": ""}, headers=headers
    )
    assert res.status_code == 422


def test_list_comments(client):
    headers, video_id = setup_video(client)
    client.post(f"/videos/{video_id}/comments", json={"content": "Uno"}, headers=headers)
    client.post(f"/videos/{video_id}/comments", json={"content": "Dos"}, headers=headers)
    res = client.get(f"/videos/{video_id}/comments")
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_update_comment(client):
    headers, video_id = setup_video(client)
    comment_id = client.post(
        f"/videos/{video_id}/comments", json={"content": "Original"}, headers=headers
    ).json()["id"]
    res = client.put(
        f"/comments/{comment_id}", json={"content": "Editado"}, headers=headers
    )
    assert res.status_code == 200
    assert res.json()["content"] == "Editado"


def test_update_comment_not_owner(client):
    headers, video_id = setup_video(client)
    other = register_and_login(client, "maria", "maria@test.com")
    comment_id = client.post(
        f"/videos/{video_id}/comments", json={"content": "Mio"}, headers=headers
    ).json()["id"]
    res = client.put(f"/comments/{comment_id}", json={"content": "Hack"}, headers=other)
    assert res.status_code == 403


def test_delete_comment(client):
    headers, video_id = setup_video(client)
    comment_id = client.post(
        f"/videos/{video_id}/comments", json={"content": "Borrar"}, headers=headers
    ).json()["id"]
    res = client.delete(f"/comments/{comment_id}", headers=headers)
    assert res.status_code == 204
    assert client.get(f"/videos/{video_id}/comments").json() == []


def test_delete_comment_not_owner(client):
    headers, video_id = setup_video(client)
    other = register_and_login(client, "maria", "maria@test.com")
    comment_id = client.post(
        f"/videos/{video_id}/comments", json={"content": "Mio"}, headers=headers
    ).json()["id"]
    res = client.delete(f"/comments/{comment_id}", headers=other)
    assert res.status_code == 403