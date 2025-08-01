#Path : services/facebook_sender.py
import httpx
from config import settings

FB_API_URL = "https://graph.facebook.com/v17.0/me/messages"

def send_facebook_reply(recipient_id: str, message_text: str):
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.FB_PAGE_ACCESS_TOKEN}"
    }

    try:
        response = httpx.post(FB_API_URL, json=payload, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(f"[❌ FB Reply Error] {e}")
