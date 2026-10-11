from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR
from app.services.pdf_importer import (
    process_uploaded_image,
    process_uploaded_pdf,
    save_custom_question,
)
from app.services.roadmap_service import get_roadmap_topics

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


@router.get("/import", response_class=HTMLResponse)
async def import_studio_page(request: Request):
    roadmap_topics = get_roadmap_topics()
    return templates.TemplateResponse(
        request=request,
        name="import_studio.html",
        context={"roadmap_topics": roadmap_topics},
    )


@router.post("/api/import/upload")
async def api_upload_exam_file(file: UploadFile = File(...)):
    filename = file.filename or "exam_file"
    ext = filename.lower().split(".")[-1]
    content_bytes = await file.read()

    try:
        if ext == "pdf":
            result = process_uploaded_pdf(content_bytes, filename)
        elif ext in ["png", "jpg", "jpeg", "webp"]:
            result = process_uploaded_image(content_bytes, filename)
        else:
            raise HTTPException(
                status_code=400,
                detail="รองรับเฉพาะไฟล์ PDF และไฟล์รูปภาพ (PNG, JPG, WEBP)",
            )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(result)


@router.post("/api/import/create-question")
async def api_create_question(req: Request):
    payload = await req.json()
    try:
        new_q = save_custom_question(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(
        {
            "success": True,
            "question_id": new_q.id,
            "message": f"บันทึกข้อสอบ {new_q.id} เข้าสู่คลังโจทย์เรียบร้อยแล้ว",
        }
    )
