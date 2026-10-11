import os
import re
import threading
import uuid
from pathlib import Path
from typing import Any

import pymupdf
import yaml

from app.config import CONTENT_DIR, DATA_DIR
from app.database import get_db
from app.models.content_schema import (
    AnswerConfig,
    ChoiceOption,
    FullSolution,
    Hint,
    Question,
    SkillInfo,
    SolutionStep,
    SourceInfo,
    VerificationInfo,
)
from app.services.content_loader import content_loader

SOURCES_DIR = DATA_DIR / "sources"
ASSETS_DIR = DATA_DIR / "assets"
PAGES_DIR = ASSETS_DIR / "pages"
IMPORTED_CONTENT_DIR = CONTENT_DIR / "imported"

# Ensure directories exist
SOURCES_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
PAGES_DIR.mkdir(parents=True, exist_ok=True)
IMPORTED_CONTENT_DIR.mkdir(parents=True, exist_ok=True)

MAX_UPLOAD_SIZE = 25 * 1024 * 1024  # 25 MB max upload
MAX_PDF_PAGES = 50  # Prevent PDF bombs
IMAGE_URL_REGEX = re.compile(
    r"^/static/assets/pages/[a-zA-Z0-9_\-\.]+\.(png|jpg|jpeg|webp)$"
)

_yaml_lock = threading.Lock()


def validate_pdf_bytes(file_bytes: bytes) -> None:
    if len(file_bytes) > MAX_UPLOAD_SIZE:
        raise ValueError(f"ไฟล์มีขนาดใหญ่เกินกำหนด (สูงสุด {MAX_UPLOAD_SIZE // (1024 * 1024)} MB)")
    if not file_bytes.startswith(b"%PDF"):
        raise ValueError("ไฟล์ PDF ไม่ถูกต้อง (Magic bytes mismatch)")


def validate_image_bytes(file_bytes: bytes, ext: str) -> None:
    if len(file_bytes) > MAX_UPLOAD_SIZE:
        raise ValueError(f"ไฟล์มีขนาดใหญ่เกินกำหนด (สูงสุด {MAX_UPLOAD_SIZE // (1024 * 1024)} MB)")
    
    clean_ext = ext.lower().strip()
    if clean_ext == ".png" and not file_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("ไฟล์ PNG ไม่ถูกต้อง (Magic bytes mismatch)")
    elif clean_ext in [".jpg", ".jpeg"] and not file_bytes.startswith(b"\xff\xd8\xff"):
        raise ValueError("ไฟล์ JPEG ไม่ถูกต้อง (Magic bytes mismatch)")
    elif clean_ext == ".webp" and not (file_bytes.startswith(b"RIFF") and file_bytes[8:12] == b"WEBP"):
        raise ValueError("ไฟล์ WEBP ไม่ถูกต้อง (Magic bytes mismatch)")


def process_uploaded_pdf(file_bytes: bytes, original_filename: str) -> dict[str, Any]:
    """
    Saves an uploaded PDF with UUID-only filename, enforces page limits,
    extracts embedded text layer first, and renders page previews.
    """
    validate_pdf_bytes(file_bytes)

    # Use pure UUID for filesystem storage (never trust client filename in path)
    file_id = uuid.uuid4().hex[:12]
    safe_filename = f"{file_id}.pdf"
    pdf_path = SOURCES_DIR / safe_filename

    with open(pdf_path, "wb") as f:
        f.write(file_bytes)

    doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    page_count = len(doc)
    if page_count > MAX_PDF_PAGES:
        # Cleanup saved file on error
        pdf_path.unlink(missing_ok=True)
        raise ValueError(f"เอกสารมีจำนวนหน้า ({page_count} หน้า) เกินขีดจำกัดที่ปลอดภัย ({MAX_PDF_PAGES} หน้า)")

    pages_data: list[dict[str, Any]] = []

    for i in range(page_count):
        page = doc[i]
        # Text layer extracted first (offline and CPU-light)
        text_content = page.get_text()

        # Render pixmap with reasonable DPI
        pix = page.get_pixmap(dpi=150)
        img_name = f"{file_id}_page_{i + 1}.png"
        img_path = PAGES_DIR / img_name
        pix.save(str(img_path))

        pages_data.append(
            {
                "page_number": i + 1,
                "image_url": f"/static/assets/pages/{img_name}",
                "text_snippet": text_content[:500].strip() if text_content else "",
                "has_text_layer": bool(text_content and text_content.strip()),
            }
        )

    # Record in database (storing human readable original name for UI display)
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO imported_files (filename, original_name, file_type, file_path, page_count)
            VALUES (?, ?, ?, ?, ?)
        """,
            (safe_filename, Path(original_filename).name, "pdf", str(pdf_path), page_count),
        )

    return {
        "file_id": file_id,
        "filename": safe_filename,
        "original_filename": original_filename,
        "page_count": page_count,
        "pages": pages_data,
    }


def process_uploaded_image(file_bytes: bytes, original_filename: str) -> dict[str, Any]:
    """
    Saves an uploaded exam image (PNG, JPG, WEBP) directly into assets using UUID filename.
    """
    ext = Path(original_filename).suffix.lower()
    if ext not in [".png", ".jpg", ".jpeg", ".webp"]:
        ext = ".png"

    validate_image_bytes(file_bytes, ext)

    file_id = uuid.uuid4().hex[:12]
    img_name = f"{file_id}{ext}"
    img_path = PAGES_DIR / img_name

    with open(img_path, "wb") as f:
        f.write(file_bytes)

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO imported_files (filename, original_name, file_type, file_path, page_count)
            VALUES (?, ?, ?, ?, ?)
        """,
            (img_name, Path(original_filename).name, "image", str(img_path), 1),
        )

    return {
        "file_id": file_id,
        "filename": img_name,
        "original_filename": original_filename,
        "page_count": 1,
        "pages": [
            {
                "page_number": 1,
                "image_url": f"/static/assets/pages/{img_name}",
                "text_snippet": "(รูปภาพข้อสอบ)",
                "has_text_layer": False,
            }
        ],
    }


