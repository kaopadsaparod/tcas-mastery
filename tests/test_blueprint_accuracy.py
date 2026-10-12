import pytest

from app.database import init_db
from app.services.content_loader import content_loader
from app.services.mock_exam import EXAM_BLUEPRINTS, start_mock_exam, submit_mock_exam


@pytest.fixture(autouse=True)
def setup_content():
    init_db()
    content_loader.reload()


# ==============================================================================
# 1. A-Level Physics Blueprint Score Accuracy (75 : 25)
# ==============================================================================


def test_alevel_physics_blueprint_scoring_structure():
    """
    MyTCAS Official Blueprint for A-Level Physics:
    - 25 Single Choice (MCQ) questions = 75.0 points (3.0 pts / question).
    - 5 Numeric questions = 25.0 points (5.0 pts / question).
    - Total = 30 questions, 100.0 points (75 : 25 ratio).
    """
    paper = content_loader.get_past_paper_by_id("alevel-phy-blueprint-30")
    assert paper is not None
    assert len(paper.questions) == 30

    mcq_questions = [q for q in paper.questions if q.number <= 25]
    numeric_questions = [q for q in paper.questions if q.number > 25]

    assert len(mcq_questions) == 25
    assert len(numeric_questions) == 5

    # Check individual scores and sum
    for q in mcq_questions:
        assert q.score == 3.0, f"A-Level MCQ question {q.number} should be 3.0 pts, got {q.score}"
        assert q.answer_type == "single_choice"

    for q in numeric_questions:
        assert q.score == 5.0, f"A-Level Numeric question {q.number} should be 5.0 pts, got {q.score}"
        assert q.answer_type == "numeric"

    total_mcq_score = sum(q.score for q in mcq_questions)
    total_numeric_score = sum(q.score for q in numeric_questions)
    total_exam_score = total_mcq_score + total_numeric_score

    assert round(total_mcq_score, 1) == 75.0
    assert round(total_numeric_score, 1) == 25.0
    assert round(total_exam_score, 1) == 100.0


# ==============================================================================
# 2. TPAT3 Blueprint Score Accuracy (60 : 40)
# ==============================================================================


def test_tpat3_blueprint_70_scoring_and_section_ratios():
    """
    MyTCAS Official Blueprint for TPAT3:
    Part 1: Aptitude Test (45 questions = 60.0 points):
      - Section 1: Numerical Reasoning (items 1-15, 15 questions = 20.0 pts)
      - Section 2: Spatial Relations (items 16-30, 15 questions = 20.0 pts)
      - Section 3: Mechanical & Physics (items 31-45, 15 questions = 20.0 pts)
    Part 2: Scientific & Technology Thinking & Awareness (25 questions = 40.0 points):
      - Section 4: Science & Tech Thinking (items 46-60, 15 questions = 24.0 pts, 1.6 pts each)
      - Section 5: Logic & Tech Awareness (items 61-70, 10 questions = 16.0 pts, 1.6 pts each)
    Total = 70 questions, 100.0 points (60 : 40 ratio).
    """
    paper = content_loader.get_past_paper_by_id("tpat3-blueprint-70")
    assert paper is not None
    assert len(paper.questions) == 70

    sec1_num = [q for q in paper.questions if 1 <= q.number <= 15]
    sec2_spa = [q for q in paper.questions if 16 <= q.number <= 30]
    sec3_mec = [q for q in paper.questions if 31 <= q.number <= 45]
    part1_questions = [q for q in paper.questions if 1 <= q.number <= 45]

    sec4_sci = [q for q in paper.questions if 46 <= q.number <= 60]
    sec5_log = [q for q in paper.questions if 61 <= q.number <= 70]
    part2_questions = [q for q in paper.questions if 46 <= q.number <= 70]

    assert len(sec1_num) == 15
    assert len(sec2_spa) == 15
    assert len(sec3_mec) == 15
    assert len(part1_questions) == 45

    assert len(sec4_sci) == 15
    assert len(sec5_log) == 10
    assert len(part2_questions) == 25

    # Check scores in Part 1 (sum = 60.0, each section = 20.0)
    score_sec1 = sum(q.score for q in sec1_num)
    score_sec2 = sum(q.score for q in sec2_spa)
    score_sec3 = sum(q.score for q in sec3_mec)
    total_part1 = sum(q.score for q in part1_questions)

    assert round(score_sec1, 1) == 20.0
    assert round(score_sec2, 1) == 20.0
    assert round(score_sec3, 1) == 20.0
    assert round(total_part1, 1) == 60.0

    # Check scores in Part 2 (sum = 40.0, 1.6 pts each)
    for q in part2_questions:
        assert q.score == 1.6

    score_sec4 = sum(q.score for q in sec4_sci)
    score_sec5 = sum(q.score for q in sec5_log)
    total_part2 = sum(q.score for q in part2_questions)

    assert round(score_sec4, 1) == 24.0
    assert round(score_sec5, 1) == 16.0
    assert round(total_part2, 1) == 40.0

    # Total exam score must be 100.0
    assert round(total_part1 + total_part2, 1) == 100.0


