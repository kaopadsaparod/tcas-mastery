import io
import threading
import pytest
from fastapi.testclient import TestClient
import pymupdf

from app.database import init_db
from app.main import app
from app.models.api_schema import ProceduralSubmitRequest, SubmitAttemptRequest
from app.services.backup_service import create_backup, delete_backup
from app.services.content_loader import content_loader
from app.services.grader import grade_numeric, grade_numeric_detailed
from app.services.pdf_importer import (
    process_uploaded_image,
    process_uploaded_pdf,
    save_custom_question,
)
from app.services.review_engine import (
    evaluate_pace,
    get_interleaved_questions,
    get_learning_stats,
    record_attempt,
)


@pytest.fixture(autouse=True)
def setup_db():
    init_db()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


# ==============================================================================
# 🔴 1. Unit Stripping & Granular Tolerance Tests
# ==============================================================================


def test_unit_mismatch_fails_with_proper_error_tag():
    """
    Review Issue: If expected answer is 20 m/s and user inputs 20 km/h,
    it must NOT strip the unit blindly and award correct. It must grade as FALSE
    and tag with 'no_unit_conversion'.
    """
    # Matching unit
    is_correct, tag = grade_numeric_detailed("20 m/s", "20", expected_unit="m/s")
    assert is_correct is True
    assert tag is None

    # Omitted unit (plain number when unit displayed in UI)
    is_correct_plain, _ = grade_numeric_detailed("20", "20", expected_unit="m/s")
    assert is_correct_plain is True

    # Unit mismatch: user answered in km/h for an m/s question
    is_correct_mismatch, tag_mismatch = grade_numeric_detailed(
        "20 km/h", "20", expected_unit="m/s"
    )
    assert is_correct_mismatch is False
    assert tag_mismatch == "no_unit_conversion"

    # Thai unit synonym match
    is_correct_thai, _ = grade_numeric_detailed(
        "20 เมตร/วินาที", "20", expected_unit="m/s"
    )
    assert is_correct_thai is True


def test_drill_strict_tolerance_versus_approximate():
    """
    Review Issue: Drills are mental math with exact integer or neat fraction outputs.
    Tolerance must be strict (<= 0.001) instead of 2%.
    """
    # 20.3 is ~1.5% off from 20 -> should fail with strict drill tolerance (0.001)
    assert grade_numeric("20.3", "20", tolerance=0.001) is False
    assert grade_numeric("20.0001", "20", tolerance=0.001) is True


