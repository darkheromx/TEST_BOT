#Path : services/notification.py
"""
services/notification.py
---------------------------------------------------
ส่งการแจ้งเตือนไปยัง Telegram Admin Bot และ LINE Notify
ใช้สำหรับแจ้ง lead ใหม่, pending questions, หรือ error สำคัญ
"""
import requests
from config import settings


def telegram_notify(message: str) -> None:
    """
    ส่งข้อความไปยัง Telegram Admin Bot
    """
    try:
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": settings.TELEGRAM_CHAT_ID,
            "text": message
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"[❌ Telegram Notify Error] {e}")

def notify_admin(message: str) -> None:
    """
    แจ้ง admin ทั่วไป โดยใช้ Telegram
    (สามารถขยายให้ใช้ line_notify ด้วยได้ตามต้องการ)
    """
    telegram_notify(message)


def notify_admin_pending(qid: int, question: str, urgent: bool=False) -> None:
    """
    แจ้ง Admin เมื่อมีคำถามใหม่ใน Pending Questions
    ใช้ทั้ง Telegram และ LINE Notify
    """
    prefix = "[URGENT]" if urgent else "[PENDING]"
    msg = f"{prefix} Q#{qid}: {question}"
    # ส่ง Telegram
    telegram_notify(msg)
    # TODO: เพิ่ม email_notify(msg) ถ้าต้องการ
