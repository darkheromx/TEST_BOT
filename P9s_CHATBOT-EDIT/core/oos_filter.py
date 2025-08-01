#Path : core/oos_filter.py
import re
from services.database import get_db

# คีย์เวิร์ดนอกขอบเขต
OOS_KEYWORDS = [
    r'\bราคา\b', r'\bสั่งซื้อ\b', r'\bรหัสสินค้า\b', r'\bโค้ดสินค้า\b'
]

def is_out_of_scope(message: str) -> bool:
    text = message.lower()
    return any(re.search(k, text) for k in OOS_KEYWORDS)

def log_oos(message: str):
    db = get_db()
    db.execute("INSERT INTO oos_logs (message) VALUES (?)", (message,))
    db.commit()
