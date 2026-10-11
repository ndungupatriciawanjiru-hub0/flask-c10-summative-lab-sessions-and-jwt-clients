from conftest import signup


def make_note(client, title="Title", content="Body"):
    return client.post("/notes", json={"title": title, "content": content})


def test_notes_require_login(client):
    assert client.get("/notes").status_code == 401
    assert client.post("/notes", json={"title": "a", "content": "b"}).status_code == 401
    assert client.patch("/notes/1", json={"title": "x"}).status_code == 401
    assert client.delete("/notes/1").status_code == 401


def test_create_and_validation(client):
    signup(client)
    assert make_note(client).status_code == 201
    assert client.post("/notes", json={"title": "only title"}).status_code == 422


def test_update_and_delete(client):
    signup(client)
    note_id = make_note(client).get_json()["id"]
    res = client.patch(f"/notes/{note_id}", json={"title": "New"})
    assert res.status_code == 200 and res.get_json()["title"] == "New"
    assert client.delete(f"/notes/{note_id}").status_code == 204
    assert client.get(f"/notes/{note_id}").status_code == 404


def test_pagination(client):
    signup(client)
    for i in range(12):
        make_note(client, title=f"Note {i}")
    page1 = client.get("/notes?page=1&per_page=5").get_json()
    assert len(page1["items"]) == 5
    assert page1["total"] == 12 and page1["pages"] == 3
    page3 = client.get("/notes?page=3&per_page=5").get_json()
    assert len(page3["items"]) == 2 and page3["has_next"] is False
    assert client.get("/notes?page=abc").status_code == 400


def test_users_cannot_touch_each_others_notes(client):
    signup(client, "alice")
    note_id = make_note(client).get_json()["id"]
    client.delete("/logout")

    signup(client, "bob")
    assert client.get("/notes").get_json()["total"] == 0
    assert client.get(f"/notes/{note_id}").status_code == 404
    assert client.patch(f"/notes/{note_id}", json={"title": "hax"}).status_code == 404
    assert client.delete(f"/notes/{note_id}").status_code == 404

    client.delete("/logout")
    client.post("/login", json={"username": "alice", "password": "secret123"})
    assert client.get(f"/notes/{note_id}").get_json()["title"] == "Title"
