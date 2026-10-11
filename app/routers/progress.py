from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR
from app.services.progress_service import get_progress_report

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


@router.get("/progress", response_class=HTMLResponse)
async def progress_page(request: Request):
    report = get_progress_report()
    return templates.TemplateResponse(
        request=request,
        name="progress.html",
        context={"report": report},
    )


@router.get("/api/progress", response_class=JSONResponse)
async def api_progress():
    report = get_progress_report()
    return JSONResponse(report)
