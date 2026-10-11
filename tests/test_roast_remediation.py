import pytest
from fastapi.testclient import TestClient

from app.database import get_db, init_db
from app.main import app
from app.services.content_loader import content_loader
from app.services.learning_path import analyze_topic_readiness
from app.services.mock_exam import EXAM_BLUEPRINTS, start_mock_exam, submit_mock_exam
from app.services.roadmap_service import get_roadmap_topics, reorder_topic_priority


@pytest.fixture(autouse=True)
def setup_db_and_content():
    init_db()
    content_loader.reload()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_roast_01_question_catalog_adapted():
    """Verify PastPaper questions are adapted into the main question bank."""
    questions = content_loader.get_all_questions()
    assert len(questions) >= 87, f"Expected at least 87 questions, got {len(questions)}"

    # Check that past paper questions are queryable as full Question models
    bp_q1 = content_loader.get_question_by_id("bp30-q01")
    assert bp_q1 is not None
    assert bp_q1.id == "bp30-q01"
    assert bp_q1.subject == "physics"
    assert bp_q1.topic == "physics.kinematics.1d"
    assert bp_q1.answer.options is not None
    assert len(bp_q1.answer.options) >= 2

    sample_q1 = content_loader.get_question_by_id("sample20-q01")
    assert sample_q1 is not None
    assert sample_q1.id == "sample20-q01"
    assert sample_q1.subject == "physics"


def test_roast_02_vectors_and_algebra_prerequisites():
    """Verify prerequisite ghost topics (vectors and algebra basics) are fully populated."""
    vec_q = content_loader.get_question_by_id("phy-vec-0001")
    assert vec_q is not None
    assert vec_q.topic == "physics.vectors"

    alg_q = content_loader.get_question_by_id("mat-alg-base-0001")
    assert alg_q is not None
    assert alg_q.topic == "math.algebra.basics"

    # Kinematics depends on physics.vectors
    readiness = analyze_topic_readiness("physics.kinematics.1d")
    assert readiness["topic_id"] == "physics.kinematics.1d"
    # Prerequisites should list physics.vectors and content loader must have questions for it
    prereq_ids = [p["topic_id"] for p in readiness["prerequisites"]]
    assert "physics.vectors" in prereq_ids
    assert len(content_loader.get_questions_by_topic("physics.vectors")) >= 1


def test_roast_03_tpat3_70_blueprint():
    """Verify authentic 70-question TPAT3 blueprint and mock session generation."""
    assert "tpat3_mock_70" in EXAM_BLUEPRINTS
    bp = EXAM_BLUEPRINTS["tpat3_mock_70"]
    assert bp["total_questions"] == 70
    assert bp["max_score"] == 100.0
    assert bp["time_limit_min"] == 180
    assert bp["is_official_blueprint"] is True

    # Start mock exam
    session = start_mock_exam("tpat3_mock_70")
    assert session["total_questions"] == 70
    assert len(session["questions"]) == 70
    assert session["time_limit_min"] == 180
    assert session["exam_type"] == "tpat3_mock_70"


def test_roast_04_mock_exam_mistakes_enter_spaced_repetition():
    """Verify that mistakes made during mock exams are fed into spaced repetition review queue."""
    session = start_mock_exam("alevel_physics_practice_20")
    session_id = session["session_id"]
    q_first = session["questions"][0]

    # Deliberately submit a wrong answer for the first question
    wrong_answer = "wrong_choice_999"
    answers = {str(q_first["number"]): wrong_answer}

    report = submit_mock_exam(session_id, answers)
    assert report["total_questions"] == 20
    assert report["correct_count"] < 20

    # Verify attempt recorded in database
    qid = q_first["question_id"]
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM attempts WHERE question_id = ? ORDER BY id DESC LIMIT 1", (qid,))
        attempt = cursor.fetchone()
        assert attempt is not None
        assert attempt["is_correct"] == 0
        assert attempt["user_answer"] == wrong_answer

        # Verify entry in review_queue
        cursor.execute("SELECT * FROM review_queue WHERE question_id = ?", (qid,))
        rq = cursor.fetchone()
        assert rq is not None


def test_roast_08_reorder_topic_priority_deadlock():
    """Verify that reordering topics with tied order_index (0, 0) resolves without deadlock."""
    with get_db() as conn:
        cursor = conn.cursor()
        # Set two existing topics to have the exact same order_index
        cursor.execute("UPDATE topic_priorities SET order_index = 0 WHERE topic_id IN ('physics.vectors', 'physics.kinematics.1d')")

    topics_before = get_roadmap_topics()
    idx_map_before = {t["topic_id"]: t["order_index"] for t in topics_before}
    assert idx_map_before.get("physics.vectors") == idx_map_before.get("physics.kinematics.1d")

    # Reorder down
    reorder_topic_priority("physics.vectors", "down")

    topics_after = get_roadmap_topics()
    idx_map_after = {t["topic_id"]: t["order_index"] for t in topics_after}
    # They must no longer have identical order_index
    assert idx_map_after["physics.vectors"] != idx_map_after["physics.kinematics.1d"]


def test_roast_09_dashboard_workflows_and_mock_integration(client):
    """Verify that the dashboard displays all primary study workflows and mock exam status."""
    res = client.get("/")
    assert res.status_code == 200
    html = res.text
    # Core workflows must be present
    assert "/planner" in html
    assert "/mock-exam" in html
    assert "/progress" in html
    assert "/roadmap" in html
    assert "ตารางติวรายวัน (Daily Planner)" in html
    assert "จำลองสอบจริง (Mock Exam)" in html
    assert "ประเมินความพร้อมสอบ (Readiness)" in html


def test_roast_10_formula_review_spaced_repetition(client):
    """Verify formula review persists next_review_at for spaced repetition."""
    payload = {
        "formula_id": "form-kin-01",
        "question_index": 0,
        "user_answer": "b",
    }
    res = client.post("/api/formulas/submit", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["is_correct"] is True

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM formula_reviews WHERE formula_id = 'form-kin-01'")
        row = cursor.fetchone()
        assert row is not None
        assert row["next_review_at"] is not None
        assert row["correct_count"] >= 1
