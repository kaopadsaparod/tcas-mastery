from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR
from app.services.backup_service import (
    check_db_integrity,
    create_backup,
    delete_backup,
    list_backups,
)

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


@router.get("/system", response_class=HTMLResponse)
async def system_page(request: Request):
    backups = list_backups()
    integrity = check_db_integrity()
    return templates.TemplateResponse(
        request=request,
        name="system.html",
        context={"backups": backups, "integrity": integrity},
    )


@router.post("/api/backup/create")
async def api_create_backup():
    file_path = create_backup()
    return JSONResponse(
        {"success": True, "filename": file_path.name, "path": str(file_path)}
    )


@router.post("/api/backup/delete")
async def api_delete_backup(req: Request):
    payload = await req.json()
    filename = payload.get("filename")
    if not filename:
        return JSONResponse({"success": False, "error": "Missing filename"}, status_code=400)
    success = delete_backup(filename)
    return JSONResponse({"success": success})


@router.get("/api/backup/list")
async def api_list_backups():
    return JSONResponse(list_backups())


@router.get("/api/system/integrity")
async def api_check_integrity():
    return JSONResponse(check_db_integrity())
