"""
End-to-End (E2E) Content Verification Suite for TCAS Mastery.

Verifies end-to-end ingestion, schema compliance, blueprint scoring invariants,
and pedagogical explanation quality across TGAT1, TGAT3, and TPAT3.

Designed to execute cleanly at Milestone 1 baseline and automatically gate
upcoming content in Milestone 2 (TGAT1), Milestone 3 (TGAT3), and Milestone 4 (TPAT3).
"""

import pytest

from app.database import init_db
from app.models.content_schema import (
    AnswerConfig,
    ChoiceOption,
    FullSolution,
    Hint,
    PastPaper,
    PastPaperQuestion,
    Question,
    SkillInfo,
    SolutionStep,
    SourceInfo,
    VerificationInfo,
)
from app.services.content_loader import content_loader
from app.services.mock_exam import EXAM_BLUEPRINTS, start_mock_exam, submit_mock_exam
from app.services.review_engine import PACE_TARGETS, evaluate_pace

HESITATION_WORDS = ["รอสักครู่", "หรือถ้า", "อ้อ", "ไม่แน่ใจ", "แก้โจทย์", "placeholder", "TODO", "TBD"]


@pytest.fixture(autouse=True)
def setup_content_and_db():
    init_db()
    content_loader.reload()


# ==============================================================================
# 1. Pydantic Schema Model Ingestion Contracts
# ==============================================================================


def test_e2e_schema_contract_tgat1_model_conformance():
    """
    Validates that TGAT1 questions strictly adhere to Pydantic models with
    authentic choice options, distractor error tags, explanations, and step-by-step solutions.
    """
    sample_speaking_q = Question(
        id="tgat1-spk-demo-001",
        subject="tgat1",
        topic="tgat1.speaking.question_response",
        source=SourceInfo(type="authored_drill", label="TGAT1 Speaking Practice"),
        verification=VerificationInfo(tier="A", status="verified", verified_by="academic_lead"),
        skills=SkillInfo(primary="social_interaction", secondary=["polite_refusal"]),
        stem="A colleague asks: 'Could you help me review this project proposal this afternoon?' Which is the most appropriate polite response?",
        answer=AnswerConfig(
            type="single_choice",
            options=[
                ChoiceOption(
                    id="1",
                    text="I'd love to, but I have a client presentation until 4 PM.",
                    correct=True,
                    explanation="Direct, polite, and gives a clear professional reason.",
                ),
                ChoiceOption(
                    id="2",
                    text="No, I am too busy with other things.",
                    correct=False,
                    error_tag="tone_too_blunt",
                    explanation="Too blunt and unprofessional for workplace communication.",
                ),
                ChoiceOption(
                    id="3",
                    text="Never mind about your proposal.",
                    correct=False,
                    error_tag="inappropriate_idiom_usage",
                    explanation="'Never mind' is used to dismiss one's own previous statement, not a colleague's request.",
                ),
                ChoiceOption(
                    id="4",
                    text="Yes, you should review it yourself.",
                    correct=False,
                    error_tag="condescending_tone",
                    explanation="Unhelpful and condescending.",
                ),
            ],
        ),
        difficulty=3,
        estimated_seconds=60,
        hints=[
            Hint(level=1, text="Look for a response that maintains professional politeness while stating availability."),
        ],
        solution=FullSolution(
            summary="Option 1 is the most appropriate workplace refusal because it expresses willingness while giving a valid reason.",
            steps=[
                SolutionStep(id="s1", text="Analyze the situation: a colleague makes a polite request for assistance."),
                SolutionStep(id="s2", text="Evaluate Option 1: combines positive acknowledgment with a valid schedule constraint."),
                SolutionStep(id="s3", text="Reject Options 2, 3, and 4 due to inappropriate tone and idiom misuse."),
            ],
        ),
    )

    assert sample_speaking_q.id == "tgat1-spk-demo-001"
    assert sample_speaking_q.subject == "tgat1"
    assert sample_speaking_q.answer.type == "single_choice"
    assert len(sample_speaking_q.answer.options) == 4
    correct_count = sum(1 for opt in sample_speaking_q.answer.options if opt.correct)
    assert correct_count == 1

    # Check distractor error tags
    for opt in sample_speaking_q.answer.options:
        if not opt.correct:
            assert opt.error_tag is not None, f"Distractor {opt.id} must carry an error_tag"
            assert opt.explanation is not None, f"Distractor {opt.id} must explain the error"


