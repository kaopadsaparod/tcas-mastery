from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR
from app.services.learning_path import analyze_topic_readiness
from app.services.study_planner import get_daily_study_plan

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


@router.get("/planner", response_class=HTMLResponse)
async def planner_page(
    request: Request,
    minutes: int = Query(60, ge=20, le=180),
    exam: str = Query("alevel"),
):
    plan = get_daily_study_plan(daily_minutes=minutes, target_exam=exam)
    return templates.TemplateResponse(
        request=request,
        name="planner.html",
        context={"plan": plan, "minutes": minutes, "exam": exam},
    )


@router.get("/api/planner")
async def api_get_plan(
    minutes: int = Query(60, ge=20, le=180),
    exam: str = Query("alevel"),
):
    plan = get_daily_study_plan(daily_minutes=minutes, target_exam=exam)
    return JSONResponse(plan)


@router.get("/api/learning-path/readiness/{topic_id}")
async def api_topic_readiness(topic_id: str):
    readiness = analyze_topic_readiness(topic_id)
    return JSONResponse(readiness)
