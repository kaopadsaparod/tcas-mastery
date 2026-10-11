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


@router.post("/api/backup/restore")
async def api_restore_backup(req: Request):
    payload = await req.json()
    filename = payload.get("filename")
    if not filename:
        return JSONResponse({"success": False, "error": "Missing filename"}, status_code=400)
    from app.services.backup_service import restore_backup
    res = restore_backup(filename)
    status_code = 200 if res.get("success") else 400
    return JSONResponse(res, status_code=status_code)


@router.post("/api/backup/verify")
async def api_verify_backup(req: Request):
    payload = await req.json()
    filename = payload.get("filename")
    if not filename:
        return JSONResponse({"valid": False, "error": "Missing filename"}, status_code=400)
    from app.config import BACKUPS_DIR
    from app.services.backup_service import verify_backup_file
    p = BACKUPS_DIR / filename
    res = verify_backup_file(p)
    return JSONResponse(res)


@router.get("/api/system/integrity")
async def api_check_integrity():
    return JSONResponse(check_db_integrity())
