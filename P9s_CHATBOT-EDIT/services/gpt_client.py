#Path : services/gpt_client.py
import time
import openai
from config import settings
from services.cache import get_cached_answer, set_cached_answer

# ตั้งค่า API Key
openai.api_key = settings.OPENAI_API_KEY


def ask_gpt(prompt: str, max_retries: int = 3) -> str:
    """
    ส่ง Prompt ไปยัง GPT API พร้อม retry และ cache:
    1. ถ้ามี cache อยู่แล้ว จะคืนค่าจาก cache
    2. หากไม่เคยถาม ลองเรียก OpenAI API สูงสุด max_retries ครั้ง
       รอเป็น exponential backoff (1s, 2s, 4s, ...)
    3. หากทุกครั้งล้มเหลว จะคืนข้อความ error
    """
    # 1) ตรวจสอบ cache
    cached = get_cached_answer(prompt)
    if cached:
        return cached

    # 2) Retry logic
    for attempt in range(1, max_retries + 1):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": (
                        "คุณคือแชทบอทผู้ช่วยด้าน ECU Remapping ที่สุภาพ "
                        "และให้ข้อมูลเฉพาะจากบริบทที่ให้"
                    )},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            answer = response.choices[0].message.content
            # 3) บันทึก cache
            set_cached_answer(prompt, answer)
            return answer

        except Exception as e:
            # ถ้ายังมีโอกาส retry
            if attempt < max_retries:
                wait_time = 2 ** (attempt - 1)
                time.sleep(wait_time)
                continue
            # retry ครบแล้ว คืน error message
            return f"[ERROR] ไม่สามารถติดต่อ GPT ได้ หลังลอง {max_retries} ครั้ง: {str(e)}"
