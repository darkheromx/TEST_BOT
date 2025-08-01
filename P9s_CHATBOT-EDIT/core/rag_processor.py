#Path : core/rag_processor.py
from typing import Tuple
import os
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from services.gpt_client import ask_gpt

# Path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
INDEX_PATH = os.path.join(DATA_DIR, "faiss_index.bin")
MAPPING_PATH = os.path.join(DATA_DIR, "faq_mapping.pkl")

# โหลดโมเดล
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
# โหลด FAISS index และ mapping
faiss_index = faiss.read_index(INDEX_PATH)
with open(MAPPING_PATH, "rb") as f:
    faq_mapping = pickle.load(f)


def process_question(user_question: str) -> str:
    # encode
    vector = embedding_model.encode([user_question])
    # search
    k = 3
    _, indices = faiss_index.search(vector, k)
    # รวบรวม context
    retrieved = ""
    for idx in indices[0]:
        if idx < len(faq_mapping):
            q = faq_mapping[idx]['question']
            a = faq_mapping[idx]['answer']
            retrieved += f"Q: {q}\nA: {a}\n\n"
    prompt = (
        f"ข้อมูลที่เกี่ยวข้อง:\n{retrieved}"
        f"คำถามจากผู้ใช้: {user_question}\n"
        f"กรุณาตอบอย่างสุภาพและเป็นธรรมชาติ โดยอิงจากข้อมูลที่ให้เท่านั้น หากไม่มีข้อมูล กรุณาตอบว่า 'ไม่พบข้อมูลค่ะ'"
    )
    return ask_gpt(prompt)


def compute_confidence(user_question: str, answer: str) -> float:
    v1 = embedding_model.encode([user_question])[0]
    v2 = embedding_model.encode([answer])[0]
    from numpy.linalg import norm
    from numpy import dot
    return float(dot(v1, v2) / (norm(v1)*norm(v2)))


def generate_answer_with_confidence(user_question: str) -> Tuple[str, float]:
    answer = process_question(user_question)
    conf = compute_confidence(user_question, answer)
    return answer, conf