def test_e2e_schema_contract_tgat3_model_conformance():
    """
    Validates that TGAT3 questions strictly adhere to Pydantic models across
    its 4 competency domains (Value Creation, Problem Solving, Emotional Governance, Civic Engagement).
    """
    sample_problem_solving_q = Question(
        id="tgat3-cps-demo-001",
        subject="tgat3",
        topic="tgat3.complex_problem_solving",
        source=SourceInfo(type="authored_drill", label="TGAT3 Problem Solving Scenario"),
        verification=VerificationInfo(tier="A", status="verified", verified_by="academic_lead"),
        skills=SkillInfo(primary="root_cause_analysis", secondary=["evidence_evaluation"]),
        stem="ยอดขายของร้านค้าออนไลน์ลดลง 30% อย่างต่อเนื่องในรอบ 2 เดือนที่ผ่านมา ในฐานะผู้จัดการฝ่ายการตลาด ขั้นตอนแรกที่ควรดำเนินการคือข้อใด",
        answer=AnswerConfig(
            type="single_choice",
            options=[
                ChoiceOption(
                    id="1",
                    text="รวบรวมข้อมูล Customer Journey และอัตราการยกเลิกคำสั่งซื้อเพื่อวิเคราะห์สาเหตุที่แท้จริง",
                    correct=True,
                    explanation="การวิเคราะห์ข้อมูลและหาสาเหตุรากเหง้า (Root Cause) เป็นขั้นตอนแรกตามกระบวนการแก้ปัญหาอย่างเป็นระบบ",
                ),
                ChoiceOption(
                    id="2",
                    text="จัดโปรโมชันลดราคา 50% ทันทีเพื่อกระตุ้นยอดขายกลับมา",
                    correct=False,
                    error_tag="symptomatic_treatment",
                    explanation="การลดราคาเป็นการแก้ปัญหาเฉพาะหน้าที่ปลายเหตุ และอาจทำลายกำไรโดยไม่ทราบสาเหตุที่แท้จริง",
                ),
                ChoiceOption(
                    id="3",
                    text="เปลี่ยนทีมงานฝ่ายขายและบริการลูกค้าทั้งหมด",
                    correct=False,
                    error_tag="premature_blame_without_evidence",
                    explanation="การลงโทษหรือเปลี่ยนทีมงานโดยไม่มีข้อมูลชี้ชัดเป็นการด่วนสรุป",
                ),
                ChoiceOption(
                    id="4",
                    text="เพิ่มงบโฆษณาเป็น 2 เท่าในทุกแพลตฟอร์ม",
                    correct=False,
                    error_tag="resource_waste_without_diagnosis",
                    explanation="เพิ่มงบประมาณโดยไม่ปรับปรุงจุดบกพร่องจะทำให้สูญเสียงบโดยเปล่าประโยชน์",
                ),
            ],
        ),
        difficulty=3,
        estimated_seconds=60,
        solution=FullSolution(
            summary="ขั้นตอนแรกของการแก้ปัญหาที่ซับซ้อนคือการรวบรวมข้อมูลเพื่อระบุสาเหตุที่แท้จริง (Define & Analyze the Problem)",
            steps=[
                SolutionStep(id="s1", text="ประเมินสถานการณ์: ยอดขายตก 30% เป็นผลลัพธ์ (Symptom) ยังไม่ใช่สาเหตุ"),
                SolutionStep(id="s2", text="ใช้หลัก Root Cause Analysis: ต้องรวบรวมข้อมูลเชิงประจักษ์ (Data) ก่อนตัดสินใจลงมือแก้"),
                SolutionStep(id="s3", text="สรุปว่าตัวเลือก 1 ถูกต้อง ส่วนตัวเลือก 2, 3, 4 เป็นการแก้ปัญหาแบบกระโดดข้ามขั้นตอน"),
            ],
        ),
    )

    assert sample_problem_solving_q.id == "tgat3-cps-demo-001"
    assert sample_problem_solving_q.subject == "tgat3"
    assert len(sample_problem_solving_q.answer.options) == 4
    for opt in sample_problem_solving_q.answer.options:
        if not opt.correct:
            assert opt.error_tag is not None
            assert opt.explanation is not None