# ==============================================================================
# 3. Transparent Titles & Provenance
# ==============================================================================


def test_blueprint_titles_transparent_and_honest():
    """
    Titles should explicitly state that they are simulated blueprints
    based on MyTCAS structures, without misleading 'Official Blueprint' claims.
    """
    p_phy30 = content_loader.get_past_paper_by_id("alevel-phy-blueprint-30")
    assert p_phy30 is not None
    assert "ข้อสอบจำลองตามโครงสร้าง MyTCAS" in p_phy30.title
    assert "Official Blueprint" not in p_phy30.title

    p_tpat3 = content_loader.get_past_paper_by_id("tpat3-blueprint-70")
    assert p_tpat3 is not None
    assert "ข้อสอบจำลองตามโครงสร้าง MyTCAS" in p_tpat3.title
    assert "Official Blueprint" not in p_tpat3.title

    # Blueprint dictionary descriptions must also be honest
    assert "alevel_physics_mock_30" in EXAM_BLUEPRINTS
    desc_phy = EXAM_BLUEPRINTS["alevel_physics_mock_30"]["description"]
    assert "3.0 คะแนน" in desc_phy
    assert "5.0 คะแนน" in desc_phy
    assert "100 คะแนนเต็ม" in desc_phy

    assert "tpat3_mock_70" in EXAM_BLUEPRINTS
    desc_tpat = EXAM_BLUEPRINTS["tpat3_mock_70"]["description"]
    assert "ส่วนที่ 1 ความถนัด 45 ข้อ 60 คะแนน" in desc_tpat
    assert "ส่วนที่ 2 ความคิดและความสนใจ 25 ข้อ 40 คะแนน" in desc_tpat


# ==============================================================================
# 4. Tailored Tutor Hints & Structured Solutions
# ==============================================================================


def test_tailored_tutor_hints_for_blueprints():
    """
    Verify that questions adapted into the practice bank receive skill-specific,
    instructive hints and structured solutions rather than generic copy-pasted text.
    """
    # 1. 1D Kinematics equation choice
    q_kin = content_loader.get_question_by_id("bp30-q01")
    assert q_kin is not None
    assert len(q_kin.hints) >= 2
    hint_texts_kin = [h.text for h in q_kin.hints]
    assert any("5 สูตรการเคลื่อนที่" in t or "ตัวแปรการเคลื่อนที่" in t for t in hint_texts_kin)

    # 2. Work-energy theorem
    q_work = content_loader.get_question_by_id("bp30-q06")
    assert q_work is not None
    hint_texts_work = [h.text for h in q_work.hints]
    assert any("งานของแรงภายนอก" in t or "ΔEk" in t for t in hint_texts_work)

    # 3. Geometric series
    q_geom = content_loader.get_question_by_id("tpat3-70-q14")
    assert q_geom is not None
    hint_texts_geom = [h.text for h in q_geom.hints]
    assert any("2/3" in t or "สัดส่วน" in t for t in hint_texts_geom)

    # 4. 3D Cube rotation
    q_rot = content_loader.get_question_by_id("tpat3-70-q18")
    assert q_rot is not None
    hint_texts_rot = [h.text for h in q_rot.hints]
    assert any("แกนดิ่ง" in t or "แกนนอน" in t for t in hint_texts_rot)


# ==============================================================================
# 5. Mock Exam Lifecycle Scoring Parity
# ==============================================================================


def test_mock_exam_execution_matches_exact_blueprint_scores():
    """
    Simulate full mock exam submissions for both blueprints and verify that
    the scoring engine calculates exact scores matching 75:25 and 60:40 ratios.
    """
    # 1. A-Level Physics 30: Answer all correctly
    sess_phy = start_mock_exam("alevel_physics_mock_30")
    answers_phy = {}
    p_phy = content_loader.get_past_paper_by_id("alevel-phy-blueprint-30")
    for q in p_phy.questions:
        answers_phy[str(q.number)] = str(q.correct_answer)

    rep_phy = submit_mock_exam(sess_phy["session_id"], answers_phy)
    assert rep_phy["total_questions"] == 30
    assert rep_phy["correct_count"] == 30
    assert round(rep_phy["total_score"], 1) == 100.0

    # 2. TPAT3 70: Answer all correctly
    sess_tpat = start_mock_exam("tpat3_mock_70")
    answers_tpat = {}
    p_tpat = content_loader.get_past_paper_by_id("tpat3-blueprint-70")
    for q in p_tpat.questions:
        answers_tpat[str(q.number)] = str(q.correct_answer)

    rep_tpat = submit_mock_exam(sess_tpat["session_id"], answers_tpat)
    assert rep_tpat["total_questions"] == 70
    assert rep_tpat["correct_count"] == 70
    assert round(rep_tpat["total_score"], 1) == 100.0
