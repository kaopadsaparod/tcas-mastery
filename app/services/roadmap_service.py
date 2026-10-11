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

        # Fetch attempt stats per topic
        cursor.execute("""
            SELECT topic,
                   COUNT(*) as total_attempts,
                   SUM(CASE WHEN status = 'correct_first_try' THEN 1 ELSE 0 END) as first_try_correct
            FROM attempts
            GROUP BY topic
        """)
        attempt_map = {r["topic"]: r for r in cursor.fetchall()}

    for t in topics:
        stat = attempt_map.get(t["topic_id"])
        if stat and stat["total_attempts"] > 0:
            tot = stat["total_attempts"]
            first_try = stat["first_try_correct"]
            mastery = round((first_try / tot) * 100, 1)
        else:
            tot = 0
            first_try = 0
            mastery = 0.0

        t["total_attempts"] = tot
        t["first_try_correct"] = first_try
        t["current_mastery_pct"] = mastery
        t["is_goal_met"] = mastery >= t["target_score_pct"] and tot >= 3

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

        # Swap order_index
        curr_order = curr_topic["order_index"]
        target_order = target_topic["order_index"]

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE topic_priorities SET order_index = ? WHERE topic_id = ?",
                (target_order, curr_topic["topic_id"]),
            )
            cursor.execute(
                "UPDATE topic_priorities SET order_index = ? WHERE topic_id = ?",
                (curr_order, target_topic["topic_id"]),
            )