def test_e2e_schema_contract_tpat3_model_conformance():
    """
    Validates TPAT3 numerical and multiple-choice schema structures.
    """
    sample_tpat3_q = Question(
        id="tpat3-demo-001",
        subject="tpat3",
        topic="tpat3.quantitative",
        source=SourceInfo(type="simulated_blueprint", label="TPAT3 Quantitative Item"),
        verification=VerificationInfo(tier="B", status="verified"),
        skills=SkillInfo(primary="geometric_progression"),
        stem="ลวดเส้นหนึ่งยาว 81 ซม. ตัดออก 1/3 ของความยาวที่เหลือ ทำซ้ำทั้งหมด 3 ครั้ง ความยาวลวดที่เหลือคือเท่าใด",
        answer=AnswerConfig(
            type="single_choice",
            options=[
                ChoiceOption(id="1", text="16 cm", correct=False, error_tag="subtracted_cut_amount_once", explanation="คำนวณส่วนที่ถูกตัดแทนส่วนที่เหลือ"),
                ChoiceOption(id="2", text="24 cm", correct=True, explanation="81 * (2/3)^3 = 81 * 8/27 = 24 cm"),
                ChoiceOption(id="3", text="27 cm", correct=False, error_tag="used_1_third_exponent", explanation="ใช้ (1/3)^3 แทน (2/3)^3"),
                ChoiceOption(id="4", text="32 cm", correct=False, error_tag="arithmetic_subtraction_error", explanation="ลบออกทีละ 27 ซม."),
                ChoiceOption(id="5", text="36 cm", correct=False, error_tag="stopped_at_2_cuts", explanation="ตัดเพียง 2 ครั้ง"),
            ],
        ),
        solution=FullSolution(
            summary="ความยาวลวดที่เหลือหลังจากตัด 3 ครั้งเท่ากับ 24 ซม.",
            steps=[
                SolutionStep(id="s1", text="แต่ละครั้งตัดออก 1/3 จะเหลือ 2/3 ของความยาวเดิม"),
                SolutionStep(id="s2", text="ทำซ้ำ 3 ครั้ง ความยาวที่เหลือ = 81 × (2/3)³ = 81 × 8/27 = 24 ซม."),
            ],
        ),
    )

    assert sample_tpat3_q.subject == "tpat3"
    assert len(sample_tpat3_q.answer.options) == 5
    correct_opts = [o for o in sample_tpat3_q.answer.options if o.correct]
    assert len(correct_opts) == 1
    assert correct_opts[0].id == "2"


# ==============================================================================
# 2. Live Content Loading & Schema Conformance by Subject
# ==============================================================================


def test_e2e_tpat3_content_loaded_and_valid():
    """
    Verifies that TPAT3 content currently in the repository loads cleanly,
    contains at least 70 questions, and passes all schema invariants.
    """
    tpat3_questions = content_loader.get_questions_by_subject("tpat3")
    assert len(tpat3_questions) >= 70, (
        f"TPAT3 catalog must contain at least 70 questions (found {len(tpat3_questions)})"
    )

    seen_ids = set()
    for q in tpat3_questions:
        # Unique ID
        assert q.id not in seen_ids, f"Duplicate TPAT3 question ID: {q.id}"
        seen_ids.add(q.id)

        # Subject & Stem
        assert q.subject == "tpat3"
        assert q.stem and q.stem.strip(), f"TPAT3 question {q.id} has empty stem"

        # Single choice validation
        if q.answer.type == "single_choice":
            assert q.answer.options is not None and len(q.answer.options) >= 2
            correct = [o for o in q.answer.options if o.correct]
            assert len(correct) == 1, f"TPAT3 question {q.id} must have exactly 1 correct option"
            for opt in q.answer.options:
                assert not opt.text.startswith("ตัวเลือก "), f"TPAT3 {q.id} contains dummy option text"
        elif q.answer.type == "numeric":
            assert q.answer.correct_value is not None
            float(str(q.answer.correct_value))


