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
    from app.services.study_planner import get_study_session_history
    history = get_study_session_history(limit=5)
    return templates.TemplateResponse(
        request=request,
        name="planner.html",
        context={"plan": plan, "minutes": minutes, "exam": exam, "history": history},
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


from pydantic import BaseModel
from typing import Any, Optional


class StartSessionRequest(BaseModel):
    target_exam: str = "alevel"
    daily_minutes: int = 60
    planned_minutes: Optional[int] = None
    blocks: Optional[list[dict[str, Any]]] = None


class LogBlockRequest(BaseModel):
    session_id: str
    block_id: Optional[str] = None
    block_index: Optional[int] = None
    time_spent_min: float = 0.0
    status: str = "completed"
    action: Optional[str] = None
    notes: str = ""


class FinishSessionRequest(BaseModel):
    session_id: str
    actual_minutes: Optional[float] = None
    notes: str = ""


@router.post("/api/planner/session/start")
@router.post("/planner/session/start")
async def api_start_session(req: StartSessionRequest):
    from app.services.study_planner import start_study_session
    res = start_study_session(
        target_exam=req.target_exam,
        daily_minutes=req.daily_minutes,
        planned_minutes=req.planned_minutes,
        blocks=req.blocks,
    )
    return JSONResponse(res)


@router.post("/api/planner/block/log")
async def api_log_block(req: LogBlockRequest):
    from app.services.study_planner import log_study_block
    res = log_study_block(
        session_id=req.session_id,
        block_id=req.block_id,
        block_index=req.block_index,
        time_spent_min=req.time_spent_min,
        status=req.status,
        action=req.action,
        notes=req.notes,
    )
    return JSONResponse(res)


@router.post("/planner/session/block/complete")
async def api_complete_block(req: LogBlockRequest):
    from app.services.study_planner import log_study_block
    res = log_study_block(
        session_id=req.session_id,
        block_id=req.block_id,
        block_index=req.block_index,
        time_spent_min=req.time_spent_min,
        status="completed",
        action="completed",
        notes=req.notes,
    )
    return JSONResponse(res)


@router.post("/planner/session/block/skip")
async def api_skip_block(req: LogBlockRequest):
    from app.services.study_planner import log_study_block
    res = log_study_block(
        session_id=req.session_id,
        block_id=req.block_id,
        block_index=req.block_index,
        time_spent_min=req.time_spent_min,
        status="skipped",
        action="skipped",
        notes=req.notes,
    )
    return JSONResponse(res)


@router.post("/api/planner/session/finish")
@router.post("/planner/session/finish")
async def api_finish_session(req: FinishSessionRequest):
    from app.services.study_planner import finish_study_session
    res = finish_study_session(
        session_id=req.session_id,
        notes=req.notes,
        actual_minutes=req.actual_minutes,
    )
    return JSONResponse(res)


@router.get("/api/planner/history")
@router.get("/planner/session/history")
async def api_planner_history():
    from app.services.study_planner import get_study_session_history
    history = get_study_session_history()
    return JSONResponse({"history": history})
