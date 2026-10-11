from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import BASE_DIR
from app.database import init_db
from app.main import app
from app.models.content_schema import PastPaper, PastPaperQuestion
from app.services.answer_sheet import grade_answer_sheet
from app.services.backup_service import create_backup, delete_backup
from app.services.grader import grade_numeric, normalize_numeric_string
from app.services.roadmap_service import (
    get_roadmap_topics,
    update_topic_priority,
)


@pytest.fixture(autouse=True)
def setup_app():
    init_db()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_offline_katex_vendor_files_exist():
    vendor_dir = BASE_DIR / "app" / "static" / "vendor" / "katex"
    assert (vendor_dir / "katex.min.css").exists()
    assert (vendor_dir / "katex.min.js").exists()
    assert (vendor_dir / "auto-render.min.js").exists()


def test_numeric_normalizer_unit_stripping_and_thai_numerals():
    # Thai numerals
    assert normalize_numeric_string("๑๒.๕") == 12.5
    assert normalize_numeric_string("๕๐") == 50.0

    # Physical units stripped
    assert normalize_numeric_string("20 m/s") == 20.0
    assert normalize_numeric_string("5.0 N") == 5.0
    assert normalize_numeric_string("1,000 J") == 1000.0
    assert normalize_numeric_string("−15.2 m/s") == -15.2

    # Scientific notation preservation
    assert normalize_numeric_string("2e3") == 2000.0


def test_answer_sheet_flexible_numeric_grading():
    dummy_paper = PastPaper(
        id="test-paper-num",
        title="Test Numeric Paper",
        subject="physics",
        year=2026,
        questions=[
            PastPaperQuestion(number=1, correct_answer="12.5", topic="physics.kinematics.1d", skill="calc", score=1.0),
            PastPaperQuestion(number=2, correct_answer="−5", topic="physics.kinematics.1d", skill="calc", score=1.0),
        ]
    )

    # User answers "12.50" for "12.5" and "-5 m/s" for "−5"
    res = grade_answer_sheet(dummy_paper, {"1": "12.50", "2": "-5 m/s"})
    assert res.correct_count == 2
    assert res.score_percent == 100.0


def test_bookmark_api_toggle(client):
    qid = "phy-kin-0001"
    # Toggle on
    res1 = client.post("/api/bookmark/toggle", json={"question_id": qid})
    assert res1.status_code == 200
    assert res1.json()["bookmarked"] is True

    # Practice page shows is_bookmarked
    res_page = client.get(f"/practice/{qid}")
    assert res_page.status_code == 200
    assert "บันทึกแล้ว" in res_page.text

    # Filter bookmarked only
    res_filter = client.get("/practice?bookmarked_only=true")
    assert res_filter.status_code == 200
    assert qid in res_filter.text

    # Toggle off
    res2 = client.post("/api/bookmark/toggle", json={"question_id": qid})
    assert res2.status_code == 200
    assert res2.json()["bookmarked"] is False


def test_presolve_ai_prompt_api(client):
    qid = "phy-kin-0001"
    res = client.get(f"/api/ai-prompt/presolve/{qid}")
    assert res.status_code == 200
    prompt = res.json()["prompt"]
    assert "สิ่งที่โจทย์กำหนดให้" in prompt
    assert "อย่าเพิ่งบอกคำตอบสุดท้าย" in prompt


def test_exam_date_update_api(client):
    payload = {"tpat_date": "2026-12-15", "alevel_date": "2027-03-22"}
    res = client.post("/api/roadmap/update-exam-dates", json=payload)
    assert res.status_code == 200
    assert res.json()["success"] is True

    res_page = client.get("/roadmap")
    assert "2026-12-15" in res_page.text


def test_roadmap_order_index_preservation():
    topics = get_roadmap_topics()
    t1 = topics[0]
    orig_order = t1["order_index"]

    # Update priority level without passing order_index
    update_topic_priority(t1["topic_id"], priority_level=2, target_score_pct=90.0)

    updated_topics = get_roadmap_topics()
    match_t = next(t for t in updated_topics if t["topic_id"] == t1["topic_id"])
    assert match_t["order_index"] == orig_order
    assert match_t["target_score_pct"] == 90.0


def test_backup_delete_service_and_api(client):
    backup_path = create_backup()
    assert backup_path.exists()

    res = client.post("/api/backup/delete", json={"filename": backup_path.name})
    assert res.status_code == 200
    assert res.json()["success"] is True
    assert not backup_path.exists()