def test_e2e_tgat1_content_loaded_and_valid():
    """
    Verifies TGAT1 questions once ingested in Milestone 2.
    Gracefully skips at Milestone 1 baseline if content files do not yet exist.
    """
    tgat1_questions = content_loader.get_questions_by_subject("tgat1")
    if not tgat1_questions:
        pytest.skip("TGAT1 content files not yet ingested (Milestone 2 target)")

    assert len(tgat1_questions) >= 60, (
        f"TGAT1 catalog must contain at least 60 questions once ingested (found {len(tgat1_questions)})"
    )

    seen_ids = set()
    for q in tgat1_questions:
        assert q.id not in seen_ids, f"Duplicate TGAT1 question ID: {q.id}"
        seen_ids.add(q.id)
        assert q.subject == "tgat1"
        assert q.stem and q.stem.strip()
        assert q.answer.type == "single_choice"
        assert q.answer.options is not None and len(q.answer.options) in (4, 5)

        correct = [o for o in q.answer.options if o.correct]
        assert len(correct) == 1, f"TGAT1 question {q.id} must have exactly 1 correct option"

        for opt in q.answer.options:
            assert not opt.text.startswith("ตัวเลือก "), f"TGAT1 {q.id} contains placeholder option"


def test_e2e_tgat3_content_loaded_and_valid():
    """
    Verifies TGAT3 questions once ingested in Milestone 3.
    Gracefully skips at Milestone 1 baseline if content files do not yet exist.
    """
    tgat3_questions = content_loader.get_questions_by_subject("tgat3")
    if not tgat3_questions:
        pytest.skip("TGAT3 content files not yet ingested (Milestone 3 target)")

    assert len(tgat3_questions) >= 60, (
        f"TGAT3 catalog must contain at least 60 questions once ingested (found {len(tgat3_questions)})"
    )

    seen_ids = set()
    for q in tgat3_questions:
        assert q.id not in seen_ids, f"Duplicate TGAT3 question ID: {q.id}"
        seen_ids.add(q.id)
        assert q.subject == "tgat3"
        assert q.stem and q.stem.strip()
        assert q.answer.type == "single_choice"
        assert q.answer.options is not None and len(q.answer.options) in (4, 5)

        correct = [o for o in q.answer.options if o.correct]
        assert len(correct) == 1, f"TGAT3 question {q.id} must have exactly 1 correct option"

        for opt in q.answer.options:
            assert not opt.text.startswith("ตัวเลือก "), f"TGAT3 {q.id} contains placeholder option"


# ==============================================================================
# 3. Blueprint Accuracy & Score Math Invariants
# ==============================================================================


def test_e2e_blueprint_tpat3_70_scoring_and_structure():
    """
    Official MyTCAS Structure for TPAT3:
    70 questions, 100.0 points total, 180 minutes.
    Part 1 (Q1-45): 45 questions = 60.0 points (Numerical 20 pts, Spatial 20 pts, Mechanical 20 pts)
    Part 2 (Q46-70): 25 questions = 40.0 points (Science Thinking 24 pts, Logic Awareness 16 pts, 1.6 pts each)
    Ratio = 60 : 40.
    """
    paper = content_loader.get_past_paper_by_id("tpat3-blueprint-70")
    assert paper is not None, "TPAT3 blueprint 70 must be loaded"
    assert len(paper.questions) == 70, f"TPAT3 blueprint must have 70 items, got {len(paper.questions)}"
    assert paper.time_limit_min == 180

    part1_questions = [q for q in paper.questions if 1 <= q.number <= 45]
    part2_questions = [q for q in paper.questions if 46 <= q.number <= 70]

    assert len(part1_questions) == 45
    assert len(part2_questions) == 25

    sec1_num = [q for q in paper.questions if 1 <= q.number <= 15]
    sec2_spa = [q for q in paper.questions if 16 <= q.number <= 30]
    sec3_mec = [q for q in paper.questions if 31 <= q.number <= 45]
    sec4_sci = [q for q in paper.questions if 46 <= q.number <= 60]
    sec5_log = [q for q in paper.questions if 61 <= q.number <= 70]

    assert len(sec1_num) == 15
    assert len(sec2_spa) == 15
    assert len(sec3_mec) == 15
    assert len(sec4_sci) == 15
    assert len(sec5_log) == 10

    # Part 1: exactly 20.0 pts per section, 60.0 pts total
    assert round(sum(q.score for q in sec1_num), 1) == 20.0
    assert round(sum(q.score for q in sec2_spa), 1) == 20.0
    assert round(sum(q.score for q in sec3_mec), 1) == 20.0
    assert round(sum(q.score for q in part1_questions), 1) == 60.0

    # Part 2: 24.0 pts (Sec 4) + 16.0 pts (Sec 5) = 40.0 pts total (1.6 pts each)
    for q in part2_questions:
        assert q.score == 1.6
    assert round(sum(q.score for q in sec4_sci), 1) == 24.0
    assert round(sum(q.score for q in sec5_log), 1) == 16.0
    assert round(sum(q.score for q in part2_questions), 1) == 40.0

    # Grand total: exactly 100.0 pts
    assert round(sum(q.score for q in paper.questions), 1) == 100.0


