from datetime import date, datetime
from typing import Any

from app.database import get_db


def get_exam_countdown() -> dict[str, Any]:
    """
    Calculates remaining time for TCAS exams (TGAT/TPAT and A-Level).
    """
    today = date.today()

    # Retrieve custom exam dates from DB if set, else use defaults
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM app_settings WHERE key = 'tpat_exam_date'")
        tpat_row = cursor.fetchone()
        cursor.execute("SELECT value FROM app_settings WHERE key = 'alevel_exam_date'")
        alevel_row = cursor.fetchone()

    tpat_date_str = tpat_row["value"] if tpat_row else "2027-01-30"
    alevel_date_str = alevel_row["value"] if alevel_row else "2027-03-20"

    tpat_target = datetime.strptime(tpat_date_str, "%Y-%m-%d").date()
    alevel_target = datetime.strptime(alevel_date_str, "%Y-%m-%d").date()

    tpat_days = max(0, (tpat_target - today).days)
    alevel_days = max(0, (alevel_target - today).days)

    return {
        "today_str": today.strftime("%d %b %Y"),
        "tpat_target_date": tpat_date_str,
        "tpat_days_left": tpat_days,
        "tpat_weeks_left": round(tpat_days / 7, 1),
        "alevel_target_date": alevel_date_str,
        "alevel_days_left": alevel_days,
        "alevel_weeks_left": round(alevel_days / 7, 1),
    }


def get_roadmap_topics() -> list[dict[str, Any]]:
    """
    Returns all syllabus topics sorted by user's priority level and custom order.
    Calculates real mastery percentages from user's attempt history.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT topic_id, subject, topic_name, priority_level, target_score_pct, notes, order_index
            FROM topic_priorities
            ORDER BY priority_level ASC, order_index ASC
        """)
        rows = cursor.fetchall()
        topics = [dict(r) for r in rows]

        # 1. Total attempts and raw first-try counts per topic
        cursor.execute("""
            SELECT topic,
                   COUNT(*) as total_attempts,
                   SUM(CASE WHEN status = 'correct_first_try' THEN 1 ELSE 0 END) as first_try_correct
            FROM attempts
            GROUP BY topic
        """)
        attempt_map = {r["topic"]: dict(r) for r in cursor.fetchall()}

        # 2. First Attempt Accuracy on unique questions
        cursor.execute("""
            WITH first_attempts AS (
                SELECT question_id, topic, is_correct, hints_opened,
                       ROW_NUMBER() OVER (PARTITION BY question_id ORDER BY id ASC) as rn
                FROM attempts
            )
            SELECT topic,
                   COUNT(*) as unique_questions_attempted,
                   SUM(CASE WHEN is_correct = 1 AND hints_opened = 0 THEN 1 ELSE 0 END) as first_try_unassisted
            FROM first_attempts
            WHERE rn = 1
            GROUP BY topic
        """)
        first_attempt_map = {r["topic"]: dict(r) for r in cursor.fetchall()}

        # 3. Recent Accuracy on unique questions (latest attempt reflects current ability)
        cursor.execute("""
            WITH latest_attempts AS (
                SELECT question_id, topic, is_correct, confidence,
                       ROW_NUMBER() OVER (PARTITION BY question_id ORDER BY id DESC) as rn
                FROM attempts
            )
            SELECT topic,
                   SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as recent_correct,
                   SUM(CASE WHEN is_correct = 1 AND confidence IN ('sure', 'unsure') THEN 1 ELSE 0 END) as recent_mastered
            FROM latest_attempts
            WHERE rn = 1
            GROUP BY topic
        """)
        latest_attempt_map = {r["topic"]: dict(r) for r in cursor.fetchall()}

        # 4. Spaced repetition queue retention
        cursor.execute("""
            SELECT topic,
                   COUNT(*) as in_queue,
                   SUM(CASE WHEN repetition_count >= 2 THEN 1 ELSE 0 END) as retained_items
            FROM review_queue
            GROUP BY topic
        """)
        queue_map = {r["topic"]: dict(r) for r in cursor.fetchall()}

    for t in topics:
        tid = t["topic_id"]
        stat = attempt_map.get(tid, {})
        first_stat = first_attempt_map.get(tid, {})
        latest_stat = latest_attempt_map.get(tid, {})
        q_stat = queue_map.get(tid, {})

        tot_attempts = stat.get("total_attempts", 0)
        first_try_correct = stat.get("first_try_correct", 0)

        unique_q = first_stat.get("unique_questions_attempted", 0)
        first_unassisted = first_stat.get("first_try_unassisted", 0)
        recent_correct = latest_stat.get("recent_correct", 0)
        retained = q_stat.get("retained_items", 0)

        if unique_q == 0:
            first_acc = 0.0
            recent_acc = 0.0
            mastery_pct = 0.0
            confidence_level = "not_enough_data"
            sufficiency = "not_enough_data"
        else:
            first_acc = round((first_unassisted / unique_q) * 100, 1)
            recent_acc = round((recent_correct / unique_q) * 100, 1)

            # Sample size weight: at least 3 unique questions needed for full confidence
            sample_weight = min(1.0, unique_q / 3.0)

            # Current mastery: 35% first try + 65% recent ability, scaled by sample size
            # plus retention bonus for spaced repetition stability
            retention_bonus = min(10.0, retained * 5.0)
            base_skill = (0.35 * first_acc) + (0.65 * recent_acc)
            mastery_pct = round(min(100.0, (base_skill * sample_weight) + retention_bonus), 1)

            if unique_q >= 3:
                sufficiency = "sufficient"
                confidence_level = "high" if recent_acc >= 75.0 else "medium"
            else:
                sufficiency = "minimal"
                confidence_level = "low"

        t["total_attempts"] = tot_attempts
        t["first_try_correct"] = first_try_correct
        t["unique_questions_attempted"] = unique_q
        t["first_attempt_accuracy"] = first_acc
        t["recent_accuracy"] = recent_acc
        t["current_mastery_pct"] = mastery_pct
        t["mastery_confidence"] = confidence_level
        t["sufficiency"] = sufficiency
        t["is_goal_met"] = (mastery_pct >= t["target_score_pct"]) and (unique_q >= 3)

    return topics