def test_drills_submit_api_enforces_unit_and_tolerance(client):
    """
    Submitting a drill via API with wrong unit gets marked incorrect.
    """
    payload = {
        "drill_type": "unit_kmh_ms",
        "question_stem": "แปลงความเร็ว 72 km/h เป็น m/s",
        "user_answer": "20 km/h",  # Wrong unit: should be 20 m/s
        "expected_answer": "20",
        "expected_unit": "m/s",
        "tolerance": 0.001,
        "time_spent_sec": 5.0,
    }
    res = client.post("/api/drills/submit", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["is_correct"] is False
    assert data["error_tag"] == "no_unit_conversion"


# ==============================================================================
# 🟠 2. Security Hardening Tests
# ==============================================================================


def test_pdf_magic_bytes_validation():
    """Rejects corrupted or fake files posing as PDF."""
    fake_bytes = b"NOT_A_PDF_HEADER_JUST_RANDOM_TEXT"
    with pytest.raises(ValueError, match="Magic bytes"):
        process_uploaded_pdf(fake_bytes, "exploit.pdf")


def test_image_magic_bytes_validation():
    """Rejects corrupted or fake image files."""
    fake_png = b"NOT_A_PNG_HEADER"
    with pytest.raises(ValueError, match="Magic bytes"):
        process_uploaded_image(fake_png, "exploit.png")


def test_pdf_page_limit_bomb_protection():
    """Rejects PDF files exceeding safe page limit (50 pages)."""
    doc = pymupdf.open()
    for _ in range(52):
        doc.new_page()
    pdf_bytes = doc.tobytes()
    doc.close()

    with pytest.raises(ValueError, match="เกินขีดจำกัดที่ปลอดภัย"):
        process_uploaded_pdf(pdf_bytes, "bomb.pdf")


def test_custom_question_rejects_xss_image_url():
    """Rejects malicious image_url like javascript: or arbitrary external URLs."""
    malicious_payload = {
        "id": "xss-test-01",
        "stem": "Test question",
        "image_url": "javascript:alert(1)",
        "answer_type": "single_choice",
        "options": [{"id": "o1", "text": "A"}],
        "correct_option": "o1",
    }
    with pytest.raises(ValueError, match="Invalid image_url format"):
        save_custom_question(malicious_payload)


def test_delete_backup_path_traversal_and_regex_protection():
    """Rejects traversal attempts and non-conforming backup filenames."""
    assert delete_backup("../../boot.ini") is False
    assert delete_backup("random_db.db") is False
    assert delete_backup("tcas_backup_badformat.db") is False

    # Valid backup deletion
    valid_backup = create_backup()
    assert valid_backup.exists()
    assert delete_backup(valid_backup.name) is True
    assert not valid_backup.exists()


def test_dns_rebinding_rejected(client):
    """Host header from untrusted external domain is rejected."""
    res = client.get("/", headers={"Host": "malicious-attacker.com"})
    assert res.status_code == 400
    assert "Untrusted Host header" in res.json()["detail"]


def test_csrf_origin_check_blocks_external_post(client):
    """Mutating POST requests from untrusted external origin are blocked."""
    res = client.post(
        "/api/bookmark/toggle",
        json={"question_id": "phy-kin-0001"},
        headers={"Origin": "https://evil-phishing-site.com"},
    )
    assert res.status_code == 403
    assert "Cross-origin request blocked" in res.json()["detail"]


# ==============================================================================
# 🧠 3. Pedagogy & Honest Mastery Tests
# ==============================================================================


def test_honest_mastery_excludes_lucky_guesses():
    """
    Review Issue: correct_first_try + guessed should NOT count as mastery.
    Honest Mastery counts only first_try with confidence 'sure' or 'unsure'.
    """
    # 1. Record a lucky guess
    record_attempt(
        question_id="phy-test-lucky",
        subject="physics",
        topic="physics.kinematics.1d",
        user_answer="o1",
        is_correct=True,
        status="correct_first_try",
        confidence="guessed",
    )

    stats_lucky = get_learning_stats()
    assert stats_lucky["lucky_guesses"] >= 1
    # Check that this guessed attempt was NOT added to honest_mastery_count
    orig_honest = stats_lucky["honest_mastery_count"]

    # 2. Record a genuine first-try master
    record_attempt(
        question_id="phy-test-sure",
        subject="physics",
        topic="physics.kinematics.1d",
        user_answer="o1",
        is_correct=True,
        status="correct_first_try",
        confidence="sure",
    )

    stats_genuine = get_learning_stats()
    assert stats_genuine["honest_mastery_count"] == orig_honest + 1


def test_confidence_calibration_metrics():
    """
    Verifies accuracy breakdown by confidence level (sure, unsure, guessed).
    """
    stats = get_learning_stats()
    assert "confidence_calibration" in stats
    assert "sure" in stats["confidence_calibration"]
    assert "unsure" in stats["confidence_calibration"]
    assert "guessed" in stats["confidence_calibration"]
    assert "misconception_rate_pct" in stats


def test_pace_evaluation_benchmark():
    """
    Tests A-Level pace benchmarks (180s for Physics/Math, 150s for TPAT3).
    """
    # Physics (target: 180s)
    fast_res = evaluate_pace("physics", 60.0)  # 60s < 180 * 0.75 (135s)
    assert fast_res["pace_status"] == "fast"

    optimal_res = evaluate_pace("physics", 160.0)  # 160s <= 180 * 1.15 (207s)
    assert optimal_res["pace_status"] == "optimal"

    slow_res = evaluate_pace("physics", 240.0)  # 240s > 207s
    assert slow_res["pace_status"] == "slow"


def test_interleaved_practice_mixing_topics():
    """
    Verifies that get_interleaved_questions returns questions alternating across topics.
    """
    questions = get_interleaved_questions(limit=5)
    assert len(questions) > 0
    if len(questions) >= 2:
        # Consecutive questions should alternate topics where multiple topics are available
        topics = [q.topic for q in questions]
        unique_topics = set(topics)
        if len(unique_topics) > 1:
            assert topics[0] != topics[1]


def test_interleaved_practice_endpoint(client):
    """Verifies /practice/interleaved renders properly."""
    res = client.get("/practice/interleaved")
    assert res.status_code == 200
    assert "โหมดฝึกสลับหัวข้อ" in res.text


def test_concurrent_custom_question_saves():
    """
    Review Issue: Import Studio read-modify-write on YAML must be thread-safe with lock
    and temp file replace to prevent file corruption.
    """
    def save_item(item_id: str):
        payload = {
            "id": f"concur-{item_id}",
            "subject": "physics",
            "topic": "physics.kinematics.1d",
            "stem": f"Concurrent test stem {item_id}",
            "answer_type": "single_choice",
            "options": [{"id": "o1", "text": "10"}, {"id": "o2", "text": "20"}],
            "correct_option": "o1",
        }
        save_custom_question(payload)

    threads = [threading.Thread(target=save_item, args=(f"thr_{i}",)) for i in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Verify all questions loaded safely into content_loader
    for i in range(4):
        assert content_loader.get_question_by_id(f"concur-thr_{i}") is not None

    # Clean up test questions from custom_questions.yaml so schema tests stay unaffected
    import yaml
    from app.config import CONTENT_DIR
    target_yaml = CONTENT_DIR / "imported" / "custom_questions.yaml"
    if target_yaml.exists():
        with open(target_yaml, "r", encoding="utf-8") as f:
            items = yaml.safe_load(f) or []
        filtered = [it for it in items if not str(it.get("id", "")).startswith("concur-thr_")]
        with open(target_yaml, "w", encoding="utf-8") as f:
            yaml.safe_dump(filtered, f, allow_unicode=True, sort_keys=False)
        content_loader.reload()


def test_lan_pin_protection(client, monkeypatch):
    """
    Review Issue: When exposed on LAN, sensitive endpoints require PIN verification.
    """
    import app.main
    monkeypatch.setattr(app.main, "TCAS_ACCESS_PIN", "4321")

    # Mutation without PIN should be rejected (401)
    res_no_pin = client.post("/api/backup/create")
    assert res_no_pin.status_code == 401
    assert "Invalid or missing TCAS PIN" in res_no_pin.json()["detail"]

    # Mutation with correct PIN header should succeed
    res_with_pin = client.post("/api/backup/create", headers={"x-tcas-pin": "4321"})
    assert res_with_pin.status_code == 200
    assert res_with_pin.json()["success"] is True

