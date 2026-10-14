import pytest
from fastapi.testclient import TestClient

from app.database import init_db
from app.main import app
from app.models.content_schema import AnswerConfig, NumericTrap, Question, SkillInfo, SourceInfo, VerificationInfo
from app.services.content_loader import content_loader
from app.services.grader import get_recommended_drill, grade_attempt
from app.services.mock_exam import EXAM_BLUEPRINTS, start_mock_exam, submit_mock_exam
from app.services.review_engine import evaluate_pace, record_attempt


@pytest.fixture(autouse=True)
def setup_app():
    init_db()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_alevel_math1_blueprint_loaded_and_scored():
    """Verify A-Level Math 1 Blueprint (30 Qs: 25 MCQ @ 3 pts + 5 Numeric @ 5 pts = 100 pts)."""
    p = content_loader.get_past_paper_by_id("alevel-math1-blueprint-30")
    assert p is not None
    assert p.subject == "math"
    assert p.time_limit_min == 90
    assert len(p.questions) == 30

    mcq_questions = [q for q in p.questions if q.answer_type == "single_choice"]
    num_questions = [q for q in p.questions if q.answer_type == "numeric"]

    assert len(mcq_questions) == 25
    assert len(num_questions) == 5

    total_score = sum(q.score for q in p.questions)
    assert total_score == 100.0
    for q in mcq_questions:
        assert q.score == 3.0
        assert len(q.options) == 5  # Official 5 choices
    for q in num_questions:
        assert q.score == 5.0
        assert q.known_traps is not None
        assert len(q.known_traps) >= 1


def test_tgat2_blueprint_loaded_and_scored():
    """Verify TGAT2 Logical Reasoning Blueprint (80 Qs @ 1.25 pts = 100 pts across 4 parts)."""
    p = content_loader.get_past_paper_by_id("tgat2-blueprint-80")
    assert p is not None
    assert p.subject == "tgat2"
    assert p.time_limit_min == 60
    assert len(p.questions) == 80

    total_score = sum(q.score for q in p.questions)
    assert abs(total_score - 100.0) < 1e-4

    # 4 distinct domains: verbal, numerical, spatial, logical (20 Qs each)
    verbal = [q for q in p.questions if q.topic == "tgat2.verbal"]
    num = [q for q in p.questions if q.topic == "tgat2.numerical"]
    spatial = [q for q in p.questions if q.topic == "tgat2.spatial"]
    logical = [q for q in p.questions if q.topic == "tgat2.logical"]

    assert len(verbal) == 20
    assert len(num) == 20
    assert len(spatial) == 20
    assert len(logical) == 20

    for q in p.questions:
        assert q.score == 1.25
        assert len(q.options) == 5  # Official 5 choices


def test_exam_blueprints_registration():
    """Verify both new engineering blueprints are registered in mock exam service."""
    assert "alevel_math1_mock_30" in EXAM_BLUEPRINTS
    assert "tgat2_mock_80" in EXAM_BLUEPRINTS
    assert EXAM_BLUEPRINTS["alevel_math1"]["paper_id"] == "alevel-math1-blueprint-30"
    assert EXAM_BLUEPRINTS["tgat2"]["paper_id"] == "tgat2-blueprint-80"
    assert EXAM_BLUEPRINTS["tgat2"]["pace_target_min"] == 0.75


def test_numeric_known_traps_detection():
    """Verify numeric questions match known_traps and return specific error_tags."""
    trap_q = Question(
        id="test-num-trap-01",
        subject="physics",
        topic="physics.mechanics.forces",
        source=SourceInfo(label="Test"),
        verification=VerificationInfo(status="verified"),
        skills=SkillInfo(primary="forces"),
        stem="คำนวณความเร่งเมื่อมีแรงเสียดทาน",
        answer=AnswerConfig(
            type="numeric",
            correct_value=2.0,
            unit="m/s^2",
            tolerance=0.02,
            require_unit=False,
            known_traps=[
                NumericTrap(
                    value=4.0,
                    error_tag="forgot_friction",
                    explanation="ลืมหักแรงเสียดทานออกจากแรงดึง",
                )
            ],
        ),
    )

    # 1. Correct answer
    res_correct = grade_attempt(trap_q, user_answer="2.0")
    assert res_correct.is_correct is True

    # 2. Trap answer: 4.0 should diagnose forgot_friction
    res_trap = grade_attempt(trap_q, user_answer="4.0")
    assert res_trap.is_correct is False
    assert res_trap.error_tag == "forgot_friction"
    assert "ลืมหักแรงเสียดทาน" in res_trap.explanation

    # 3. Arbitrary wrong answer: should fall back to arithmetic_error
    res_other = grade_attempt(trap_q, user_answer="99.0")
    assert res_other.is_correct is False
    assert res_other.error_tag == "arithmetic_error"


