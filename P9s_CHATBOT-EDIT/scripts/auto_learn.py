#Path : scripts/auto_learn.py
import sqlite3

def auto_learn():
    conn = sqlite3.connect('data/main.db')
    c = conn.cursor()
    # ดึง pending_questions ที่ answered
    c.execute("SELECT question, admin_answer FROM pending_questions WHERE is_answered=1 AND learned=0")
    rows = c.fetchall()
    for q, a in rows:
        # เพิ่มเป็น FAQ ใหม่
        c.execute("INSERT INTO faq (question, answer, category) VALUES (?,?,?)", (q, a, 'auto'))
        # ทำ mark ว่า learned แล้ว
        c.execute("UPDATE pending_questions SET learned=1 WHERE question=? AND admin_answer=?", (q, a))
    conn.commit()
    conn.close()

if __name__=='__main__':
    auto_learn()