def test_e2e_blueprint_tgat1_60_scoring_and_structure():
    """
    Official MyTCAS Structure for TGAT1 (English Communication):
    60 questions, 100.0 points total, 60 minutes.
    Part 1 Speaking: 30 questions (Q1-30) = 50.0 points (1.6666666666666667 pts each):
      - Question-Response: 10 items (Q1-10)
      - Short Conversations: 10 items (Q11-20)
      - Long Conversations: 10 items (Q21-30)
    Part 2 Reading: 30 questions (Q31-60) = 50.0 points (1.6666666666666667 pts each):
      - Text Completion: 15 items (Q31-45)
      - Reading Comprehension: 15 items (Q46-60)
    Total = 100.0 points (50 : 50 ratio).
    """
    paper = content_loader.get_past_paper_by_id("tgat1-blueprint-60")
    if paper is None:
        pytest.skip("tgat1-blueprint-60 not ingested yet (Milestone 2 target)")

    assert len(paper.questions) == 60, f"TGAT1 blueprint must have 60 items, got {len(paper.questions)}"
    assert paper.time_limit_min == 60

    speaking = [q for q in paper.questions if 1 <= q.number <= 30]
    reading = [q for q in paper.questions if 31 <= q.number <= 60]

    assert len(speaking) == 30
    assert len(reading) == 30

    qr_items = [q for q in paper.questions if 1 <= q.number <= 10]
    sc_items = [q for q in paper.questions if 11 <= q.number <= 20]
    lc_items = [q for q in paper.questions if 21 <= q.number <= 30]
    tc_items = [q for q in paper.questions if 31 <= q.number <= 45]
    rc_items = [q for q in paper.questions if 46 <= q.number <= 60]

    assert len(qr_items) == 10
    assert len(sc_items) == 10
    assert len(lc_items) == 10
    assert len(tc_items) == 15
    assert len(rc_items) == 15

    score_speaking = sum(q.score for q in speaking)
    score_reading = sum(q.score for q in reading)
    total_score = sum(q.score for q in paper.questions)

    assert round(score_speaking, 1) == 50.0
    assert round(score_reading, 1) == 50.0
    assert round(total_score, 1) == 100.0


def test_e2e_blueprint_tgat3_60_scoring_and_structure():
    """
    Official MyTCAS Structure for TGAT3 (Future Workforce Competencies):
    60 questions, 100.0 points total, 60 minutes.
    4 sections of 15 questions = 25.0 points each (1.6666666666666667 pts each):
      - Section 1: Value Creation & Innovation (Q1-15) = 25.0 pts
      - Section 2: Complex Problem Solving (Q16-30) = 25.0 pts
      - Section 3: Emotional Governance (Q31-45) = 25.0 pts
      - Section 4: Civic Engagement (Q46-60) = 25.0 pts
    Total = 100.0 points (25 : 25 : 25 : 25 ratio).
    """
    paper = content_loader.get_past_paper_by_id("tgat3-blueprint-60")
    if paper is None:
        pytest.skip("tgat3-blueprint-60 not ingested yet (Milestone 3 target)")

    assert len(paper.questions) == 60, f"TGAT3 blueprint must have 60 items, got {len(paper.questions)}"
    assert paper.time_limit_min == 60

    sec1_val = [q for q in paper.questions if 1 <= q.number <= 15]
    sec2_cps = [q for q in paper.questions if 16 <= q.number <= 30]
    sec3_emg = [q for q in paper.questions if 31 <= q.number <= 45]
    sec4_civ = [q for q in paper.questions if 46 <= q.number <= 60]

    assert len(sec1_val) == 15
    assert len(sec2_cps) == 15
    assert len(sec3_emg) == 15
    assert len(sec4_civ) == 15

    assert round(sum(q.score for q in sec1_val), 1) == 25.0
    assert round(sum(q.score for q in sec2_cps), 1) == 25.0
    assert round(sum(q.score for q in sec3_emg), 1) == 25.0
    assert round(sum(q.score for q in sec4_civ), 1) == 25.0
    assert round(sum(q.score for q in paper.questions), 1) == 100.0


# ==============================================================================
# 4. Pedagogical Quality & Distractor Misconception Analysis
# ==============================================================================


