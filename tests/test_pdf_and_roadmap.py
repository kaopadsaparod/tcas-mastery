import pymupdf
import pytest
from fastapi.testclient import TestClient

from app.database import init_db
from app.main import app
from app.services.content_loader import content_loader
from app.services.pdf_importer import process_uploaded_pdf, save_custom_question
from app.services.roadmap_service import (
    add_custom_topic,
    get_exam_countdown,
    get_roadmap_topics,
    reorder_topic_priority,
    update_topic_priority,
)


@pytest.fixture(autouse=True)
def setup_test_env():
    init_db()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_pdf_importer_and_question_builder():
    """Create an in-memory PDF, process it, and save a question into custom bank."""
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Sample Physics Exam from Social Media Page 1")
    pdf_bytes = doc.tobytes()
    doc.close()

    result = process_uploaded_pdf(pdf_bytes, "ig_exam_test.pdf")
    assert result["page_count"] == 1
    assert len(result["pages"]) == 1
    assert result["original_filename"] == "ig_exam_test.pdf"
    assert result["filename"].endswith(".pdf")
    assert "Sample Physics Exam" in result["pages"][0]["text_snippet"]

    # Save a question built from this PDF
    question_payload = {
        "id": "custom-ig-001",
        "subject": "physics",
        "topic": "physics.kinematics.1d",
        "stem": "วัตถุเคลื่อนที่ด้วยความเร็ว $10\\text{ m/s}$ (อ้างอิงจากชีต IG)",
        "image_url": result["pages"][0]["image_url"],
        "answer_type": "single_choice",
        "options": [
            {"id": "o1", "text": "10 m"},
            {"id": "o2", "text": "20 m"},
        ],
        "correct_option": "o1",
        "solution_summary": "แนวคิดคือความเร็วคูณเวลา",
        "source_label": "ชีตฟิสิกส์ IG Test",
    }

    q = save_custom_question(question_payload)
    assert q.id == "custom-ig-001"

    # Verify content_loader instantly sees it
    fetched = content_loader.get_question_by_id("custom-ig-001")
    assert fetched is not None
    assert fetched.stem == question_payload["stem"]
    assert fetched.image_url == question_payload["image_url"]


def test_roadmap_service_and_priorities():
    """Test custom syllabus priority reordering and topic addition."""
    topics = get_roadmap_topics()
    assert len(topics) >= 4

    # Add a custom chapter from syllabus
    add_custom_topic(
        topic_id="physics.shm",
        subject="physics",
        topic_name="การเคลื่อนที่แบบฮาร์มอนิกอย่างง่าย (SHM)",
        priority_level=1,
        target_score_pct=85.0,
        notes="ข้อสอบออกสม่ำเสมอ 2 ข้อทุกปี",
    )

    updated_topics = get_roadmap_topics()
    shm_topic = next(
        (t for t in updated_topics if t["topic_id"] == "physics.shm"), None
    )
    assert shm_topic is not None
    assert shm_topic["priority_level"] == 1
    assert shm_topic["target_score_pct"] == 85.0

    # Update priority
    update_topic_priority(
        topic_id="physics.shm",
        priority_level=2,
        order_index=5,
        target_score_pct=90.0,
        notes="ปรับลดมาเน้นหลังกลศาสตร์",
    )

    t_recheck = next(
        (t for t in get_roadmap_topics() if t["topic_id"] == "physics.shm"), None
    )
    assert t_recheck["priority_level"] == 2
    assert t_recheck["target_score_pct"] == 90.0

    # Reorder test
    reorder_topic_priority("physics.shm", "up")

    # Countdown test
    countdown = get_exam_countdown()
    assert countdown["tpat_days_left"] > 0
    assert countdown["alevel_days_left"] > 0


def test_routes_import_and_roadmap(client):
    """Test web routes for /import and /roadmap."""
    res_import = client.get("/import")
    assert res_import.status_code == 200
    assert "Exam Import Studio" in res_import.text

    res_roadmap = client.get("/roadmap")
    assert res_roadmap.status_code == 200
    assert "Custom Study Roadmap" in res_roadmap.text
