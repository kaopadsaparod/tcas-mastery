from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR
from app.services.review_engine import get_due_reviews, get_learning_stats

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


@router.get("/stats", response_class=HTMLResponse)
async def stats_page(request: Request, verified_only: bool = False):
    stats = get_learning_stats(verified_only=verified_only)
    due_reviews = get_due_reviews()
    return templates.TemplateResponse(
        request=request,
        name="stats.html",
        context={
            "stats": stats,
            "due_reviews": due_reviews,
            "verified_only": verified_only,
        },
    )


@router.get("/api/stats")
async def api_stats(verified_only: bool = False):
    return JSONResponse(get_learning_stats(verified_only=verified_only))
