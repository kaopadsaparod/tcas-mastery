import pytest

from app.database import get_db, init_db
from app.services.review_engine import (
    get_learning_stats,
    record_attempt,
)


@pytest.fixture(autouse=True)
def setup_db():
    init_db()
    with get_db() as conn:
        conn.execute("DELETE FROM review_queue;")
        conn.execute("DELETE FROM attempts;")


def test_record_attempt_wrong_sure():
    """Misconception: sure but wrong should be assigned high priority."""
    res = record_attempt(
        question_id="test-q1",
        subject="physics",
        topic="physics.kinematics.1d",
        user_answer="o2",
        is_correct=False,
        status="wrong",
        confidence="sure",
        error_tag="no_unit_conversion",
    )
    assert res["priority"] == "high"
    assert res["interval_days"] == 1


def test_record_attempt_correct_first_try_progression():
    """Progression: correct first try with sure confidence advances spaced interval."""
    res1 = record_attempt(
        question_id="test-q2",
        subject="physics",
        topic="physics.kinematics.1d",
        user_answer="o1",
        is_correct=True,
        status="correct_first_try",
        confidence="sure",
    )
    assert res1["interval_days"] == 3
    assert res1["priority"] == "normal"

    # Second consecutive correct attempt
    res2 = record_attempt(
        question_id="test-q2",
        subject="physics",
        topic="physics.kinematics.1d",
        user_answer="o1",
        is_correct=True,
        status="correct_first_try",
        confidence="sure",
    )
    assert res2["interval_days"] == 7


def test_get_learning_stats():
    stats = get_learning_stats()
    assert "total_attempts" in stats
    assert "honest_mastery_rate" in stats
    assert "top_error_tags" in stats
    assert "topic_breakdown" in stats
