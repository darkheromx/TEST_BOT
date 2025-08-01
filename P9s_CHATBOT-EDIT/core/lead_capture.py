#Path : core/lead_capture.py
"""
core/lead_capture.py
---------------------------------------------------
แยกชื่อและเบอร์โทรศัพท์จากข้อความของผู้ใช้
เมื่อเจตนาเป็น "สนใจสมัคร"
"""

import re
from services.notification import notify_admin


def extract_phone(text: str) -> str:
    """
    ดึงเบอร์โทรศัพท์จากข้อความ (รองรับ 9-10 หลัก)
    """
    match = re.search(r"(0\d{8,9})", text)
    return match.group(1) if match else "ไม่พบเบอร์"


def extract_name(text: str) -> str:
    """
    พยายามแยกชื่อ (แบบง่ายๆ จากต้นข้อความ)
    เช่น "ชื่อกิตติครับ" หรือ "ผมชื่อปิยะ"
    """
    match = re.search(r"(ชื่อ|ผมชื่อ|ดิฉันชื่อ|ฉันชื่อ)\s*([\u0E00-\u0E7F]+)", text)
    return match.group(2) if match else "ไม่ระบุชื่อ"


def process_lead(user_id: str, text: str) -> dict:
    """
    ประมวลผล lead → แยกชื่อ เบอร์ → แจ้งแอดมิน

    Returns:
        dict: { name, phone }
    """
    name = extract_name(text)
    phone = extract_phone(text)

    # ✅ แจ้งแอดมินทาง Telegram
    notify_admin(f"[🎯 Lead ใหม่จาก LINE]\n👤 {name}\n📱 {phone}\n🆔 {user_id}")

    return {
        "name": name,
        "phone": phone
    }
