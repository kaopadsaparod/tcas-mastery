from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.config import BASE_DIR
from app.services.mock_exam import (
    EXAM_BLUEPRINTS,
    get_mock_exam_history,
    get_mock_exam_session,
    save_mock_exam_progress,
    start_mock_exam,
    submit_mock_exam,
)

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


class StartExamRequest(BaseModel):
    exam_type: str = "alevel_physics"


class SaveProgressRequest(BaseModel):
    answers: dict[str, str]
    flagged: list[int]
    time_spent_min: float = 0.0


class SubmitExamRequest(BaseModel):
    answers: dict[str, str]
    time_spent_min: float = 0.0


@router.get("/mock-exam", response_class=HTMLResponse)
async def mock_exam_landing_page(request: Request):
    history = get_mock_exam_history()
    return templates.TemplateResponse(
        request=request,
        name="mock_exam_landing.html",
        context={"blueprints": EXAM_BLUEPRINTS, "history": history},
    )


@router.post("/api/mock-exam/start")
async def api_start_mock_exam(req: StartExamRequest):
    session_data = start_mock_exam(req.exam_type)
    return JSONResponse(session_data)


@router.get("/mock-exam/{session_id}", response_class=HTMLResponse)
async def mock_exam_active_page(request: Request, session_id: str):
    sess = get_mock_exam_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Mock exam session not found")

    if sess["status"] == "completed":
        # Redirect to report
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=f"/mock-exam/{session_id}/report")

    # Load questions without answers
    from app.services.mock_exam import start_mock_exam
    blueprint = EXAM_BLUEPRINTS.get(sess["exam_type"], EXAM_BLUEPRINTS["alevel_physics"])

    # Load question data for this session
    from app.services.content_loader import content_loader
    past_papers = content_loader.get_past_papers_by_subject(blueprint["subject"])
    questions = []
    if past_papers:
        paper = past_papers[0]
        for q in paper.questions:
            full_q = content_loader.get_question_by_id(f"phy-kin-000{q.number}")
            stem = full_q.stem if full_q else f"ข้อสอบข้อที่ {q.number} ({q.topic})"
            opts = []
            if full_q and full_q.answer.options:
                opts = [{"id": o.id, "text": o.text} for o in full_q.answer.options]
            elif (q.answer_type or "single_choice") == "single_choice":
                opts = [{"id": str(x), "text": f"ตัวเลือก {x}"} for x in range(1, 6)]

            ans_type = q.answer_type or ("single_choice" if str(q.correct_answer) in {"1", "2", "3", "4", "5"} else "numeric")
            questions.append({
                "number": q.number,
                "stem": stem,
                "topic": q.topic,
                "skill": q.skill,
                "answer_type": ans_type,
                "options": opts,
                "score": q.score,
                "unit": q.unit,
            })

    return templates.TemplateResponse(
        request=request,
        name="mock_exam_active.html",
        context={"session": sess, "blueprint": blueprint, "questions": questions},
    )


@router.post("/api/mock-exam/{session_id}/save")
async def api_save_progress(session_id: str, req: SaveProgressRequest):
    ok = save_mock_exam_progress(
        session_id=session_id,
        answers=req.answers,
        flagged=req.flagged,
        time_spent_min=req.time_spent_min,
    )
    return JSONResponse({"success": ok})


@router.post("/api/mock-exam/{session_id}/submit")
async def api_submit_mock_exam(session_id: str, req: SubmitExamRequest):
    report = submit_mock_exam(
        session_id=session_id,
        answers=req.answers,
        time_spent_min=req.time_spent_min,
    )
    return JSONResponse({"success": True, "report": report})


@router.get("/mock-exam/{session_id}/report", response_class=HTMLResponse)
async def mock_exam_report_page(request: Request, session_id: str):
    sess = get_mock_exam_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Mock exam session not found")

    report = sess.get("report") or {}
    return templates.TemplateResponse(
        request=request,
        name="mock_exam_report.html",
        context={"session": sess, "report": report},
    )
