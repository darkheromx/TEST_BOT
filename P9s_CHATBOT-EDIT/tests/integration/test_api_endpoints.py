import os
import pytest
from fastapi.testclient import TestClient

# ชี้ DATABASE_URL ไปยังไฟล์ชั่วคราว
@pytest.fixture(autouse=True)
def setup_env(tmp_path, monkeypatch):
    db_file = tmp_path/"test.db"
    # ให้ init_db.py ทำงานสร้างตาราง
    from scripts.init_db import init_db
    init_db_path = tmp_path/"data"
    init_db()
    # ชี้ DATABASE_URL
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_file}")
    yield

from app import app

client = TestClient(app)

def test_healthz():
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

def test_admin_login_fail():
    resp = client.get("/admin", auth=("wrong","wrong"))
    assert resp.status_code == 401
