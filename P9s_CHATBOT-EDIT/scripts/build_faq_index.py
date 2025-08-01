#Path : scripts/build_faq_index.py
"""
scripts/build_faq_index.py
---------------------------------------------------
ใช้สร้างไฟล์ faiss_index.bin จาก knowledge_base.csv
เพื่อให้บอทค้นหาคำตอบได้เร็วขึ้นผ่านเวกเตอร์ (FAISS)
"""

import pandas as pd
import faiss
import os
import pickle
from sentence_transformers import SentenceTransformer

def main():
    # === Path ของโปรเจกต์
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    CSV_PATH = os.path.join(DATA_DIR, "knowledge_base.csv")
    INDEX_PATH = os.path.join(DATA_DIR, "faiss_index.bin")
    MAPPING_PATH = os.path.join(DATA_DIR, "faq_mapping.pkl")

    # === โหลดโมเดลฝังเวกเตอร์
    print("🔍 Loading sentence-transformer model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # === โหลดไฟล์ความรู้
    print(f"📚 Loading knowledge base from: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)

    if "question" not in df.columns or "answer" not in df.columns:
        raise ValueError("❌ ไฟล์ knowledge_base.csv ต้องมีคอลัมน์ 'question' และ 'answer'")

    # === แปลงข้อความคำถามเป็นเวกเตอร์
    print("⚙️ Encoding questions into vectors...")
    embeddings = model.encode(df["question"].tolist(), show_progress_bar=True)

    # === สร้าง FAISS Index
    print("🧠 Building FAISS index...")
    dimension = embeddings[0].shape[0]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # === บันทึก Index และ Mapping
    print(f"💾 Saving index to: {INDEX_PATH}")
    faiss.write_index(index, INDEX_PATH)

    with open(MAPPING_PATH, "wb") as f:
        pickle.dump(df.to_dict(orient="records"), f)

    print("✅ Success! FAISS index & mapping saved.")

if __name__ == "__main__":
    main()

