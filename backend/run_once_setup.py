from database import engine, SessionLocal
from models import Base, User
from utils import hash_password
from models import Base, User, Candidate  


# 1. DB 테이블 생성
Base.metadata.create_all(bind=engine)

# 2. 초기 유저 삽입
with SessionLocal() as db:
    if not db.query(User).filter(User.email == "admin@kosa.ai").first():
        user = User(
            email="admin@kosa.ai",
            password_hash=hash_password("1234"),
            role="company"
        )
        db.add(user)
        db.commit()
        print("✅ 관리자 계정 생성 완료: admin@kosa.ai / 1234")
    else:
        print("ℹ️ 이미 admin@kosa.ai 계정이 존재합니다.")

# 후보자 더미 데이터
from models import Candidate

candidate = Candidate(
    github_id="123456",
    username="noahdev",
    email="noah@example.com",
    location="Seoul",
    languages="Python, JavaScript",
    avatar_url="https://avatars.githubusercontent.com/u/123456?v=4",
    score=87
)

db.add(candidate)
db.commit()
