import pytest
from core.intent_classifier import classify_intent

@pytest.mark.parametrize("text,expected", [
    ("ผมสนใจสมัครคอร์ส", "lead"),
    ("ราคาเท่าไรครับ", "lead"),  # คำว่า ราคา ใน lead_keywords
    ("สวัสดีค่ะ", "ask"),
    ("มีคำถาม", "ask"),
])
def test_classify_intent(text, expected):
    assert classify_intent(text) == expected
