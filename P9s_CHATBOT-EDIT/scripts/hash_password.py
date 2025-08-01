#Path : scripts\hash_password.py
#!/usr/bin/env python3
"""
scripts/hash_password.py

รัน:
    python scripts/hash_password.py
แล้วใส่รหัสผ่าน → จะโชว์ bcrypt hash ออกมา
"""
import sys
import getpass
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pw = sys.argv[1]
    else:
        pw = getpass.getpass("Enter password to hash: ")
    print(hash_password(pw))
