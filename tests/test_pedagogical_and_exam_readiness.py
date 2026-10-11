import json
import pytest
from fastapi.testclient import TestClient

from app.database import get_db, init_db
from app.main import app
from app.models.api_schema import SubmitAttemptRequest
from app.models.content_schema import PastPaper, PastPaperQuestion, Question, SourceInfo, VerificationInfo, SkillInfo, AnswerConfig, ChoiceOption
from app.services.answer_sheet import grade_answer_sheet
from app.services.backup_service import create_backup, restore_backup, verify_backup_file
from app.services.content_loader import content_loader
from app.services.grader import grade_attempt, grade_numeric, grade_numeric_detailed
from app.services.learning_path import analyze_topic_readiness, get_prerequisites_for_topic, get_skill_remediation
from app.services.mock_exam import (
    get_mock_exam_sanitized_questions,
    get_mock_exam_session,
    save_mock_exam_progress,
    start_mock_exam,
    submit_mock_exam,
)
from app.services.review_engine import record_attempt
from app.services.roadmap_service import get_roadmap_topics
from app.services.study_planner import get_daily_study_plan
from app.services.tutor_engine import build_tutor_breakdown


@pytest.fixture(autouse=True)
def setup_db():
    init_db()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


# ==============================================================================
# 🔴 P1: Answer Sheet & Type-Specific Scoring Tests
# ==============================================================================


def test_mcq_choice_rejects_close_numeric_answer():
    """
    P1 Issue: If question is MCQ choice '3', user submitting '3.05' MUST BE REJECTED.
    Numeric tolerance must NEVER apply to multiple choice items!
    """
    paper = PastPaper(
        id="mock-mcq-test",
        title="MCQ Strict Test",
        subject="physics",
        year=2566,
        questions=[
            PastPaperQuestion(
                number=1,
                correct_answer="3",
                answer_type="single_choice",
                topic="physics.kinematics.1d",
                skill="test_skill",
                score=3.0,
            )
        ],
    )

    # User enters "3.05" for choice "3" -> MUST BE WRONG
    res_float = grade_answer_sheet(paper, {"1": "3.05"})
    assert res_float.correct_count == 0
    assert res_float.score_percent == 0.0

    # User enters exact "3" -> CORRECT
    res_exact = grade_answer_sheet(paper, {"1": "3"})
    assert res_exact.correct_count == 1
    assert res_exact.score_percent == 100.0


def test_numeric_question_accepts_within_tolerance_only():
    """
    P1 Issue: For numeric questions, tolerance applies properly.
    """
    paper = PastPaper(
        id="mock-num-test",
        title="Numeric Tolerance Test",
        subject="physics",
        year=2566,
        questions=[
            PastPaperQuestion(
                number=1,
                correct_answer="50.0",
                answer_type="numeric",
                tolerance=0.02,  # 2% tolerance -> [49.0, 51.0]
                topic="physics.forces_energy",
                skill="test_skill",
                score=5.0,
            )
        ],
    )

    # 50.5 is within 1% (< 2%) -> Accepted
    res_close = grade_answer_sheet(paper, {"1": "50.5"})
    assert res_close.correct_count == 1

    # 53.0 is 6% off (> 2%) -> Rejected
    res_far = grade_answer_sheet(paper, {"1": "53.0"})
    assert res_far.correct_count == 0


# ==============================================================================
# 🔴 P1: Grader Unit Requirements & Missing Unit Feedback
# ==============================================================================


def test_missing_unit_when_require_unit_is_true():
    """
    P1 Issue: When require_unit is True and student enters number without unit,
    system must reject and tag with 'missing_unit'.
    """
    # Expected: 20 m/s with require_unit=True
    is_ok, tag = grade_numeric_detailed(
        "20", "20", tolerance=0.01, expected_unit="m/s", require_unit=True
    )
    assert is_ok is False
    assert tag == "missing_unit"

    # When unit is provided: 20 m/s -> Accepted
    is_ok_with_unit, tag_ok = grade_numeric_detailed(
        "20 m/s", "20", tolerance=0.01, expected_unit="m/s", require_unit=True
    )
    assert is_ok_with_unit is True
    assert tag_ok is None


