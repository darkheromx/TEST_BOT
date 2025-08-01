#Path : core/intent_classifier.py
"""
core/intent_classifier.py
---------------------------------------------------
แยกแยะว่าเจตนาของผู้ใช้คือ "ถามคำถาม" หรือ "สนใจสมัคร"
แบบ rule-based ง่าย ๆ
"""

import re

# คำที่บ่งบอกว่าเป็น lead (สนใจสมัครเรียน)
lead_keywords = [
    "สนใจ", "สมัคร", "ราคา", "ติดต่อ", "เรียน", "คอร์ส", "จอง", "รายละเอียด", "ค่าใช้จ่าย", "มัดจำ"
]

def classify_intent(text: str) -> str:
    """
    จำแนกว่าเป็นคำถามทั่วไป (ask) หรือสนใจสมัคร (lead)

    Returns:
        "lead" หรือ "ask"
    """
    text = text.lower()

    for kw in lead_keywords:
        if re.search(rf"\b{kw}\b", text):
            return "lead"

    return "ask"
