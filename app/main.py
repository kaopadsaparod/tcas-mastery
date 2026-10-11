import ipaddress
import urllib.parse
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import (
    ALLOWED_HOSTS,
    APP_HOST,
    APP_PORT,
    ASSETS_DIR,
    BASE_DIR,
    DATA_DIR,
    TCAS_ACCESS_PIN,
)
from app.database import init_db
from app.routers.answer_sheet import router as answer_sheet_router
from app.routers.content_audit import router as content_audit_router
from app.routers.drills import router as drills_router
from app.routers.formulas import router as formulas_router
from app.routers.import_studio import router as import_studio_router
from app.routers.mock_exam import router as mock_exam_router
from app.routers.planner import router as planner_router
from app.routers.practice import router as practice_router
from app.routers.progress import router as progress_router
from app.routers.roadmap import router as roadmap_router
from app.routers.stats import router as stats_router
from app.routers.system import router as system_router
from app.services.content_loader import content_loader
from app.services.review_engine import get_due_reviews, get_learning_stats


def is_allowed_host(host_str: str) -> bool:
    """
    Validates Host, Origin, and Referer headers against allowed domains and private LAN ranges.
    Protects against DNS Rebinding and CSRF attacks.
    """
    if not host_str:
        return True
    host_only = host_str.split(":")[0].strip().lower()
    if "*" in ALLOWED_HOSTS:
        return True
    if host_only in ["localhost", "127.0.0.1", "testserver", "::1"]:
        return True
    for allowed in ALLOWED_HOSTS:
        if allowed.lower() == host_only:
            return True
        if allowed.startswith("*.") and host_only.endswith(allowed[1:]):
            return True
    # Allow standard private RFC 1918 LAN addresses (for tablet access over home Wi-Fi)
    try:
        ip = ipaddress.ip_address(host_only)
        if ip.is_private or ip.is_loopback:
            return True
    except ValueError:
        pass
    return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure DB tables and reload content
    init_db()
    content_loader.reload()
    yield
    # Shutdown


app = FastAPI(
    title="TCAS Mastery Prep System",
    description="Local-First Deterministic TCAS Examination Prep System",
    version="1.0.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def security_and_csrf_middleware(request: Request, call_next):
    # 1. DNS Rebinding protection: Verify Host header
    host_header = request.headers.get("host", "")
    if host_header and not is_allowed_host(host_header):
        return JSONResponse(
            {"detail": f"Forbidden: Untrusted Host header '{host_header}'"},
            status_code=400,
        )

    # 2. CSRF & Origin validation on state-mutating requests
    if request.method in ("POST", "PUT", "DELETE", "PATCH"):
        origin = request.headers.get("origin")
        referer = request.headers.get("referer")

        if origin:
            parsed_origin = urllib.parse.urlparse(origin)
            origin_host = parsed_origin.hostname or ""
            if not is_allowed_host(origin_host):
                return JSONResponse(
                    {"detail": "Forbidden: Cross-origin request blocked (CSRF)"},
                    status_code=403,
                )
        elif referer:
            parsed_referer = urllib.parse.urlparse(referer)
            referer_host = parsed_referer.hostname or ""
            if not is_allowed_host(referer_host):
                return JSONResponse(
                    {"detail": "Forbidden: Untrusted referer header (CSRF)"},
                    status_code=403,
                )

        # 3. Optional LAN PIN verification on sensitive mutation endpoints
        if TCAS_ACCESS_PIN and request.url.path in [
            "/api/backup/delete",
            "/api/backup/create",
            "/api/backup/restore",
            "/api/import/upload",
            "/api/import/create-question",
        ]:
            client_pin = request.headers.get("x-tcas-pin") or request.query_params.get("pin")
            if client_pin != TCAS_ACCESS_PIN:
                return JSONResponse(
                    {"detail": "Unauthorized: Invalid or missing TCAS PIN"},
                    status_code=401,
                )

    response = await call_next(request)
    # Security response headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    return response


# Static and Assets
static_dir = BASE_DIR / "app" / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

ASSETS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

templates_dir = BASE_DIR / "app" / "templates"
templates_dir.mkdir(parents=True, exist_ok=True)
templates = Jinja2Templates(directory=str(templates_dir))

# Include Routers
app.include_router(practice_router)
app.include_router(drills_router)
app.include_router(formulas_router)
app.include_router(answer_sheet_router)
app.include_router(stats_router)
app.include_router(system_router)
app.include_router(import_studio_router)
app.include_router(roadmap_router)
app.include_router(planner_router)
app.include_router(mock_exam_router)
app.include_router(content_audit_router)
app.include_router(progress_router)


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    stats = get_learning_stats()
    due_reviews = get_due_reviews()
    total_questions = len(content_loader.get_all_questions())
    total_formulas = len(content_loader.get_all_formulas())
    total_papers = len(content_loader.get_all_past_papers())

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "stats": stats,
            "due_reviews": due_reviews,
            "total_questions": total_questions,
            "total_formulas": total_formulas,
            "total_papers": total_papers,
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=APP_HOST, port=APP_PORT, reload=True)
