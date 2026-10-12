from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR
from app.database import get_db
from app.models.api_schema import FormulaRecallSubmitRequest
from app.services.content_loader import content_loader

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


@router.get("/formulas", response_class=HTMLResponse)
async def formulas_page(request: Request, subject: str | None = None):
    all_formulas = content_loader.get_all_formulas()
    physics_count = sum(1 for f in all_formulas if f.subject == "physics")
    math_count = sum(1 for f in all_formulas if f.subject == "math")

    if subject in ["physics", "math"]:
        filtered_formulas = [f for f in all_formulas if f.subject == subject]
    else:
        filtered_formulas = all_formulas
        subject = "all"

    return templates.TemplateResponse(
        request=request,
        name="formula_recall.html",
        context={
            "formulas": filtered_formulas,
            "all_formulas": all_formulas,
            "selected_subject": subject,
            "total_count": len(all_formulas),
            "physics_count": physics_count,
            "math_count": math_count,
        },
    )


@router.post("/api/formulas/submit")
async def api_submit_formula_recall(req: FormulaRecallSubmitRequest):
    card = content_loader.get_formula_by_id(req.formula_id)
    if not card or req.question_index >= len(card.recall_questions):
        raise HTTPException(status_code=404, detail="Formula or question not found")

    q = card.recall_questions[req.question_index]
    is_correct = req.user_answer.strip().lower() == q["answer"].strip().lower()

    from datetime import datetime, timedelta, timezone

    now = datetime.now(timezone.utc)
    interval_days = 3 if is_correct else 1
    next_review_at = (now + timedelta(days=interval_days)).strftime("%Y-%m-%d %H:%M:%S")

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO formula_reviews (formula_id, subject, correct_count, wrong_count, next_review_at, last_reviewed_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(formula_id) DO UPDATE SET
                correct_count = correct_count + ?,
                wrong_count = wrong_count + ?,
                next_review_at = excluded.next_review_at,
                last_reviewed_at = CURRENT_TIMESTAMP
        """,
            (
                card.id,
                card.subject,
                1 if is_correct else 0,
                0 if is_correct else 1,
                next_review_at,
                1 if is_correct else 0,
                0 if is_correct else 1,
            ),
        )

    return JSONResponse(
        {
            "is_correct": is_correct,
            "correct_answer": q["answer"],
            "explanation": q.get("explanation", ""),
        }
    )
