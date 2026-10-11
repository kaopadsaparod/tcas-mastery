from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR
from app.models.api_schema import AnswerSheetSubmitRequest
from app.services.answer_sheet import grade_answer_sheet
from app.services.content_loader import content_loader

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


@router.get("/answer-sheet", response_class=HTMLResponse)
async def answer_sheet_index(request: Request):
    papers = content_loader.get_all_past_papers()
    return templates.TemplateResponse(
        request=request, name="answer_sheet_list.html", context={"papers": papers}
    )


@router.get("/answer-sheet/{paper_id}", response_class=HTMLResponse)
async def answer_sheet_detail(request: Request, paper_id: str):
    paper = content_loader.get_past_paper_by_id(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return templates.TemplateResponse(
        request=request, name="answer_sheet.html", context={"paper": paper}
    )


@router.post("/api/answer-sheet/submit")
async def api_submit_answer_sheet(req: AnswerSheetSubmitRequest):
    paper = content_loader.get_past_paper_by_id(req.paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    result = grade_answer_sheet(paper, req.answers, req.time_taken_min)
    return JSONResponse(result.model_dump())
