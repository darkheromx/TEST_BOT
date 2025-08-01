# app.py

import os
import logging
from logging.handlers import RotatingFileHandler

import uvicorn
from fastapi import (
    FastAPI, Request, Depends, HTTPException, status, Form
)
from fastapi.responses import RedirectResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from passlib.context import CryptContext
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
import openai
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

from config import settings
from handlers.message_router import router as message_router
from handlers.admin_faq import router as admin_faq_router
from services.database import init_db, get_db
from services.cache import init_cache_db
from services.line_sender import send_line_reply
from services.facebook_sender import send_facebook_reply

# ─── Logging: RotatingFileHandler ──────────────────────────────────────────
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
log_path = os.path.join(LOG_DIR, "app.log")
handler = RotatingFileHandler(
    filename=log_path,
    maxBytes=5 * 1024 * 1024,   # 5 MB
    backupCount=5,
    encoding='utf-8'
)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
handler.setFormatter(formatter)
handler.setLevel(logging.INFO)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(handler)

uvicorn_error_logger = logging.getLogger("uvicorn.error")
uvicorn_error_logger.addHandler(handler)

# ─── Sentry for error tracking ────────────────────────────────────────────
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=0.2,
        send_default_pii=True
    )

# ─── Validate required ENV vars ───────────────────────────────────────────
settings.validate()

# ─── Security: HTTP Basic + bcrypt ────────────────────────────────────────
security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def get_current_username(
    credentials: HTTPBasicCredentials = Depends(security)
):
    if credentials.username != settings.ADMIN_USER:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"}
        )
    if not verify_password(
        credentials.password,
        settings.ADMIN_PASSWORD_HASH
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"}
        )
    return credentials.username

# ─── Initialize database & cache ─────────────────────────────────────────
#init_db()
init_cache_db()

# ─── Configure OpenAI API ────────────────────────────────────────────────
openai.api_key = settings.OPENAI_API_KEY

# ─── Create FastAPI app ─────────────────────────────────────────────────
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI Chatbot for LINE & Facebook using RAG + GPT",
    version="1.0.0"
)

# ─── Wrap with Sentry middleware if enabled ──────────────────────────────
if settings.SENTRY_DSN:
    app.add_middleware(SentryAsgiMiddleware)

# ─── Templates & Static files ────────────────────────────────────────────
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ─── Prometheus Metrics ──────────────────────────────────────────────────
REQUEST_COUNT = Counter(
    "p9s_request_count",
    "Total HTTP requests",
    ["method", "endpoint", "http_status"]
)
REQUEST_LATENCY = Histogram(
    "p9s_request_latency_seconds",
    "HTTP request latency",
    ["method", "endpoint"]
)

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    import time
    start = time.time()
    response = await call_next(request)
    latency = time.time() - start
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(latency)
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        http_status=response.status_code
    ).inc()
    return response

@app.get("/metrics")
def metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)

# ─── Include Routers ────────────────────────────────────────────────────
app.include_router(message_router, prefix="/webhook")
app.include_router(admin_faq_router)

# ─── Healthcheck Endpoint ────────────────────────────────────────────────
@app.get("/healthz")
async def healthcheck():
    # Database check
    try:
        db = get_db()
        db.execute("SELECT 1").fetchone()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"DB error: {e}")
    # FAISS index file check
    if not os.path.exists(settings.FAISS_INDEX_PATH):
        raise HTTPException(status_code=503, detail="FAISS index missing")
    # OpenAI connectivity
    try:
        openai.Engine.list()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"OpenAI not reachable: {e}")
    return {"status": "ok", "message": f"{settings.PROJECT_NAME} is healthy"}

# ─── Admin UI: Login & Dashboard ────────────────────────────────────────
@app.get("/admin/login")
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/admin")
async def admin_dashboard(
    request: Request,
    username: str = Depends(get_current_username)
):
    db = get_db()
    faq_count = db.execute("SELECT COUNT(*) FROM faq").fetchone()[0]
    log_count = db.execute("SELECT COUNT(*) FROM chat_logs").fetchone()[0]
    pending_count = db.execute(
        "SELECT COUNT(*) FROM pending_questions WHERE is_answered=0"
    ).fetchone()[0]
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": username,
        "faq_count": faq_count,
        "log_count": log_count,
        "pending_count": pending_count
    })

@app.get("/admin/logout")
async def logout():
    return RedirectResponse(url="/admin/login")

# ─── Admin Pending Questions Management ─────────────────────────────────
@app.get("/admin/pending")
async def view_pending(
    request: Request,
    username: str = Depends(get_current_username),
    q: str = "", platform: str = "", page: int = 1
):
    db = get_db()
    per_page = 10
    base_sql = "FROM pending_questions WHERE is_answered=0"
    params = []
    if q:
        base_sql += " AND question LIKE ?"
        params.append(f"%{q}%")
    if platform:
        base_sql += " AND user_platform=?"
        params.append(platform)
    total = db.execute(f"SELECT COUNT(*) {base_sql}", params).fetchone()[0]
    total_pages = (total + per_page - 1) // per_page
    offset = (page - 1) * per_page
    sql = f"SELECT * {base_sql} ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([per_page, offset])
    rows = [dict(r) for r in db.execute(sql, params).fetchall()]
    pagination = {"page": page, "total_pages": total_pages}
    if page > 1:
        pagination["prev_page"] = page - 1
    if page < total_pages:
        pagination["next_page"] = page + 1
    return templates.TemplateResponse("pending.html", {
        "request": request,
        "rows": rows,
        "pagination": pagination
    })

@app.post("/admin/reply")
async def admin_reply(
    request: Request,
    question_id: int = Form(...),
    reply_text: str = Form(...),
    username: str = Depends(get_current_username)
):
    db = get_db()
    db.execute(
        """
        UPDATE pending_questions
        SET is_answered=1,
            answered_by=?,
            answered_at=CURRENT_TIMESTAMP,
            admin_answer=?
        WHERE id=?
        """,
        (username, reply_text, question_id)
    )
    db.commit()
    rec = db.execute(
        "SELECT user_platform, user_id FROM pending_questions WHERE id=?",
        (question_id,)
    ).fetchone()
    plat, uid = rec["user_platform"], rec["user_id"]
    if plat == "line":
        send_line_reply(uid, reply_text)
    else:
        send_facebook_reply(uid, reply_text)
    return RedirectResponse(url="/admin/pending", status_code=302)

# ─── Global Exception Handler ──────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if settings.SENTRY_DSN:
        sentry_sdk.capture_exception(exc)
    if request.url.path.startswith("/webhook"):
        return JSONResponse(status_code=500, content={"error": "Internal Server Error"})
    return templates.TemplateResponse("error.html", {
        "request": request,
        "error": str(exc)
    })

# ─── Run Local Development Server ────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=settings.PORT, reload=True)
