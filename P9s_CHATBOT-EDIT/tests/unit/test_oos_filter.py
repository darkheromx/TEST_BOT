import pytest
from core.oos_filter import is_out_of_scope

@pytest.mark.parametrize("msg,expected", [
    ("รหัสสินค้า ABC123", True),
    ("สนใจสมัครเรียนรีแมพ", False),
    ("ราคาเท่าไร", False),  # ราคา ไม่ถือเป็น OOS ในนี้
])
def test_oos_filter(msg, expected):
    assert is_out_of_scope(msg) == expected
