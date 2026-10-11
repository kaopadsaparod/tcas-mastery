from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.config import BASE_DIR
from app.database import get_db
from app.services.roadmap_service import (
    add_custom_topic,
    get_exam_countdown,
    get_roadmap_topics,
    reorder_topic_priority,
    update_topic_priority,
)

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


class UpdatePriorityRequest(BaseModel):
    topic_id: str
    priority_level: int
    order_index: int | None = None
    target_score_pct: float = 80.0
    notes: str | None = None


class AddTopicRequest(BaseModel):
    topic_id: str
    subject: str
    topic_name: str
    priority_level: int = 1
    target_score_pct: float = 80.0
    notes: str = ""


class ReorderRequest(BaseModel):
    topic_id: str
    direction: str  # 'up' or 'down'


class ExamDateUpdateRequest(BaseModel):
    tpat_date: str
    alevel_date: str


@router.get("/roadmap", response_class=HTMLResponse)
async def roadmap_page(request: Request):
    topics = get_roadmap_topics()
    countdown = get_exam_countdown()
    return templates.TemplateResponse(
        request=request,
        name="roadmap.html",
        context={"topics": topics, "countdown": countdown},
    )


@router.post("/api/roadmap/update-priority")
async def api_update_priority(req: UpdatePriorityRequest):
    update_topic_priority(
        topic_id=req.topic_id,
        priority_level=req.priority_level,
        order_index=req.order_index,
        target_score_pct=req.target_score_pct,
        notes=req.notes,
    )
    return JSONResponse({"success": True})


@router.post("/api/roadmap/add-topic")
async def api_add_topic(req: AddTopicRequest):
    add_custom_topic(
        topic_id=req.topic_id,
        subject=req.subject,
        topic_name=req.topic_name,
        priority_level=req.priority_level,
        target_score_pct=req.target_score_pct,
        notes=req.notes,
    )
    return JSONResponse({"success": True})


@router.post("/api/roadmap/reorder")
async def api_reorder_topic(req: ReorderRequest):
    reorder_topic_priority(req.topic_id, req.direction)
    return JSONResponse({"success": True})


@router.post("/api/roadmap/update-exam-dates")
async def api_update_exam_dates(req: ExamDateUpdateRequest):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO app_settings (key, value) VALUES ('tpat_exam_date', ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """,
            (req.tpat_date,),
        )
        cursor.execute(
            """
            INSERT INTO app_settings (key, value) VALUES ('alevel_exam_date', ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """,
            (req.alevel_date,),
        )
    return JSONResponse({"success": True})