def test_e2e_pedagogical_solutions_non_empty_across_catalog():
    """
    Audits every single loaded question across the platform to ensure:
    - Non-empty step-by-step solution.
    - Solution text length >= 15 characters.
    - Zero hesitation keywords (รอสักครู่, หรือถ้า, อ้อ, ไม่แน่ใจ, แก้โจทย์, etc.).
    """
    all_questions = content_loader.get_all_questions()
    assert len(all_questions) >= 80

    for q in all_questions:
        assert q.solution is not None, f"Question {q.id} missing solution model"

        sol_text = ""
        if q.solution.summary:
            sol_text += q.solution.summary.strip()
        if q.solution.steps:
            sol_text += " " + " ".join(s.text.strip() for s in q.solution.steps)

        assert len(sol_text) >= 15, (
            f"Question {q.id} has insufficient pedagogical solution: '{sol_text}'"
        )

        for hw in HESITATION_WORDS:
            assert hw not in sol_text, (
                f"Question {q.id} contains draft hesitation token '{hw}' in solution"
            )


def test_e2e_pedagogical_zero_placeholders_and_options_integrity():
    """
    Verifies that no question in the catalog contains placeholder options ('ตัวเลือก '),
    that stems are robust (>= 10 chars), and single-choice items have exactly 1 correct option.
    """
    all_questions = content_loader.get_all_questions()
    for q in all_questions:
        assert q.stem and len(q.stem.strip()) >= 10, f"Question {q.id} stem is too short or empty"

        if q.answer.type == "single_choice":
            assert q.answer.options is not None and len(q.answer.options) >= 2
            for opt in q.answer.options:
                assert not opt.text.startswith("ตัวเลือก "), (
                    f"Question {q.id} contains dummy placeholder '{opt.text}'"
                )
                assert len(opt.text.strip()) > 0, f"Question {q.id} has empty option text"

            correct_opts = [o for o in q.answer.options if o.correct]
            assert len(correct_opts) == 1, (
                f"Question {q.id} must have exactly 1 correct option (found {len(correct_opts)})"
            )


def test_e2e_pedagogical_distractor_error_tags_tgat1():
    """
    Verifies that every distractor in TGAT1 carries an error_tag and pedagogical explanation.
    Skips at baseline if TGAT1 is not yet ingested (M2 target).
    """
    tgat1_questions = content_loader.get_questions_by_subject("tgat1")
    if not tgat1_questions:
        pytest.skip("TGAT1 content not yet ingested (Milestone 2 target)")

    for q in tgat1_questions:
        if q.answer.type == "single_choice" and q.answer.options:
            for opt in q.answer.options:
                if not opt.correct:
                    assert opt.error_tag, f"TGAT1 Q {q.id} distractor {opt.id} missing error_tag"
                    assert opt.explanation, f"TGAT1 Q {q.id} distractor {opt.id} missing explanation"


def test_e2e_pedagogical_distractor_error_tags_tgat3():
    """
    Verifies that every distractor in TGAT3 carries an error_tag and pedagogical explanation.
    Skips at baseline if TGAT3 is not yet ingested (M3 target).
    """
    tgat3_questions = content_loader.get_questions_by_subject("tgat3")
    if not tgat3_questions:
        pytest.skip("TGAT3 content not yet ingested (Milestone 3 target)")

    for q in tgat3_questions:
        if q.answer.type == "single_choice" and q.answer.options:
            for opt in q.answer.options:
                if not opt.correct:
                    assert opt.error_tag, f"TGAT3 Q {q.id} distractor {opt.id} missing error_tag"
                    assert opt.explanation, f"TGAT3 Q {q.id} distractor {opt.id} missing explanation"


def test_e2e_pedagogical_distractor_error_tags_tpat3():
    """
    Verifies TPAT3 distractor error tag coverage.
    At Milestone 1 baseline, TPAT3 distractors do not yet carry error tags (scheduled for M4 F11).
    Once Milestone 4 is complete, this test enforces 100% error tag presence on distractors.
    """
    paper = content_loader.get_past_paper_by_id("tpat3-blueprint-70")
    assert paper is not None

    tagged_distractors = sum(
        1
        for q in paper.questions
        if q.options
        for opt in q.options
        if (str(opt.id).strip().lower() != str(q.correct_answer).strip().lower()) and getattr(opt, "error_tag", None)
    )
    total_distractors = sum(
        1
        for q in paper.questions
        if q.options
        for opt in q.options
        if (str(opt.id).strip().lower() != str(q.correct_answer).strip().lower())
    )

    if tagged_distractors == 0:
        pytest.skip("TPAT3 distractor error tags pending Milestone 4 pedagogical upgrade (F11)")

    assert tagged_distractors == total_distractors, (
        f"TPAT3 distractors must 100% carry error tags ({tagged_distractors}/{total_distractors})"
    )