def test_wrong_unit_returns_no_unit_conversion():
    """
    P1 Issue: When user provides a mismatched unit (e.g. 20 km/h for 20 m/s),
    system must reject and tag with 'no_unit_conversion'.
    """
    is_ok, tag = grade_numeric_detailed(
        "20 km/h", "20", tolerance=0.01, expected_unit="m/s", require_unit=True
    )
    assert is_ok is False
    assert tag == "no_unit_conversion"


def test_assisted_attempts_do_not_count_as_first_try_mastery():
    """
    P1 Issue: Solving correctly after hints opened must NOT be counted as honest first-try mastery.
    """
    q = content_loader.get_question_by_id("phy-kin-0001")
    assert q is not None

    # Correct with 1 hint opened
    res = grade_attempt(question=q, user_answer="o1", hints_opened=1, confidence="sure")
    assert res.is_correct is True
    assert res.status == "correct_assisted"
    assert res.next_review_interval_days == 1  # Reviewed sooner because hints were used


# ==============================================================================
# 🔴 P1: Topic Mastery Formula & Anti-Inflation Tests
# ==============================================================================


def test_repeated_attempts_do_not_inflate_unique_question_mastery():
    """
    P1 Issue: Repeatedly submitting the same question 10 times must NOT inflate unique questions
    nor claim 100% mastery without multi-question evidence.
    """
    tid = "test.anti_inflation.topic"
    qid = "test-repeat-q-001"

    with get_db() as conn:
        conn.execute("DELETE FROM attempts WHERE topic = ?", (tid,))
        conn.execute("DELETE FROM topic_priorities WHERE topic_id = ?", (tid,))
        conn.execute(
            "INSERT INTO topic_priorities (topic_id, subject, topic_name, priority_level) VALUES (?, ?, ?, ?)",
            (tid, "physics", "หัวข้อทดสอบ Anti-Inflation", 1),
        )

    # User attempts the same question 10 times correctly
    for _ in range(10):
        record_attempt(
            question_id=qid,
            subject="physics",
            topic=tid,
            user_answer="o1",
            is_correct=True,
            status="correct_first_try",
            confidence="sure",
        )

    topics = get_roadmap_topics()
    match = next(t for t in topics if t["topic_id"] == tid)

    # Must detect only 1 unique question attempted, not 10!
    assert match["total_attempts"] == 10
    assert match["unique_questions_attempted"] == 1
    # Sample size is insufficient (1 < 3) -> goal is NOT met!
    assert match["sufficiency"] == "minimal"
    assert match["is_goal_met"] is False


def test_cold_start_does_not_claim_strength_or_weakness():
    """
    P1 Issue: When user has 0 attempts for a topic, system must report 'not_enough_data'
    without making false claims.
    """
    tid = "test.cold_start.topic"
    with get_db() as conn:
        conn.execute("DELETE FROM attempts WHERE topic = ?", (tid,))
        conn.execute("DELETE FROM topic_priorities WHERE topic_id = ?", (tid,))
        conn.execute(
            "INSERT INTO topic_priorities (topic_id, subject, topic_name, priority_level) VALUES (?, ?, ?, ?)",
            (tid, "physics", "หัวข้อทดสอบ Cold Start", 2),
        )

    topics = get_roadmap_topics()
    match = next(t for t in topics if t["topic_id"] == tid)

    assert match["total_attempts"] == 0
    assert match["unique_questions_attempted"] == 0
    assert match["current_mastery_pct"] == 0.0
    assert match["sufficiency"] == "not_enough_data"
    assert match["mastery_confidence"] == "not_enough_data"


