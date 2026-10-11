from app.services.content_loader import content_loader
from app.services.grader import grade_attempt, grade_numeric, normalize_numeric_string


def test_normalize_unicode_minus():
    assert normalize_numeric_string("−50") == -50.0
    assert normalize_numeric_string("–12.5") == -12.5
    assert normalize_numeric_string("-4") == -4.0


def test_normalize_thousands_commas():
    assert normalize_numeric_string("1,000") == 1000.0
    assert normalize_numeric_string("25,400.5") == 25400.5


def test_normalize_fractions():
    assert normalize_numeric_string("3/4") == 0.75
    assert normalize_numeric_string("1/2") == 0.5
    assert normalize_numeric_string("-1/4") == -0.25


def test_normalize_scientific_notation():
    assert normalize_numeric_string("2e3") == 2000.0
    assert normalize_numeric_string("3*10^2") == 300.0
    assert normalize_numeric_string("4x10^-1") == 0.4
    assert normalize_numeric_string("5×10^3") == 5000.0


def test_grade_numeric_tolerance():
    assert grade_numeric("80", 80, tolerance=0.01) is True
    assert grade_numeric("80.5", 80, tolerance=0.02) is True  # within 2%
    assert grade_numeric("85", 80, tolerance=0.02) is False  # 5/80 = 6.25% > 2%


def test_grade_attempt_mcq_with_error_tag():
    q = content_loader.get_question_by_id("phy-kin-0001")
    assert q is not None

    # Correct attempt without hints
    res = grade_attempt(q, user_answer="o1", hints_opened=0, confidence="sure")
    assert res.is_correct is True
    assert res.status == "correct_first_try"
    assert res.error_tag is None
    assert res.next_review_interval_days == 3

    # Correct attempt with hints opened
    res_assisted = grade_attempt(q, user_answer="o1", hints_opened=2, confidence="sure")
    assert res_assisted.is_correct is True
    assert res_assisted.status == "correct_assisted"
    assert res_assisted.next_review_interval_days == 1

    # Distractor choice with error tag: o2 = no_unit_conversion
    res_wrong = grade_attempt(q, user_answer="o2", hints_opened=0, confidence="sure")
    assert res_wrong.is_correct is False
    assert res_wrong.status == "wrong"
    assert res_wrong.error_tag == "no_unit_conversion"
    assert "แปลงหน่วย" in res_wrong.error_tag_description


def test_grade_attempt_plan_step():
    q = content_loader.get_question_by_id("phy-kin-0001")
    assert q is not None

    # Correct plan step option 'b'
    res = grade_attempt(q, user_answer="o1", plan_step_answer="b")
    assert res.plan_step_correct is True

    # Wrong plan step option 'a'
    res2 = grade_attempt(q, user_answer="o1", plan_step_answer="a")
    assert res2.plan_step_correct is False
