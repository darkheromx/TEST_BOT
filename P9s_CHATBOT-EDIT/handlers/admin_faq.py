# handlers/admin_faq.py

import subprocess
from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from config import settings
from services.database import get_db
from core.models import FAQ, ChatLog, Lead
from app import get_current_username  # เรียกใช้ฟังก์ชัน auth

templates = Jinja2Templates(directory="templates")
router = APIRouter()

# ——— FAQ CRUD ———

@router.get("/admin/faqs")
async def list_faqs(request: Request,
                    db: Session = Depends(get_db),
                    username: str = Depends(get_current_username)):
    faqs = db.query(FAQ).order_by(FAQ.created_at.desc()).all()
    return templates.TemplateResponse("faqs.html", {
        "request": request,
        "faqs": faqs
    })

@router.post("/admin/faqs/create")
async def create_faq(question: str = Form(...),
                     answer: str = Form(...),
                     category: str = Form(""),
                     db: Session = Depends(get_db),
                     username: str = Depends(get_current_username)):
    new = FAQ(question=question, answer=answer, category=category)
    db.add(new)
    db.commit()
    return RedirectResponse(url="/admin/faqs", status_code=302)

@router.post("/admin/faqs/update")
async def update_faq(faq_id: int = Form(...),
                     question: str = Form(...),
                     answer: str = Form(...),
                     category: str = Form(""),
                     db: Session = Depends(get_db),
                     username: str = Depends(get_current_username)):
    faq = db.get(FAQ, faq_id)
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    faq.question = question
    faq.answer = answer
    faq.category = category
    db.commit()
    return RedirectResponse(url="/admin/faqs", status_code=302)

@router.post("/admin/faqs/delete")
async def delete_faq(faq_id: int = Form(...),
                     db: Session = Depends(get_db),
                     username: str = Depends(get_current_username)):
    faq = db.get(FAQ, faq_id)
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    db.delete(faq)
    db.commit()
    return RedirectResponse(url="/admin/faqs", status_code=302)

@router.post("/admin/faqs/rebuild")
async def rebuild_index(username: str = Depends(get_current_username)):
    # เรียกสคริปต์ build_faq_index.py เพื่ออัปเดต FAISS
    subprocess.run(["python3", "scripts/build_faq_index.py"], check=True)
    return RedirectResponse(url="/admin/faqs", status_code=302)

# ——— Log Viewer ———

@router.get("/admin/logs")
async def view_logs(request: Request,
                    db: Session = Depends(get_db),
                    username: str = Depends(get_current_username),
                    q: str = "", page: int = 1):
    per_page = 20
    query = db.query(ChatLog)
    if q:
        query = query.filter(
            (ChatLog.question.contains(q)) |
            (ChatLog.answer.contains(q))
        )
    total = query.count()
    total_pages = (total + per_page - 1) // per_page
    logs = query.order_by(ChatLog.timestamp.desc()) \
                .offset((page-1)*per_page).limit(per_page).all()
    pagination = {
        "page": page,
        "total_pages": total_pages,
        "prev_page": page-1 if page>1 else None,
        "next_page": page+1 if page<total_pages else None
    }
    return templates.TemplateResponse("logs.html", {
        "request": request,
        "rows": logs,
        "pagination": pagination,
        "q": q
    })

# ——— Lead Viewer ———

@router.get("/admin/leads")
async def view_leads(request: Request,
                     db: Session = Depends(get_db),
                     username: str = Depends(get_current_username),
                     page: int = 1):
    per_page = 20
    query = db.query(Lead)
    total = query.count()
    total_pages = (total + per_page - 1) // per_page
    leads = query.order_by(Lead.timestamp.desc()) \
                 .offset((page-1)*per_page).limit(per_page).all()
    pagination = {
        "page": page,
        "total_pages": total_pages,
        "prev_page": page-1 if page>1 else None,
        "next_page": page+1 if page<total_pages else None
    }
    return templates.TemplateResponse("leads.html", {
        "request": request,
        "rows": leads,
        "pagination": pagination
    })
