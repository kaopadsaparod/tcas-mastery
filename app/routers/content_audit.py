from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR
from app.services.content_audit import get_content_audit_report

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


@router.get("/audit/content", response_class=HTMLResponse)
async def content_audit_page(request: Request):
    report = get_content_audit_report()
    return templates.TemplateResponse(
        request=request,
        name="content_audit.html",
        context={"audit": report},
    )


@router.get("/api/audit/content", response_class=JSONResponse)
async def api_content_audit():
    report = get_content_audit_report()
    return JSONResponse(report)
