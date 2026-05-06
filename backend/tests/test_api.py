from fastapi.testclient import TestClient


def test_health(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_project_crud_flow(client: TestClient):
    r = client.post(
        "/api/projects",
        json={"name": "pytest-project", "client_org": "client-a", "project_code": "P-1"},
    )
    assert r.status_code == 200
    pid = r.json()["id"]
    r2 = client.get(f"/api/projects/{pid}")
    assert r2.json()["name"] == "pytest-project"
    r3 = client.get("/api/projects")
    ids = [p["id"] for p in r3.json()]
    assert pid in ids


def test_segment_list_and_patch(client: TestClient):
    r = client.post("/api/projects", json={"name": "list-test"})
    pid = r.json()["id"]
    client.post(
        f"/api/projects/{pid}/segments",
        json={"display_name": "old.mp4"},
    )
    r2 = client.get(f"/api/projects/{pid}/segments")
    assert r2.status_code == 200
    assert len(r2.json()) == 1
    sid = r2.json()[0]["id"]
    r3 = client.patch(
        f"/api/segments/{sid}",
        json={"display_name": "new.mp4", "chain_start_label": "A1", "chain_end_label": "A2"},
    )
    assert r3.json()["display_name"] == "new.mp4"
    assert r3.json()["chain_start_label"] == "A1"


def test_segment_defect_recomputes_indices(client: TestClient):
    r = client.post("/api/projects", json={"name": "seg-test"})
    pid = r.json()["id"]
    r2 = client.post(
        f"/api/projects/{pid}/segments",
        json={"chain_start_label": "W1", "chain_end_label": "W2"},
    )
    assert r2.status_code == 200
    sid = r2.json()["id"]
    assert r2.json()["ri"] == 0.0 and r2.json()["mi"] == 0.0
    client.post(
        f"/api/segments/{sid}/defects",
        json={"defect_code": "PL", "level": 2, "kind": "structural"},
    )
    r3 = client.get(f"/api/segments/{sid}")
    assert r3.json()["ri"] is not None and r3.json()["ri"] > 0
