from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR
from app.database import get_db
from app.models.api_schema import ProceduralSubmitRequest
from app.services.grader import grade_numeric_detailed
from app.services.procedural_gen import generate_random_drill

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


@router.get("/drills", response_class=HTMLResponse)
async def drills_page(request: Request, drill_type: str = "unit_kmh_ms"):
    drill = generate_random_drill(drill_type)
    return templates.TemplateResponse(
        request=request,
        name="procedural_drill.html",
        context={"drill": drill, "current_type": drill_type},
    )


@router.get("/api/drills/new")
async def api_new_drill(drill_type: str = "unit_kmh_ms"):
    drill = generate_random_drill(drill_type)
    return JSONResponse(drill)


@router.post("/api/drills/submit")
async def api_submit_drill(req: ProceduralSubmitRequest):
    # Grade numeric answer with strict tolerance and unit checking
    is_correct, error_tag = grade_numeric_detailed(
        req.user_answer,
        req.expected_answer,
        tolerance=req.tolerance,
        expected_unit=req.expected_unit,
    )

    # Persist in SQLite
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO procedural_attempts (drill_type, question_stem, user_answer, expected_answer, is_correct, time_spent_sec)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                req.drill_type,
                req.question_stem,
                req.user_answer,
                req.expected_answer,
                1 if is_correct else 0,
                req.time_spent_sec,
            ),
        )

    return JSONResponse(
        {
            "is_correct": is_correct,
            "expected_answer": req.expected_answer,
            "user_answer": req.user_answer,
            "error_tag": error_tag,
        }
    )
