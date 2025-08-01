#Path : services/cache.py
"""
จัดการ Cache สำหรับ GPT เพื่อลดค่าใช้จ่าย และตอบได้เร็วขึ้น
ถ้ามีคำถามเดิม → ดึงจาก cache ก่อนส่งให้ GPT
"""

import sqlite3
import os
from datetime import datetime, timedelta

# === กำหนด path ของไฟล์ cache.db
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DB_PATH = os.path.join(BASE_DIR, "data", "cache.db")

# === สร้างตาราง cache ถ้ายังไม่มี
def init_cache_db():
    conn = sqlite3.connect(CACHE_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gpt_cache (
            question TEXT PRIMARY KEY,
            answer TEXT,
            created_at TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# === ค้นหาใน cache ว่ามีคำถามนี้ไหม
def get_cached_answer(question: str, expiry_minutes: int = 1440) -> str | None:
    conn = sqlite3.connect(CACHE_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT answer, created_at FROM gpt_cache WHERE question = ?", (question,))
    row = cursor.fetchone()
    conn.close()

    if row:
        answer, created_at = row
        created_time = datetime.fromisoformat(created_at)
        if datetime.now() - created_time < timedelta(minutes=expiry_minutes):
            return answer
    return None

# === บันทึกคำตอบใหม่ลง cache
def set_cached_answer(question: str, answer: str):
    conn = sqlite3.connect(CACHE_DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "REPLACE INTO gpt_cache (question, answer, created_at) VALUES (?, ?, ?)",
        (question, answer, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


# === เรียกใช้ทันทีเมื่อ import ไฟล์นี้ เพื่อสร้างตารางไว้
init_cache_db()