# ==============================================================================
# 🔴 P1: Real Backup Restore & Verification Tests
# ==============================================================================


def test_real_backup_restore_and_verification():
    """
    P1 Issue: Verify real backup restoration mechanism with SQLite integrity check.
    """
    # 1. Create a live backup
    backup_path = create_backup()
    assert backup_path.exists()

    # 2. Verify backup file directly
    v_res = verify_backup_file(backup_path)
    assert v_res["valid"] is True
    assert v_res["integrity_ok"] is True
    assert len(v_res["missing_tables"]) == 0

    # 3. Perform real restore
    r_res = restore_backup(backup_path.name)
    assert r_res["success"] is True
    assert "safety_backup" in r_res

    # 4. Cleanup
    backup_path.unlink(missing_ok=True)
    if "safety_backup" in r_res:
        (backup_path.parent / r_res["safety_backup"]).unlink(missing_ok=True)


# ==============================================================================
# 🟠 P2: Adaptive Learning Path & Prerequisite Engine Tests
# ==============================================================================


def test_prerequisite_dependency_analysis():
    """
    P2: Forces & Energy requires 1D Kinematics and Vectors.
    """
    prereqs = get_prerequisites_for_topic("physics.forces_energy")
    assert "physics.kinematics.1d" in prereqs

    readiness = analyze_topic_readiness("physics.forces_energy")
    assert readiness["has_prerequisites"] is True
    assert "prerequisites" in readiness


def test_skill_remediation_lookup():
    """
    P2: Missing choose_constant_accel_eq links to kinematics 5-EQ drill.
    """
    rem = get_skill_remediation("choose_constant_accel_eq")
    assert rem is not None
    assert rem["drill_type"] == "kinematics_5eq"
    assert "5 สมการ" in rem["title"]


def test_personal_study_planner_generation():
    """
    P2: Study planner generates 4 blocks matching requested time budget.
    """
    plan = get_daily_study_plan(daily_minutes=60, target_exam="alevel")
    assert plan["daily_minutes"] == 60
    assert len(plan["blocks"]) == 4

    # Total allocated minutes matches ~60 min
    total_allocated = sum(b["allocated_minutes"] for b in plan["blocks"])
    assert total_allocated == 60

    # Blocks include Spaced Review and Speed Drill
    block_ids = [b["block_id"] for b in plan["blocks"]]
    assert "spaced_review" in block_ids
    assert "speed_drill" in block_ids
    assert "micro_quiz" in block_ids


def test_pedagogical_5_step_tutor_breakdown():
    """
    P2: Tutor engine returns 5 structured steps for mistake remediation.
    """
    q = content_loader.get_question_by_id("phy-kin-0001")
    assert q is not None

    breakdown = build_tutor_breakdown(q, user_answer="o2", error_tag="no_unit_conversion")
    assert "step_1_given_goal" in breakdown
    assert "step_2_principle" in breakdown
    assert "step_3_substitution" in breakdown
    assert "step_4_sanity_check" in breakdown
    assert "step_5_variant" in breakdown
    assert breakdown["error_tag"] == "no_unit_conversion"


# ==============================================================================
# 🟡 P3: Full Mock Exam Engine Tests
# ==============================================================================


def test_full_mock_exam_lifecycle():
    """
    P3: Start mock exam -> save progress -> submit -> receive full diagnostic report.
    """
    # 1. Start exam
    sess_data = start_mock_exam("alevel_physics")
    session_id = sess_data["session_id"]
    assert session_id is not None
    assert sess_data["time_limit_min"] == 90
    assert sess_data["total_questions"] > 0

    # Verify questions are sanitized (no answers exposed)
    for q in sess_data["questions"]:
        assert "correct_answer" not in q

    # 2. Check session retrieval
    sess = get_mock_exam_session(session_id)
    assert sess is not None
    assert sess["status"] == "in_progress"

    # 3. Submit exam with sample answers
    # Answer question 1 correctly ("2" based on sample paper)
    answers = {"1": "2", "2": "4", "19": "25"}
    report = submit_mock_exam(session_id, answers, time_spent_min=45.0)

    assert report["session_id"] == session_id
    assert report["time_spent_min"] == 45.0
    assert report["total_score"] > 0
    assert "topic_breakdown" in report
    assert "detailed_results" in report
    assert report["avg_pace_min"] > 0


