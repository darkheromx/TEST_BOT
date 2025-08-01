import pytest
from core.rag_processor import process_question

def test_process_question_no_index(tmp_path, monkeypatch):
    # ชี้ FAISS index ไปยังไฟล์ชั่วคราวที่ไม่มีอยู่
    monkeypatch.setenv("FAISS_INDEX_PATH", str(tmp_path/"no_index.bin"))
    with pytest.raises(Exception):
        process_question("test")
