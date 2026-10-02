from tests.conftest import create_video, register_and_login


def test_increment_views(client):
    headers = register_and_login(client)
    video_id = create_video(client, headers).json()["id"]

    assert client.post(f"/videos/{video_id}/views").json()["views"] == 1
    assert client.post(f"/videos/{video_id}/views").json()["views"] == 2
    assert client.post(f"/videos/{video_id}/views").json()["views"] == 3
    assert client.get(f"/videos/{video_id}").json()["views"] == 3


def test_increment_views_not_found(client):
    res = client.post("/videos/999/views")
    assert res.status_code == 404