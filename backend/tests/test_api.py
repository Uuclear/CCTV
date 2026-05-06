from unittest.mock import patch

from fastapi.testclient import TestClient

from app.config import settings


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


def test_project_patch(client: TestClient):
    r = client.post("/api/projects", json={"name": "patch-me"})
    pid = r.json()["id"]
    r2 = client.patch(
        f"/api/projects/{pid}",
        json={"client_org": "XX 单位", "road_name": "测试路"},
    )
    assert r2.status_code == 200
    body = r2.json()
    assert body["client_org"] == "XX 单位"
    assert body["road_name"] == "测试路"
    assert body["name"] == "patch-me"


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


def test_upload_video_and_extract_preview_mocked(
    client: TestClient, tmp_path, monkeypatch
) -> None:
    monkeypatch.setattr(settings, "files_dir", tmp_path)
    r = client.post("/api/projects", json={"name": "vid-proj"})
    pid = r.json()["id"]
    r2 = client.post(f"/api/projects/{pid}/segments", json={})
    sid = r2.json()["id"]
    files = {"file": ("clip.mp4", b"fake-bytes", "video/mp4")}
    r3 = client.post(f"/api/segments/{sid}/video", files=files)
    assert r3.status_code == 200
    assert "uploads/" in r3.json()["video_relpath"]
    with patch("app.routers.segments.video_frames.extract_preview_png", return_value=2.5):
        r4 = client.post(f"/api/segments/{sid}/extract-preview", json={"margin_sec": 0.5})
    assert r4.status_code == 200
    body = r4.json()
    assert body["sample_time_sec"] == 2.5
    assert body["preview_frame_relpath"].startswith("previews/")


def test_extract_preview_requires_video(client: TestClient) -> None:
    r = client.post("/api/projects", json={"name": "no-vid"})
    pid = r.json()["id"]
    r2 = client.post(f"/api/projects/{pid}/segments", json={})
    sid = r2.json()["id"]
    r3 = client.post(f"/api/segments/{sid}/extract-preview", json={})
    assert r3.status_code == 400
