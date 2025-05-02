# backend/utils.py

import bcrypt

def hash_password(password: str) -> str:
    """비밀번호를 bcrypt로 해싱합니다."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """입력된 비밀번호와 해시된 비밀번호를 비교합니다."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode())
