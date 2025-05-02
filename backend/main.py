from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.status import HTTP_302_FOUND
import httpx
import os
from dotenv import load_dotenv

from backend.database import SessionLocal
from backend.models import User, Candidate, MailLog
from backend.utils import verify_password


# Load GitHub token from .env file
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

app = FastAPI()

# 템플릿과 정적 파일 폴더 설정
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

GITHUB_API_URL = "https://api.github.com/search/users"
GITHUB_HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"token {GITHUB_TOKEN}"
}

# 홈(랜딩) 페이지
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 로그인 페이지
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# 로그인 처리
@app.post("/login")
async def login_process(request: Request, email: str = Form(...), password: str = Form(...)):
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    db.close()
    if user and verify_password(password, user.password_hash):
        return RedirectResponse(url="/dashboard", status_code=302)
    return RedirectResponse(url="/login", status_code=302)

# 대시보드 페이지
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "current_page": "dashboard"
    })

# 후보자 리스트
@app.get("/candidates", response_class=HTMLResponse)
async def candidate_list(request: Request):
    db = SessionLocal()
    candidates = db.query(Candidate).all()
    db.close()
    return templates.TemplateResponse("candidates.html", {
        "request": request,
        "candidates": candidates,
        "current_page": "candidates"
    })

# 메일 발송 처리
@app.post("/send-mail")
async def send_mail(request: Request, candidate_ids: list[int] = Form(...)):
    db = SessionLocal()
    for cid in candidate_ids:
        mail = MailLog(
            company_id=1,  # TODO: 실제 로그인된 기업 ID로 교체
            candidate_id=cid,
            status="sent"
        )
        db.add(mail)
    db.commit()
    db.close()
    return RedirectResponse(url="/candidates", status_code=HTTP_302_FOUND)

# 회신자 리스트
@app.get("/replied-candidates", response_class=HTMLResponse)
async def replied_candidates(request: Request):
    db = SessionLocal()
    replied = db.query(MailLog).filter(MailLog.status == "replied").all()
    candidate_ids = [r.candidate_id for r in replied]
    candidates = db.query(Candidate).filter(Candidate.id.in_(candidate_ids)).all()
    db.close()
    return templates.TemplateResponse("replied_candidates.html", {
        "request": request,
        "replied_candidates": candidates,
        "current_page": "replied_candidates"
        
    })

# 새 채용 시작 화면
@app.get("/new-hiring", response_class=HTMLResponse)
async def new_hiring_page(request: Request):
    return templates.TemplateResponse("new_hiring.html", {
        "request": request,
        "current_page": "new_hiring"
    })

async def search_candidates(languages, regions, count):
    query_parts = []
    if languages:
        lang_query = " ".join([f"language:{lang}" for lang in languages])
        query_parts.append(lang_query)
    if regions:
        loc_query = " ".join([f"location:{region}" for region in regions])
        query_parts.append(loc_query)
    query = " ".join(query_parts)

    params = {"q": query, "per_page": count or 10}
    async with httpx.AsyncClient() as client:
        response = await client.get(GITHUB_API_URL, params=params, headers=GITHUB_HEADERS)
    data = response.json()

    candidates = []
    async with httpx.AsyncClient() as client:
        for item in data.get("items", []):
            # 개별 유저 상세 API 호출
            user_resp = await client.get(f"https://api.github.com/users/{item['login']}", headers=GITHUB_HEADERS)
            user_data = user_resp.json()
            email = user_data.get("email") or "N/A"

            candidates.append({
                "username": item["login"],
                "avatar_url": item["avatar_url"],
                "profile_url": item["html_url"],
                "score": item.get("score", 0),
                "email": email,
                "location": user_data.get("location") or "지역 미정",
                "languages": ", ".join(languages) if languages else "언어 미정"
            })
    return candidates

# 필터링 처리
@app.post("/filter-candidates", response_class=HTMLResponse)
async def filter_candidates(
    request: Request,
    languages: list[str] = Form([]),
    regions: list[str] = Form([]),
    all_region: str = Form(None),
    salary: int = Form(None),  # ✅ 선택적 파라미터로 변경
    total_count: int = Form(...)
):
    if all_region == "all":
        regions = ['서울','인천','경기','부산','대구','광주','대전','세종','울산','강원','충북','충남','전북','전남','경북','경남','제주']
    
    candidates = await search_candidates(languages, regions, total_count)

    return templates.TemplateResponse("candidates.html", {
        "request": request,
        "candidates": candidates,
        "current_page": "candidates",
        "salary": salary  # 필요시 템플릿 전달용
    })


@app.get("/past-records", response_class=HTMLResponse)
async def past_records_page(request: Request):
    past_records_data = [
        {"id": 1, "title": "2024 상반기 개발자 채용", "completed_date": "2024-03-10", "hired_count": 3, "required_skills": "Python, Django"},
        {"id": 2, "title": "2023 하반기 백엔드 채용", "completed_date": "2023-11-05", "hired_count": 2, "required_skills": "Java, Spring"}
    ]
    return templates.TemplateResponse("past_records.html", {
        "request": request,
        "past_records": past_records_data,
        "current_page": "past_records"
    })