def test_api_planner_and_mock_exam_routes(client):
    """
    Verify /planner, /mock-exam and API endpoints respond with 200 OK.
    """
    res_planner = client.get("/planner?minutes=45")
    assert res_planner.status_code == 200
    assert "ตารางติวประจำวันของคุณ" in res_planner.text

    res_mock = client.get("/mock-exam")
    assert res_mock.status_code == 200
    assert "ระบบจำลองสอบเสมือนจริง" in res_mock.text


def test_mock_exam_single_question_snapshot_freezing():
    """
    Phase 1: Session must store a frozen snapshot in questions_json.
    Sanitized question stream must hide answers, and grading must verify against snapshot IDs.
    """
    sess = start_mock_exam("alevel_physics_practice_20")
    session_id = sess["session_id"]

    db_sess = get_mock_exam_session(session_id)
    assert db_sess is not None
    assert len(db_sess["questions"]) == sess["total_questions"]
    assert db_sess["questions"][0]["question_id"] is not None

    # Sanitized questions do not expose correct_answer
    sanitized = get_mock_exam_sanitized_questions(session_id)
    for q in sanitized:
        assert "correct_answer" not in q

    # Grade with exact answers from snapshot
    target_q = db_sess["questions"][0]
    num = str(target_q["number"])
    ans = target_q["correct_answer"]

    rep = submit_mock_exam(session_id, {num: ans}, time_spent_min=10.0)
    assert rep["correct_count"] >= 1
    match_item = next(item for item in rep["detailed_results"] if item["number"] == target_q["number"])
    assert match_item["is_correct"] is True
    assert match_item["question_id"] == target_q["question_id"]


def test_mock_exam_resumption_and_autosave():
    """
    Phase 1: Progress auto-saved during an active exam must be retained on reload/resume.
    """
    sess = start_mock_exam("alevel_physics_practice_20")
    session_id = sess["session_id"]

    # Autosave progress
    save_ok = save_mock_exam_progress(
        session_id=session_id,
        answers={"1": "2", "2": "4"},
        flagged=[2, 5],
        time_spent_min=12.5,
    )
    assert save_ok is True

    # Resume session
    resumed = get_mock_exam_session(session_id)
    assert resumed["answers"] == {"1": "2", "2": "4"}
    assert resumed["flagged"] == [2, 5]
    assert resumed["time_spent_min"] == 12.5


def test_mock_exam_submission_idempotency():
    """
    Phase 1: Submitting an already completed mock exam session returns the existing report
    and avoids double submission or altered scores.
    """
    sess = start_mock_exam("alevel_physics_practice_20")
    session_id = sess["session_id"]

    rep1 = submit_mock_exam(session_id, {"1": "2"}, time_spent_min=20.0)
    rep2 = submit_mock_exam(session_id, {"1": "999"}, time_spent_min=99.0)

    assert rep1["total_score"] == rep2["total_score"]
    assert rep1["time_spent_min"] == rep2["time_spent_min"]
    assert rep2["session_id"] == session_id


def test_mock_exam_tpat3_flow():
    """
    Phase 1: TPAT3 practice flow runs smoothly from initialization to grading.
    """
    sess = start_mock_exam("tpat3_practice_25")
    assert sess["total_questions"] > 0
    assert sess["time_limit_min"] == 60

    rep = submit_mock_exam(sess["session_id"], {}, time_spent_min=2.0)
    assert rep["total_score"] >= 0.0
    assert rep["pace_status"] == "optimal"