def test_mock_exam_ignores_unit_and_matches_known_traps(client):
    """Verify mock exam mode ignores units on numeric questions and detects known traps."""
    sess_data = start_mock_exam("alevel_math1_mock_30")
    sess_id = sess_data["session_id"]

    # Submit Q26 with known trap 100.0 (intermediate_stage_only) and Q27 with 420 (correct)
    answers = {
        "26": "100.0",  # trap
        "27": "420",    # correct
    }
    report = submit_mock_exam(sess_id, answers=answers, time_spent_min=45.0)

    q26_res = next(r for r in report["detailed_results"] if r["number"] == 26)
    q27_res = next(r for r in report["detailed_results"] if r["number"] == 27)

    assert q26_res["is_correct"] is False
    assert q26_res["error_tag"] == "intermediate_stage_only"
    assert q27_res["is_correct"] is True


def test_srs_guessed_resets_interval_and_overconfidence_penalty():
    """Verify guessed resets interval to 1 day and sure+wrong triggers overconfidence."""
    # Guessed + Correct -> interval must be 1 day (not multiplied)
    rec_guessed = record_attempt(
        question_id="test-srs-01",
        subject="math",
        topic="math.real_numbers",
        user_answer="5",
        is_correct=True,
        status="correct_first_try",
        confidence="guessed",
    )
    assert rec_guessed["interval_days"] == 1
    assert rec_guessed["is_overconfidence"] is False

    # Sure + Wrong -> Overconfidence penalty (priority high, interval 1)
    rec_overconf = record_attempt(
        question_id="test-srs-02",
        subject="math",
        topic="math.real_numbers",
        user_answer="1",
        is_correct=False,
        status="wrong",
        confidence="sure",
    )
    assert rec_overconf["interval_days"] == 1
    assert rec_overconf["priority"] == "high"
    assert rec_overconf["is_overconfidence"] is True


def test_recommended_drill_and_formula_card():
    """Verify error tags map to recommended drills and formula cards."""
    # Unit conversion tag maps to speed conversion drill
    drill_unit = get_recommended_drill("no_unit_conversion")
    assert drill_unit is not None
    assert drill_unit["type"] == "speed_conversion"

    # Arithmetic tag maps to powers and scientific drill
    drill_arith = get_recommended_drill("arithmetic_error")
    assert drill_arith is not None
    assert drill_arith["type"] == "powers_and_scientific"

    # Topic formula lookup
    formula = content_loader.get_formula_for_topic("physics.kinematics.1d", "physics")
    assert formula is not None
    assert "v = u + at" in formula.latex




def test_self_diagnose_api_endpoint(client):
    """Verify /api/attempt/self-diagnose updates attempt error_tag in database."""
    # Record an attempt first
    record_attempt(
        question_id="test-diag-01",
        subject="math",
        topic="math.real_numbers",
        user_answer="99",
        is_correct=False,
        status="wrong",
        confidence="sure",
    )

    # Post self-diagnosis
    resp = client.post(
        "/api/attempt/self-diagnose",
        json={"question_id": "test-diag-01", "error_tag": "formula_misapplication"},
    )
    assert resp.status_code == 200
    assert resp.json()["success"] is True

    # Verify review_queue updated
    from app.database import get_db
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT last_error_tag FROM review_queue WHERE question_id = ?", ("test-diag-01",))
        row = cursor.fetchone()
        assert row["last_error_tag"] == "formula_misapplication"


def test_pace_target_for_tgat2():
    """Verify TGAT2 pace target is calibrated to 45.0 seconds per question."""
    pace = evaluate_pace("tgat2", 30.0)
    assert pace["pace_target_sec"] == 45.0
    assert pace["pace_status"] == "fast"

    pace_slow = evaluate_pace("tgat2", 70.0)
    assert pace_slow["pace_status"] == "slow"