# ==============================================================================
# 5. Mock Exam Full Lifecycle & Scoring Simulation
# ==============================================================================


def test_e2e_mock_exam_simulation_tpat3_70():
    """
    Full simulation of TPAT3 70-question mock exam submission.
    Submitting all correct answers must yield exactly 100.0 points.
    """
    paper = content_loader.get_past_paper_by_id("tpat3-blueprint-70")
    assert paper is not None

    session = start_mock_exam("tpat3_mock_70")
    session_id = session["session_id"]
    assert session["total_questions"] == 70

    answers = {str(q.number): str(q.correct_answer) for q in paper.questions}
    report = submit_mock_exam(session_id, answers)

    assert report["total_questions"] == 70
    assert report["correct_count"] == 70
    assert round(report["total_score"], 1) == 100.0
    assert round(report["max_score"], 1) == 100.0
    assert report["score_percent"] == 100.0


def test_e2e_mock_exam_simulation_tgat1_60():
    """
    Full simulation of TGAT1 60-question mock exam submission.
    Gracefully skips at Milestone 1 if blueprint or paper is not yet registered.
    """
    if "tgat1_mock_60" not in EXAM_BLUEPRINTS or content_loader.get_past_paper_by_id("tgat1-blueprint-60") is None:
        pytest.skip("tgat1_mock_60 blueprint or paper not yet available (Milestone 1/2)")

    paper = content_loader.get_past_paper_by_id("tgat1-blueprint-60")
    assert paper is not None

    session = start_mock_exam("tgat1_mock_60")
    session_id = session["session_id"]
    assert session["total_questions"] == 60

    answers = {str(q.number): str(q.correct_answer) for q in paper.questions}
    report = submit_mock_exam(session_id, answers)

    assert report["total_questions"] == 60
    assert report["correct_count"] == 60
    assert round(report["total_score"], 1) == 100.0


def test_e2e_mock_exam_simulation_tgat3_60():
    """
    Full simulation of TGAT3 60-question mock exam submission.
    Gracefully skips at Milestone 1 if blueprint or paper is not yet registered.
    """
    if "tgat3_mock_60" not in EXAM_BLUEPRINTS or content_loader.get_past_paper_by_id("tgat3-blueprint-60") is None:
        pytest.skip("tgat3_mock_60 blueprint or paper not yet available (Milestone 1/3)")

    paper = content_loader.get_past_paper_by_id("tgat3-blueprint-60")
    assert paper is not None

    session = start_mock_exam("tgat3_mock_60")
    session_id = session["session_id"]
    assert session["total_questions"] == 60

    answers = {str(q.number): str(q.correct_answer) for q in paper.questions}
    report = submit_mock_exam(session_id, answers)

    assert report["total_questions"] == 60
    assert report["correct_count"] == 60
    assert round(report["total_score"], 1) == 100.0


# ==============================================================================
# 6. Pace Targets & Review Engine Invariants
# ==============================================================================


def test_e2e_pace_targets_configured():
    """
    Verifies that pace benchmarks are configured for TPAT3 and evaluates pace feedback.
    Checks TGAT1 / TGAT3 pace targets (60.0s) if present.
    """
    assert "tpat3" in PACE_TARGETS
    assert PACE_TARGETS["tpat3"] == 150.0

    eval_tpat3 = evaluate_pace("tpat3", 140.0)
    assert eval_tpat3["pace_status"] == "optimal"

    eval_slow = evaluate_pace("tpat3", 250.0)
    assert eval_slow["pace_status"] == "slow"

    # TGAT pace targets check
    if "tgat1" in PACE_TARGETS:
        assert PACE_TARGETS["tgat1"] == 60.0
        eval_tgat1 = evaluate_pace("tgat1", 50.0)
        assert eval_tgat1["pace_status"] == "optimal"

    if "tgat3" in PACE_TARGETS:
        assert PACE_TARGETS["tgat3"] == 60.0
