#Path : handlers/message_router.py
from fastapi import APIRouter, Request, Header
from starlette.responses import JSONResponse
from services.database import save_log, save_lead, save_pending_question
from core.intent_classifier import classify_intent
from core.oos_filter import is_out_of_scope, log_oos
from core.lead_capture import process_lead
from core.rag_processor import generate_answer_with_confidence
from services.notification import notify_admin, notify_admin_pending
from services.line_sender import send_line_reply
from services.facebook_sender import send_facebook_reply
from services.rate_limiter import is_rate_limited
from config import settings

router = APIRouter()

@router.post("/line")
async def line_webhook(request: Request, x_line_signature: str = Header(None)):
    # รับ payload
    body = await request.json()
    events = body.get("events", [])
    responses = []

    for event in events:
        user_id = event.get("source", {}).get("userId")
        msg = event.get("message", {}).get("text", "").strip()
        reply_token = event.get("replyToken")

        # 1) Rate limit
        if is_rate_limited(user_id):
            send_line_reply(reply_token, "ระบบกำลังถูกใช้งานสูง กรุณารอสักครู่ค่ะ")
            continue

        # 2) Out-of-scope filter
        if is_out_of_scope(msg):
            log_oos(msg)
            resp = (
                "ขออภัยค่ะ ระบบนี้ให้คำปรึกษาเฉพาะคอร์สรีแมพตัวต่อตัว "
                "กรุณาติดต่อสอบถามข้อมูลคอร์สโดยตรง"
            )
            send_line_reply(reply_token, resp)
            save_log(user_id, 'oos', msg, resp)
            responses.append({"user_id":user_id, "intent":"oos", "question":msg, "answer":resp})
            continue

        # 3) Intent classification
        intent = classify_intent(msg)

        # 4) Process intents
        if intent == 'lead':
            lead_info = process_lead(user_id, msg)
            resp = f"ขอบคุณค่ะ คุณ {lead_info['name']} ทางเราจะติดต่อกลับโดยเร็วที่สุด"

        elif intent == 'ask':
            answer, conf = generate_answer_with_confidence(msg)
            if conf < settings.AUTO_REPLY_THRESHOLD:
                # Save pending
                pid = save_pending_question('line', user_id, msg)
                notify_admin_pending(pid, msg, urgent=True)
                send_line_reply(reply_token,
                    "ขอบคุณสำหรับคำถาม ทีมงานกำลังดำเนินการตอบกลับโดยเร็วที่สุดค่ะ"
                )
                continue
            resp = answer

        else:
            resp = "ขออภัยค่ะ ไม่เข้าใจคำถามของคุณ ลองพิมพ์ใหม่อีกครั้งได้เลยนะคะ"

        # 5) Send and log
        send_line_reply(reply_token, resp)
        save_log(user_id, intent, msg, resp)
        notify_admin(user_id, intent, msg)
        responses.append({"user_id":user_id, "intent":intent, "question":msg, "answer":resp})

    return JSONResponse(status_code=200, content={"results":responses})


@router.post("/facebook")
async def facebook_webhook(request: Request):
    body = await request.json()
    entries = body.get("entry", [])
    responses = []

    for e in entries:
        for ev in e.get("messaging", []):
            sid = ev.get("sender", {}).get("id")
            msg = ev.get("message", {}).get("text", "").strip()

            # 1) Rate limit
            if is_rate_limited(sid):
                send_facebook_reply(sid, "ระบบกำลังถูกใช้งานสูง กรุณารอสักครู่ค่ะ")
                continue

            # 2) Out-of-scope filter
            if is_out_of_scope(msg):
                log_oos(msg)
                resp = (
                    "ขออภัยค่ะ ระบบนี้ให้คำปรึกษาเฉพาะคอร์สรีแมพตัวต่อตัว "
                    "กรุณาติดต่อสอบถามข้อมูลคอร์สโดยตรง"
                )
                send_facebook_reply(sid, resp)
                save_log(sid, 'oos', msg, resp)
                responses.append({"user_id":sid, "intent":"oos", "question":msg, "answer":resp})
                continue

            # 3) Intent classification
            intent = classify_intent(msg)

            if intent == 'lead':
                lead_info = process_lead(sid, msg)
                resp = f"ขอบคุณค่ะ คุณ {lead_info['name']} ทางเราจะติดต่อกลับโดยเร็วที่สุด"

            elif intent == 'ask':
                answer, conf = generate_answer_with_confidence(msg)
                if conf < settings.AUTO_REPLY_THRESHOLD:
                    pid = save_pending_question('facebook', sid, msg)
                    notify_admin_pending(pid, msg, urgent=True)
                    send_facebook_reply(sid,
                        "ขอบคุณสำหรับคำถาม ทีมงานกำลังดำเนินการตอบกลับโดยเร็วที่สุดค่ะ"
                    )
                    continue
                resp = answer

            else:
                resp = "ขออภัยค่ะ ไม่เข้าใจคำถามของคุณ ลองพิมพ์ใหม่อีกครั้งได้เลยนะคะ"

            # 4) Send and log
            send_facebook_reply(sid, resp)
            save_log(sid, intent, msg, resp)
            notify_admin(sid, intent, msg)
            responses.append({"user_id":sid, "intent":intent, "question":msg, "answer":resp})

    return JSONResponse(status_code=200, content={"results":responses})