# config/settings.py
import os
from dotenv import load_dotenv

# โหลดค่าจาก .env
load_dotenv()

class Settings:
    # ───– Basic API Keys & Tokens –───
    OPENAI_API_KEY            = os.getenv("OPENAI_API_KEY")
    LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    LINE_CHANNEL_SECRET       = os.getenv("LINE_CHANNEL_SECRET")
    # LINE_NOTIFY_TOKEN ตัดออกแล้ว
    FB_PAGE_ACCESS_TOKEN      = os.getenv("FB_PAGE_ACCESS_TOKEN")
    FB_VERIFY_TOKEN           = os.getenv("FB_VERIFY_TOKEN")
    TELEGRAM_BOT_TOKEN        = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID          = os.getenv("TELEGRAM_CHAT_ID")

    # ───– Database & Index Paths –───
    DATABASE_URL              = os.getenv("DATABASE_URL", "sqlite:///data/main.db")
    SQLITE_DB_PATH            = DATABASE_URL.replace("sqlite:///", "")
    FAISS_INDEX_PATH          = os.getenv("FAISS_INDEX_PATH", "data/faiss_index.bin")
    FAQ_MAPPING_PATH          = os.getenv("FAQ_MAPPING_PATH", "data/faq_mapping.pkl")

    # ───– Admin UI / App Settings –───
    ADMIN_USER                = os.getenv("ADMIN_USER", "admin")
    ADMIN_PASSWORD_HASH       = os.getenv("ADMIN_PASSWORD_HASH")
    PROJECT_NAME              = os.getenv("PROJECT_NAME", "P9s_CHATBOT")
    PORT                      = int(os.getenv("PORT", 8000))
    AUTO_REPLY_THRESHOLD      = float(os.getenv("AUTO_REPLY_THRESHOLD", 0.75))

    # ───– Monitoring & Error Tracking –───
    SENTRY_DSN                = os.getenv("SENTRY_DSN", "")

    def validate(self):
        """
        ตรวจสอบว่า ENV vars สำคัญถูกตั้งครบหรือไม่
        เรียก settings.validate() ก่อนเริ่มระบบ
        """
        missing = []
        for var in [
            "OPENAI_API_KEY",
            "LINE_CHANNEL_ACCESS_TOKEN",
            "LINE_CHANNEL_SECRET",
            # LINE_NOTIFY_TOKEN ถูกตัดออก
            "FB_PAGE_ACCESS_TOKEN",
            "FB_VERIFY_TOKEN",
            "TELEGRAM_BOT_TOKEN",
            "TELEGRAM_CHAT_ID",
            "ADMIN_PASSWORD_HASH"
        ]:
            if not getattr(self, var):
                missing.append(var)
        if missing:
            raise EnvironmentError(
                f"[ERROR] Missing required ENV vars: {', '.join(missing)}"
            )

# สร้าง instance ให้ import ใช้ง่าย
settings = Settings()
