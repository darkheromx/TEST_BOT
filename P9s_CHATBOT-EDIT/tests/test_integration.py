# tests/test_integration.py
import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db(tmp_path, monkeypatch):
    # ชี้ SQLite ไปยังไฟล์ชั่วคราว
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_file}")
    # สร้าง DB + Index ก่อนทดสอบ
    import scripts.init_db; scripts.init_db.init_db()
    import scripts.build_faq_index; scripts.build_faq_index.main()  # ปรับชื่อฟังก์ชันตามจริง
    yield

def test_healthcheck():
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json().get("status") == "ok"

def test_admin_login_and_faq_crud():
    # เข้าสู่ระบบด้วย Basic Auth
    response = client.get(
        "/admin/faqs",
        auth=("admin", "your_password")  # เปลี่ยนให้ตรงกับ hash ใน .env.test
    )
    assert response.status_code == 200
