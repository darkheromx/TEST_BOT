#Path : services/line_sender.py
"""
services/line_sender.py
---------------------------------------------------
ส่งข้อความตอบกลับไปยังผู้ใช้ LINE ด้วย LINE Messaging API
"""

import requests
from config import settings


def send_line_reply(reply_token: str, message: str) -> None:
    """
    ใช้ LINE Messaging API ส่งข้อความกลับไปยังผู้ใช้

    Args:
        reply_token (str): โทเคนที่ได้จาก Webhook ของ LINE
        message (str): ข้อความที่ต้องการส่งกลับ
    """
    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.LINE_CHANNEL_ACCESS_TOKEN}"
    }
    body = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": message}]
    }

    try:
        response = requests.post(url, json=body, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(f"[❌ LINE Reply Error] {e}")