def update_topic_priority(
    topic_id: str,
    priority_level: int,
    order_index: int | None = None,
    target_score_pct: float = 80.0,
    notes: str | None = None,
) -> None:
    """Updates an existing topic's priority and targets while preserving order_index."""
    with get_db() as conn:
        cursor = conn.cursor()
        if order_index is not None and order_index > 0:
            if notes is not None:
                cursor.execute(
                    """
                    UPDATE topic_priorities
                    SET priority_level = ?, order_index = ?, target_score_pct = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE topic_id = ?
                """,
                    (priority_level, order_index, target_score_pct, notes, topic_id),
                )
            else:
                cursor.execute(
                    """
                    UPDATE topic_priorities
                    SET priority_level = ?, order_index = ?, target_score_pct = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE topic_id = ?
                """,
                    (priority_level, order_index, target_score_pct, topic_id),
                )
        else:
            if notes is not None:
                cursor.execute(
                    """
                    UPDATE topic_priorities
                    SET priority_level = ?, target_score_pct = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE topic_id = ?
                """,
                    (priority_level, target_score_pct, notes, topic_id),
                )
            else:
                cursor.execute(
                    """
                    UPDATE topic_priorities
                    SET priority_level = ?, target_score_pct = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE topic_id = ?
                """,
                    (priority_level, target_score_pct, topic_id),
                )


def add_custom_topic(
    topic_id: str,
    subject: str,
    topic_name: str,
    priority_level: int = 1,
    target_score_pct: float = 80.0,
    notes: str = "",
) -> None:
    """Inserts a new topic into the study roadmap."""
    with get_db() as conn:
        cursor = conn.cursor()
        # Find max order index
        cursor.execute(
            "SELECT COALESCE(MAX(order_index), 0) + 1 as next_idx FROM topic_priorities"
        )
        next_idx = cursor.fetchone()["next_idx"]

        cursor.execute(
            """
            INSERT INTO topic_priorities (topic_id, subject, topic_name, priority_level, target_score_pct, notes, order_index)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(topic_id) DO UPDATE SET
                subject = excluded.subject,
                topic_name = excluded.topic_name,
                priority_level = excluded.priority_level,
                target_score_pct = excluded.target_score_pct,
                notes = excluded.notes,
                updated_at = CURRENT_TIMESTAMP
        """,
            (
                topic_id,
                subject,
                topic_name,
                priority_level,
                target_score_pct,
                notes,
                next_idx,
            ),
        )


def reorder_topic_priority(topic_id: str, direction: str) -> None:
    """
    Moves a topic up or down within its priority group.
    direction is 'up' or 'down'.
    """
    topics = get_roadmap_topics()
    idx = next((i for i, t in enumerate(topics) if t["topic_id"] == topic_id), -1)
    if idx == -1:
        return

    swap_idx = idx - 1 if direction == "up" else idx + 1
    if 0 <= swap_idx < len(topics):
        curr_topic = topics[idx]
        target_topic = topics[swap_idx]

        curr_order = curr_topic["order_index"]
        target_order = target_topic["order_index"]

        with get_db() as conn:
            cursor = conn.cursor()
            if curr_order == target_order:
                # If order indices are tied, normalize sequential order first then swap
                for i, t in enumerate(topics, 1):
                    cursor.execute(
                        "UPDATE topic_priorities SET order_index = ? WHERE topic_id = ?",
                        (i, t["topic_id"]),
                    )
                cursor.execute(
                    "UPDATE topic_priorities SET order_index = ? WHERE topic_id = ?",
                    (swap_idx + 1, curr_topic["topic_id"]),
                )
                cursor.execute(
                    "UPDATE topic_priorities SET order_index = ? WHERE topic_id = ?",
                    (idx + 1, target_topic["topic_id"]),
                )
            else:
                cursor.execute(
                    "UPDATE topic_priorities SET order_index = ? WHERE topic_id = ?",
                    (target_order, curr_topic["topic_id"]),
                )
                cursor.execute(
                    "UPDATE topic_priorities SET order_index = ? WHERE topic_id = ?",
                    (curr_order, target_topic["topic_id"]),
                )