def save_custom_question(data: dict[str, Any]) -> Question:
    """
    Saves a new question created from an imported PDF/image into the YAML question bank.
    Uses threading lock and atomic temp file replace to avoid race conditions and file corruption.
    """
    target_yaml = IMPORTED_CONTENT_DIR / "custom_questions.yaml"

    # Validate image_url if provided
    image_url = data.get("image_url")
    if image_url:
        image_url = image_url.strip()
        if not IMAGE_URL_REGEX.match(image_url):
            raise ValueError(f"Invalid image_url format: {image_url}")

    qid = data.get("id") or f"custom-{uuid.uuid4().hex[:6]}"
    subject = data.get("subject", "physics")
    topic = data.get("topic", "physics.kinematics.1d")
    stem = data.get("stem", "").strip()

    # Options
    raw_options = data.get("options", [])
    correct_opt_id = str(data.get("correct_option", "o1"))
    options_list = []
    for opt in raw_options:
        opt_id = opt.get("id", "o1")
        options_list.append(
            ChoiceOption(
                id=opt_id,
                text=opt.get("text", ""),
                correct=(opt_id == correct_opt_id),
                error_tag=opt.get("error_tag"),
                explanation=opt.get("explanation"),
            )
        )

    # If numeric answer
    ans_type = data.get("answer_type", "single_choice")
    if ans_type == "numeric":
        ans_config = AnswerConfig(
            type="numeric",
            correct_value=data.get("numeric_value", 0),
            unit=data.get("unit", ""),
        )
    else:
        ans_config = AnswerConfig(type="single_choice", options=options_list)

    # Hints
    hints_list = []
    for h in data.get("hints", []):
        hints_list.append(Hint(level=h.get("level", 1), text=h.get("text", "")))
    if not hints_list:
        hints_list = [
            Hint(level=1, text="ทบทวนข้อมูลที่โจทย์กำหนดและสิ่งที่ต้องหา"),
            Hint(level=2, text="เลือกสูตรและพิจารณาเครื่องหมายให้ถูกต้อง"),
        ]

    # Solution
    solution_text = data.get("solution_summary", "เฉลยสำหรับข้อสอบข้อนี้")
    full_sol = FullSolution(
        steps=[SolutionStep(id="s1", text=solution_text)], summary=solution_text
    )

    new_q = Question(
        id=qid,
        subject=subject,
        topic=topic,
        source=SourceInfo(
            type="exam_prep", label=data.get("source_label", "ข้อสอบนำเข้าจาก PDF/โซเชียล")
        ),
        verification=VerificationInfo(
            tier=data.get("verification_tier", "D"),
            verified_by=data.get("verified_by", "user_imported"),
            notes=data.get("notes", "นำเข้าผ่านระบบ Web Import Studio (รอการตรวจสอบ)"),
        ),
        skills=SkillInfo(
            primary=data.get("primary_skill", "general_problem_solving"), secondary=[]
        ),
        stem=stem,
        image_url=image_url,
        answer=ans_config,
        hints=hints_list,
        solution=full_sol,
    )

    q_dict = new_q.model_dump(exclude_none=True)

    with _yaml_lock:
        existing_items = []
        if target_yaml.exists():
            with open(target_yaml, "r", encoding="utf-8") as f:
                loaded = yaml.safe_load(f)
                if isinstance(loaded, list):
                    existing_items = loaded

        existing_items.append(q_dict)

        # Unique temp file to avoid Windows sharing collisions
        tmp_yaml = target_yaml.parent / f"{target_yaml.stem}_{uuid.uuid4().hex}.tmp"
        try:
            with open(tmp_yaml, "w", encoding="utf-8") as f:
                yaml.safe_dump(existing_items, f, allow_unicode=True, sort_keys=False)
            os.replace(tmp_yaml, target_yaml)
        finally:
            tmp_yaml.unlink(missing_ok=True)

        # Reload global content loader atomically under lock to avoid Windows read-lock collision
        content_loader.reload()

    return new_q
