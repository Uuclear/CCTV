# 幕色 API 冒烟测试
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    """健康检查应返回 ok。"""
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["ok"] is True


def test_categories_and_wallpapers():
    """种子数据应包含分类与壁纸。"""
    cats = client.get("/api/categories").json()
    assert len(cats) >= 6
    walls = client.get("/api/wallpapers").json()
    assert walls["total"] >= 10


def test_admin_login_and_stats():
    """管理员可登录并读取统计。"""
    login = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    assert login.status_code == 200
    token = login.json()["access_token"]
    stats = client.get("/api/stats", headers={"Authorization": f"Bearer {token}"})
    assert stats.status_code == 200
    assert stats.json()["category_count"] >= 1


def test_wish_provider_and_create():
    """许愿池提供方信息与提交接口可用。"""
    meta = client.get("/api/wishes/meta/provider")
    assert meta.status_code == 200
    assert meta.json()["cursor_native"] is False
    created = client.post(
        "/api/wishes",
        json={"prompt": "minimal soft gradient wallpaper for phone", "width": 512, "height": 512},
    )
    assert created.status_code == 201
    assert created.json()["status"] in {"pending", "generating", "done"}
