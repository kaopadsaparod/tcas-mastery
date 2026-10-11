import pytest

from app.database import init_db
from app.models.content_schema import AnswerConfig, ChoiceOption, Question, SkillInfo, SourceInfo, VerificationInfo
from app.services.content_loader import content_loader
from app.services.mock_exam import EXAM_BLUEPRINTS, start_mock_exam, submit_mock_exam


@pytest.fixture(autouse=True)
def setup_content():
    init_db()
    content_loader.reload()


# ==============================================================================
# 1. P0 Regression Tests: Question & Answer Key Correctness
# ==============================================================================


def test_tpat3_q14_answer_key_and_solution_consistency():
    """
    P0 Issue: TPAT3 item 14 wire cut geometric sequence.
    Wire starts at 81 cm, cut 1/3 of remaining each step.
    After 3 cuts: 81 * (2/3)^3 = 81 * (8/27) = 24 cm.
    Must map to option '2' (24 cm), NOT option '1' (16 cm).
    Solution must be professional without draft notes.
    """
    paper = content_loader.get_past_paper_by_id("tpat3-blueprint-70")
    assert paper is not None
    q14 = next((q for q in paper.questions if q.number == 14), None)
    assert q14 is not None

    # Assert correct answer is option 2
    assert q14.correct_answer == "2"

    # Assert option 2 is 24 cm
    opt_map = {opt.id: opt.text for opt in (q14.options or [])}
    assert opt_map.get("2") == "24 cm"
    assert opt_map.get("1") == "16 cm"

    # Math assertion
    length_initial = 81
    remaining = length_initial * ((2 / 3) ** 3)
    assert round(remaining) == 24

    # Solution hygiene: no draft hesitation words
    sol = q14.solution or ""
    assert "24 cm" in sol
    assert "อ้อ" not in sol
    assert "รอสักครู่" not in sol


def test_tpat3_q18_cube_rotation_geometry():
    """
    P0 Issue: TPAT3 item 18 3D cube rotation.
    1. Rotate right 90 degrees about vertical axis: Left face -> Front face.
    2. Tilt/pitch forward 90 degrees about horizontal axis: Front face -> Bottom face (ด้านล่าง).
    Must map to option '4' ('ด้านล่าง'), NOT option '1' ('ด้านหน้า').
    """
    paper = content_loader.get_past_paper_by_id("tpat3-blueprint-70")
    assert paper is not None
    q18 = next((q for q in paper.questions if q.number == 18), None)
    assert q18 is not None

    assert q18.correct_answer == "4"
    opt_map = {opt.id: opt.text for opt in (q18.options or [])}
    assert opt_map.get("4") == "ด้านล่าง"

    sol = q18.solution or ""
    assert "ด้านล่าง" in sol
    assert "หรือถ้า" not in sol


def test_alevel_phy_q06_work_energy_consistency():
    """
    P0 Issue: A-Level Physics item 6 work-energy theorem.
    F = 16 N, m = 2 kg, s = 9 m from rest.
    W = F*s = 16 * 9 = 144 J = (1/2)*m*v^2 = v^2 => v = 12 m/s.
    Stem, options, answer key, and solution must be 100% harmonious without hesitation.
    """
    paper = content_loader.get_past_paper_by_id("alevel-phy-blueprint-30")
    assert paper is not None
    q6 = next((q for q in paper.questions if q.number == 6), None)
    assert q6 is not None

    assert "16" in (q6.stem or "")
    assert "9" in (q6.stem or "")
    assert "2" in (q6.stem or "")

    assert q6.correct_answer == "4"
    opt_map = {opt.id: opt.text for opt in (q6.options or [])}
    assert opt_map.get("4") == "12 m/s"

    # Math assertion
    f, m, s = 16.0, 2.0, 9.0
    v = (2 * f * s / m) ** 0.5
    assert round(v, 4) == 12.0

    sol = q6.solution or ""
    assert "12 m/s" in sol
    assert "รอสักครู่" not in sol
    assert "หรือถ้า" not in sol


def test_alevel_phy_q26_stopping_distance():
    """
    P0 Issue: A-Level Physics item 26 stopping distance calculation.
    Car at 72 km/h (20 m/s) brakes with constant deceleration 4 m/s^2.
    Stopping distance s = v^2 / (2a) = 400 / 8 = 50 m.
    """
    paper = content_loader.get_past_paper_by_id("alevel-phy-blueprint-30")
    assert paper is not None
    q26 = next((q for q in paper.questions if q.number == 26), None)
    assert q26 is not None

    assert q26.correct_answer == "50"
    u_ms = 72.0 * (5.0 / 18.0)
    a = 4.0
    s_stop = (u_ms ** 2) / (2.0 * a)
    assert round(s_stop, 2) == 50.0


# ==============================================================================
# 2. Provenance & Verification Gating Tests
# ==============================================================================


def test_source_provenance_honesty():
    """
    Verify that authored drills are NOT falsely marked as official past papers,
    and simulated blueprints honestly disclose their simulation provenance.
    """
    # 1. Vectors drill items must be authored_drill, not official
    for qid in ["phy-vec-0001", "phy-vec-0002", "phy-vec-0003"]:
        q = content_loader.get_question_by_id(qid)
        assert q is not None
        assert q.source.type == "authored_drill"
        assert q.verification.tier in ["B", "C"]
        assert q.verification.status == "reviewed"

    # 2. Algebra basics drill items must be authored_drill, not official
    for qid in ["mat-alg-base-0001", "mat-alg-base-0002"]:
        q = content_loader.get_question_by_id(qid)
        assert q is not None
        assert q.source.type == "authored_drill"
        assert q.verification.tier in ["B", "C"]
        assert q.verification.status == "reviewed"

    # 3. Simulated past papers must carry simulated_blueprint provenance
    p_tpat3 = content_loader.get_past_paper_by_id("tpat3-blueprint-70")
    assert p_tpat3 is not None
    assert p_tpat3.source_type == "simulated_blueprint"

    p_phy30 = content_loader.get_past_paper_by_id("alevel-phy-blueprint-30")
    assert p_phy30 is not None
    assert p_phy30.source_type == "simulated_blueprint"


