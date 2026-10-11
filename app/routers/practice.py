from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR
from app.database import get_db
from app.models.api_schema import SubmitAttemptRequest
from app.services.ai_helper import (
    generate_ai_tutor_prompt,
    generate_presolve_hint_prompt,
)
from app.services.content_loader import content_loader
from app.services.grader import grade_attempt
from app.services.review_engine import (
    evaluate_pace,
    get_interleaved_questions,
    record_attempt,
)

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


@router.get("/practice", response_class=HTMLResponse)
async def practice_index(
    request: Request,
    subject: str = None,
    topic: str = None,
    bookmarked_only: bool = False,
    verified_only: bool = False,
):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT question_id FROM bookmarks")
        bookmarked_ids = {row["question_id"] for row in cursor.fetchall()}

    questions = content_loader.get_all_questions(verified_only=verified_only)
    if subject:
        questions = [q for q in questions if q.subject == subject]
    if topic:
        questions = [q for q in questions if q.topic == topic]
    if bookmarked_only:
        questions = [q for q in questions if q.id in bookmarked_ids]

    topics = sorted(list(set(q.topic for q in content_loader.get_all_questions())))
    return templates.TemplateResponse(
        request=request,
        name="practice_list.html",
        context={
            "questions": questions,
            "topics": topics,
            "current_subject": subject or "",
            "current_topic": topic or "",
            "bookmarked_only": bookmarked_only,
            "bookmarked_ids": bookmarked_ids,
            "verified_only": verified_only,
            "is_interleaved": False,
        },
    )


@router.get("/practice/interleaved", response_class=HTMLResponse)
async def practice_interleaved(
    request: Request, limit: int = 15, verified_only: bool = False
):
    """Interleaved Practice: Rapidly alternates across subjects/topics to prevent cognitive blocking."""
    questions = get_interleaved_questions(limit=limit, verified_only=verified_only)
    topics = sorted(list(set(q.topic for q in content_loader.get_all_questions())))
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT question_id FROM bookmarks")
        bookmarked_ids = {row["question_id"] for row in cursor.fetchall()}

    return templates.TemplateResponse(
        request=request,
        name="practice_list.html",
        context={
            "questions": questions,
            "topics": topics,
            "current_subject": "interleaved",
            "current_topic": "",
            "bookmarked_only": False,
            "bookmarked_ids": bookmarked_ids,
            "verified_only": verified_only,
            "is_interleaved": True,
        },
    )


@router.get("/practice/{question_id}", response_class=HTMLResponse)
async def practice_question(request: Request, question_id: str):
    q = content_loader.get_question_by_id(question_id)
    if not q:
        raise HTTPException(status_code=404, detail="ไม่พบข้อสอบข้อนี้")

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM bookmarks WHERE question_id = ?", (question_id,)
        )
        is_bookmarked = cursor.fetchone() is not None

    presolve_prompt = generate_presolve_hint_prompt(q)

    return templates.TemplateResponse(
        request=request,
        name="practice.html",
        context={
            "q": q,
            "is_bookmarked": is_bookmarked,
            "presolve_prompt": presolve_prompt,
        },
    )


@router.post("/api/bookmark/toggle")
async def api_toggle_bookmark(req: Request):
    payload = await req.json()
    qid = payload.get("question_id")
    if not qid:
        raise HTTPException(status_code=400, detail="Missing question_id")

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT question_id FROM bookmarks WHERE question_id = ?", (qid,))
        row = cursor.fetchone()
        if row:
            cursor.execute("DELETE FROM bookmarks WHERE question_id = ?", (qid,))
            bookmarked = False
        else:
            cursor.execute("INSERT INTO bookmarks (question_id) VALUES (?)", (qid,))
            bookmarked = True

    return JSONResponse({"question_id": qid, "bookmarked": bookmarked})


@router.get("/api/ai-prompt/presolve/{question_id}")
async def api_presolve_prompt(question_id: str):
    q = content_loader.get_question_by_id(question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    prompt = generate_presolve_hint_prompt(q)
    return JSONResponse({"prompt": prompt})


@router.post("/api/submit-attempt")
async def api_submit_attempt(req: SubmitAttemptRequest):
    q = content_loader.get_question_by_id(req.question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    grade_result = grade_attempt(
        question=q,
        user_answer=req.user_answer,
        hints_opened=req.hints_opened,
        confidence=req.confidence,
        plan_step_answer=req.plan_step_answer,
    )

    # Evaluate A-Level / TPAT3 Pace
    pace_info = evaluate_pace(q.subject, req.time_spent_sec)
    grade_result.pace_status = pace_info["pace_status"]
    grade_result.pace_target_sec = pace_info["pace_target_sec"]
    grade_result.pace_feedback = pace_info["pace_feedback"]

    # Persist in SQLite and update Spaced Repetition queue
    queue_record = record_attempt(
        question_id=q.id,
        subject=q.subject,
        topic=q.topic,
        user_answer=req.user_answer,
        is_correct=grade_result.is_correct,
        status=grade_result.status,
        confidence=req.confidence,
        hints_opened=req.hints_opened,
        plan_step_answer=req.plan_step_answer,
        plan_step_correct=grade_result.plan_step_correct,
        error_tag=grade_result.error_tag,
        time_spent_sec=req.time_spent_sec,
        review_time_sec=req.review_time_sec,
    )

    # Synchronize actual spaced repetition interval from queue database
    grade_result.next_review_interval_days = queue_record["interval_days"]

    # Generate AI copy prompt
    ai_prompt = generate_ai_tutor_prompt(
        question=q, user_answer=req.user_answer, error_tag=grade_result.error_tag
    )

    res_dict = grade_result.model_dump()
    res_dict["next_review_interval_days"] = queue_record["interval_days"]
    res_dict["next_review_at"] = queue_record["next_review_at"]
    res_dict["queue_priority"] = queue_record["priority"]
    res_dict["ai_prompt"] = ai_prompt
    return JSONResponse(res_dict)
