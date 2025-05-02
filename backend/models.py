from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String, default="company")  # 'admin' or 'company'
    created_at = Column(DateTime, default=datetime.utcnow)

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    github_id = Column(String, unique=True)
    username = Column(String)
    email = Column(String)
    location = Column(String)
    languages = Column(String)
    avatar_url = Column(String)
    score = Column(Integer)

class MailLog(Base):
    __tablename__ = "mail_logs"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("users.id"))
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    status = Column(String, default="sent")  # sent / replied
    sent_at = Column(DateTime, default=datetime.utcnow)