def test_verification_gating():
    """
    Verify that unverified or draft questions are strictly excluded when
    calling get_all_questions(verified_only=True).
    """
    all_q = content_loader.get_all_questions(verified_only=False)
    verified_q = content_loader.get_all_questions(verified_only=True)

    # Every item in verified_q must have status in ('verified', 'reviewed') and tier in ('A', 'B', 'C')
    for q in verified_q:
        assert q.verification.status in ["verified", "reviewed"]
        assert q.verification.tier in ["A", "B", "C"]

    # Temporarily inject a draft question into loader cache
    draft_q = Question(
        id="test-draft-gating-001",
        subject="physics",
        topic="physics.kinematics.1d",
        source=SourceInfo(type="invented", label="Draft Test Item"),
        verification=VerificationInfo(tier="D", status="draft"),
        skills=SkillInfo(primary="testing"),
        stem="ข้อสอบทดสอบ Draft Gating",
        answer=AnswerConfig(type="numeric", correct_value="42"),
    )
    content_loader._questions[draft_q.id] = draft_q

    # Verified query must gate it out
    v_list = content_loader.get_all_questions(verified_only=True)
    assert not any(q.id == draft_q.id for q in v_list)

    # Unverified query must include it
    all_list = content_loader.get_all_questions(verified_only=False)
    assert any(q.id == draft_q.id for q in all_list)

    # Cleanup
    content_loader._questions.pop(draft_q.id, None)


# ==============================================================================
# 3. Content Completeness & Integrity across Entire Catalog
# ==============================================================================


def test_content_completeness_no_placeholders_across_catalog():
    """
    Audits all loaded questions across the platform:
    1. No dummy options (no 'ตัวเลือก 1', 'ตัวเลือก 2' fallback).
    2. No empty stems.
    3. No hesitation or draft phrases in solution.
    4. Exactly 1 correct option for single choice.
    5. Unique IDs across the catalog.
    """
    all_questions = content_loader.get_all_questions()
    assert len(all_questions) >= 87, "Question catalog should contain adapted blueprint questions"

    seen_ids = set()
    hesitation_words = ["รอสักครู่", "หรือถ้า", "อ้อ", "ไม่แน่ใจ", "แก้โจทย์"]

    for q in all_questions:
        # 1. Unique ID
        assert q.id not in seen_ids, f"Duplicate question ID found: {q.id}"
        seen_ids.add(q.id)

        # 2. Non-empty stem
        assert q.stem and q.stem.strip(), f"Question {q.id} has an empty stem"

        # 3. Choice options validation
        if q.answer.type == "single_choice":
            assert q.answer.options is not None, f"Question {q.id} missing options"
            assert len(q.answer.options) >= 2, f"Question {q.id} has fewer than 2 options"

            for opt in q.answer.options:
                assert not opt.text.startswith("ตัวเลือก "), (
                    f"Question {q.id} contains dummy placeholder option: '{opt.text}'"
                )

            correct_opts = [o for o in q.answer.options if o.correct]
            assert len(correct_opts) == 1, (
                f"Question {q.id} must have exactly 1 correct option (found {len(correct_opts)})"
            )

        # 4. Numeric validation
        elif q.answer.type == "numeric":
            assert q.answer.correct_value is not None, f"Numeric question {q.id} missing correct_value"
            try:
                float(str(q.answer.correct_value))
            except ValueError:
                pytest.fail(f"Numeric question {q.id} has invalid correct_value: {q.answer.correct_value}")

        # 5. Solution quality (no draft hesitation)
        sol_text = ""
        if q.solution:
            sol_text += (q.solution.summary or "") + " "
            if q.solution.steps:
                sol_text += " ".join(s.text for s in q.solution.steps)

        for hw in hesitation_words:
            assert hw not in sol_text, (
                f"Question {q.id} contains draft hesitation word '{hw}' in solution: {sol_text[:80]}"
            )


# ==============================================================================
# 4. Mock Exam Parity
# ==============================================================================


def test_mock_exam_parity():
    """
    Ensures that questions displayed, answers graded, and scores in report
    strictly originate from the exact frozen questions_json snapshot.
    """
    session = start_mock_exam("alevel_physics_practice_20")
    sess_id = session["session_id"]
    questions = session["questions"]
    assert len(questions) == 20

    # Build answers: answer first 5 questions correctly, rest incorrectly
    paper = content_loader.get_past_paper_by_id("alevel-phy-2566-mock")
    assert paper is not None
    paper_q_map = {q.number: q for q in paper.questions}

    answers = {}
    expected_score = 0.0

    for i, q in enumerate(questions):
        num = q["number"]
        pq = paper_q_map[num]
        if i < 5:
            # Answer correctly
            answers[str(num)] = str(pq.correct_answer)
            expected_score += float(pq.score)
        else:
            # Answer wrong
            answers[str(num)] = "wrong_parity_test_choice"

    report = submit_mock_exam(sess_id, answers)
    assert report["total_questions"] == 20
    assert report["correct_count"] == 5
    assert round(report["total_score"], 1) == round(expected_score, 1)

    # Parity check: each detailed result must match the frozen session question
    for res in report["detailed_results"]:
        q_matching = next(q for q in questions if q["number"] == res["number"])
        assert q_matching["question_id"] == res["question_id"]
        assert q_matching["topic"] == res["topic"]
