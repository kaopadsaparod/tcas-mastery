import random
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

from app.database import get_db
from app.models.content_schema import Question
from app.services.content_loader import content_loader

SPACED_INTERVALS = [1, 3, 7, 14, 30]

# Standard examination pace targets (seconds per question)
PACE_TARGETS = {
    "physics": 180.0,  # A-Level Physics: 30 questions in 90 min (3 min/q)
    "math": 180.0,     # A-Level Math 1: 30 questions in 90 min (3 min/q)
    "tpat3": 150.0,    # TPAT3: ~70 questions in 180 min (2.5 min/q)
    "tgat1": 60.0,     # TGAT1 English Communication: 60 questions in 60 min (1 min/q)
    "tgat2": 45.0,     # TGAT2: fast reasoning (80 questions in 60 min = 45s/q)
    "tgat3": 60.0,     # TGAT3 Future Workforce: 60 questions in 60 min (1 min/q)
}


def evaluate_pace(subject: str, time_spent_sec: float) -> dict[str, Any]:
    """
    Evaluates student pace against official exam benchmarks.
    Returns status ('fast', 'optimal', 'slow', 'untracked'), target seconds, and diagnostic feedback.
    """
    target = PACE_TARGETS.get(subject.lower() if subject else "", 180.0)
    if time_spent_sec <= 0:
        return {
            "pace_status": "untracked",
            "pace_target_sec": target,
            "pace_feedback": None,
        }

    if time_spent_sec <= target * 0.75:
        return {
            "pace_status": "fast",
            "pace_target_sec": target,
            "pace_feedback": f"⚡ เร็วกว่าเวลาเป้าหมาย ({round(time_spent_sec, 1)}s / เกณฑ์ {int(target)}s)",
        }
    elif time_spent_sec <= target * 1.15:
        return {
            "pace_status": "optimal",
            "pace_target_sec": target,
            "pace_feedback": f"🎯 อยู่ในเกณฑ์เวลาสอบจริง ({round(time_spent_sec, 1)}s / เกณฑ์ {int(target)}s)",
        }
    else:
        return {
            "pace_status": "slow",
            "pace_target_sec": target,
            "pace_feedback": f"⏳ ช้ากว่าเกณฑ์เวลาสอบ ({round(time_spent_sec, 1)}s / เกณฑ์ {int(target)}s) ควรฝึกบริหารเวลา",
        }


def record_attempt(
    question_id: str,
    subject: str,
    topic: str,
    user_answer: str,
    is_correct: bool,
    status: str,
    confidence: str = "sure",
    hints_opened: int = 0,
    plan_step_answer: str | None = None,
    plan_step_correct: bool | None = None,
    error_tag: str | None = None,
    time_spent_sec: float = 0.0,
    review_time_sec: float = 0.0,
) -> dict[str, Any]:
    """
    Records a user attempt in the database and updates the spaced repetition review queue.
    Executed in a single atomic transaction.
    """
    now = datetime.now(timezone.utc)
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")

    with get_db() as conn:
        cursor = conn.cursor()

        # 1. Insert attempt
        cursor.execute(
            """
            INSERT INTO attempts (
                question_id, subject, topic, user_answer, is_correct, status,
                confidence, hints_opened, plan_step_answer, plan_step_correct,
                error_tag, time_spent_sec, review_time_sec, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                question_id,
                subject,
                topic,
                user_answer,
                1 if is_correct else 0,
                status,
                confidence,
                hints_opened,
                plan_step_answer,
                1
                if plan_step_correct is True
                else (0 if plan_step_correct is False else None),
                error_tag,
                time_spent_sec,
                review_time_sec,
                now_str,
            ),
        )

        # 2. Fetch existing queue record if any
        cursor.execute(
            "SELECT interval_days, repetition_count FROM review_queue WHERE question_id = ?",
            (question_id,),
        )
        row = cursor.fetchone()
        last_interval = row["interval_days"] if row else 1
        rep_count = row["repetition_count"] if row else 0

        # 3. Compute next interval & priority
        is_overconfidence = (confidence == "sure" and not is_correct)
        if not is_correct:
            next_interval = 1
            new_rep = 0
            # High priority if student was sure but was actually wrong (severe misconception)
            priority = "high" if is_overconfidence else "normal"
        elif status == "correct_assisted":
            next_interval = 1
            new_rep = 0
            priority = "normal"
        else:  # correct_first_try
            if confidence == "guessed":
                next_interval = 1  # Reset to 1 day: guessing correctly is not true mastery
                new_rep = 0
                priority = "normal"
            elif confidence == "unsure":
                next_interval = 1 if rep_count == 0 else max(1, last_interval)
                new_rep = rep_count
                priority = "normal"
            else:  # sure
                new_rep = min(rep_count + 1, len(SPACED_INTERVALS) - 1)
                next_interval = SPACED_INTERVALS[new_rep]
                priority = "normal"

        next_review_at = now + timedelta(days=next_interval)
        next_review_str = next_review_at.strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(
            """
            INSERT INTO review_queue (
                question_id, subject, topic, next_review_at, interval_days,
                repetition_count, priority, last_status, last_error_tag, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(question_id) DO UPDATE SET
                subject = excluded.subject,
                topic = excluded.topic,
                next_review_at = excluded.next_review_at,
                interval_days = excluded.interval_days,
                repetition_count = excluded.repetition_count,
                priority = excluded.priority,
                last_status = excluded.last_status,
                last_error_tag = excluded.last_error_tag,
                updated_at = excluded.updated_at
        """,
            (
                question_id,
                subject,
                topic,
                next_review_str,
                next_interval,
                new_rep,
                priority,
                status,
                error_tag,
                now_str,
            ),
        )

    return {
        "question_id": question_id,
        "next_review_at": next_review_str,
        "interval_days": next_interval,
        "priority": priority,
        "is_overconfidence": is_overconfidence,
    }


def get_due_reviews() -> list[dict[str, Any]]:
    """Retrieves all questions due for review today or overdue, ordered by priority."""
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT question_id, subject, topic, next_review_at, interval_days,
                   repetition_count, priority, last_status, last_error_tag
            FROM review_queue
            WHERE next_review_at <= ?
            ORDER BY
                CASE priority WHEN 'high' THEN 1 WHEN 'normal' THEN 2 ELSE 3 END,
                next_review_at ASC
        """,
            (now_str,),
        )
        rows = cursor.fetchall()
        return [dict(r) for r in rows]


def get_learning_stats(verified_only: bool = False) -> dict[str, Any]:
    """
    Computes comprehensive learning analytics, honest mastery metrics,
    confidence calibration curves, and error tags.
    Honest Mastery counts ONLY first-try correct answers where confidence was 'sure' or 'unsure',
    excluding lucky guesses.
    """
    with get_db() as conn:
        cursor = conn.cursor()

        # Build dynamic where condition when filtering only verified questions (Tiers A-C)
        if verified_only:
            verified_questions = content_loader.get_all_questions(verified_only=True)
            verified_qids = [q.id for q in verified_questions]
            if verified_qids:
                placeholders = ",".join("?" for _ in verified_qids)
                where_base = f"question_id IN ({placeholders})"
                base_params = tuple(verified_qids)
            else:
                where_base = "1=0"
                base_params = ()
        else:
            where_base = ""
            base_params = ()

        def build_where(extra_cond: str = "") -> tuple[str, tuple]:
            if where_base and extra_cond:
                return f"WHERE {where_base} AND ({extra_cond})", base_params
            elif where_base:
                return f"WHERE {where_base}", base_params
            elif extra_cond:
                return f"WHERE {extra_cond}", ()
            return "", ()

        # Overall counts
        w, p = build_where()
        cursor.execute(f"SELECT COUNT(*) as total FROM attempts {w}", p)
        total_attempts = cursor.fetchone()["total"]

        # Raw first-try count
        w, p = build_where("status = 'correct_first_try'")
        cursor.execute(f"SELECT COUNT(*) as first_try FROM attempts {w}", p)
        first_try_raw = cursor.fetchone()["first_try"]

        # Honest Mastery: first_try and NOT guessed (requires genuine confidence 'sure' or 'unsure')
        w, p = build_where("status = 'correct_first_try' AND confidence IN ('sure', 'unsure')")
        cursor.execute(f"SELECT COUNT(*) as honest_mastery FROM attempts {w}", p)
        honest_mastery_count = cursor.fetchone()["honest_mastery"]

        # Lucky guesses: correct first try but student was just guessing
        w, p = build_where("status = 'correct_first_try' AND confidence = 'guessed'")
        cursor.execute(f"SELECT COUNT(*) as lucky_guesses FROM attempts {w}", p)
        lucky_guesses = cursor.fetchone()["lucky_guesses"]

        w, p = build_where("status = 'correct_assisted'")
        cursor.execute(f"SELECT COUNT(*) as assisted FROM attempts {w}", p)
        assisted_correct = cursor.fetchone()["assisted"]

        w, p = build_where("is_correct = 0")
        cursor.execute(f"SELECT COUNT(*) as wrong FROM attempts {w}", p)
        wrong_count = cursor.fetchone()["wrong"]

        # Average thinking time and review time
        w, p = build_where()
        cursor.execute(
            f"SELECT AVG(time_spent_sec) as avg_think, AVG(review_time_sec) as avg_review FROM attempts {w}",
            p,
        )
        time_row = cursor.fetchone()
        avg_think = round(time_row["avg_think"] or 0, 1)
        avg_review = round(time_row["avg_review"] or 0, 1)

        # High priority misconceptions (sure but wrong)
        w, p = build_where("is_correct = 0 AND confidence = 'sure'")
        cursor.execute(f"SELECT COUNT(*) as misconceptions FROM attempts {w}", p)
        misconceptions = cursor.fetchone()["misconceptions"]

        # Confidence Calibration Breakdown
        calibration: dict[str, dict[str, Any]] = {}
        for conf in ["sure", "unsure", "guessed"]:
            w, p = build_where("confidence = ?")
            cursor.execute(
                f"""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct
                FROM attempts {w}
            """,
                base_params + (conf,),
            )
            c_row = cursor.fetchone()
            c_tot = c_row["total"] or 0
            c_cor = c_row["correct"] or 0
            c_acc = round((c_cor / c_tot * 100), 1) if c_tot > 0 else 0.0
            calibration[conf] = {
                "total": c_tot,
                "correct": c_cor,
                "accuracy_pct": c_acc,
            }

        sure_tot = calibration["sure"]["total"]
        misconception_rate_pct = (
            round((misconceptions / sure_tot * 100), 1) if sure_tot > 0 else 0.0
        )

        # Top error tags
        w, p = build_where("error_tag IS NOT NULL AND error_tag != ''")
        cursor.execute(f"""
            SELECT error_tag, COUNT(*) as count
            FROM attempts {w}
            GROUP BY error_tag
            ORDER BY count DESC
            LIMIT 5
        """, p)
        top_errors = [dict(r) for r in cursor.fetchall()]

        # Breakdown by topic
        w, p = build_where()
        cursor.execute(f"""
            SELECT topic,
                   COUNT(*) as total,
                   SUM(CASE WHEN status = 'correct_first_try' AND confidence IN ('sure', 'unsure') THEN 1 ELSE 0 END) as honest_mastery,
                   SUM(CASE WHEN status = 'correct_first_try' THEN 1 ELSE 0 END) as first_try,
                   SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as total_correct
            FROM attempts {w}
            GROUP BY topic
        """, p)
        topic_stats = [dict(r) for r in cursor.fetchall()]

        # Procedural drills statistics
        cursor.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct,
                   AVG(time_spent_sec) as avg_time
            FROM procedural_attempts
        """)
        drill_row = cursor.fetchone()
        total_drills = drill_row["total"] or 0
        correct_drills = drill_row["correct"] or 0
        avg_drill_time = round(drill_row["avg_time"] or 0, 1)
        drill_accuracy_pct = (
            round((correct_drills / total_drills * 100), 1) if total_drills > 0 else 0.0
        )

        cursor.execute("""
            SELECT drill_type,
                   COUNT(*) as total,
                   SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct
            FROM procedural_attempts
            GROUP BY drill_type
        """)
        drills_by_type = [dict(r) for r in cursor.fetchall()]

        # Bookmarks count
        cursor.execute("SELECT COUNT(*) as cnt FROM bookmarks")
        bookmarked_count = cursor.fetchone()["cnt"]

        # Honest Mastery Rate (excludes lucky guesses)
        honest_mastery_rate = (
            round((honest_mastery_count / total_attempts * 100), 1)
            if total_attempts > 0
            else 0.0
        )

        return {
            "total_attempts": total_attempts,
            "first_try_correct": first_try_raw,
            "honest_mastery_count": honest_mastery_count,
            "lucky_guesses": lucky_guesses,
            "assisted_correct": assisted_correct,
            "wrong_count": wrong_count,
            "honest_mastery_rate": honest_mastery_rate,
            "avg_think_time_sec": avg_think,
            "avg_review_time_sec": avg_review,
            "misconception_count": misconceptions,
            "misconception_rate_pct": misconception_rate_pct,
            "confidence_calibration": calibration,
            "top_error_tags": top_errors,
            "topic_breakdown": topic_stats,
            "total_drills": total_drills,
            "correct_drills": correct_drills,
            "drill_accuracy_pct": drill_accuracy_pct,
            "avg_drill_time_sec": avg_drill_time,
            "drills_by_type": drills_by_type,
            "bookmarked_count": bookmarked_count,
        }


def get_interleaved_questions(limit: int = 10, verified_only: bool = False) -> list[Question]:
    """
    Selects questions across distinct topics and subjects in a round-robin interleaved order.
    Interleaving prevents cognitive blocking and trains selective recall under exam conditions.
    Prioritizes questions due in review queue or from high-priority roadmap topics.
    """
    all_questions = content_loader.get_all_questions(verified_only=verified_only)
    if not all_questions:
        return []

    # Get due question IDs
    due_items = get_due_reviews()
    due_ids = {d["question_id"] for d in due_items}

    # Group questions by topic
    topic_map: dict[str, list[Question]] = defaultdict(list)
    for q in all_questions:
        topic_map[q.topic].append(q)

    # Sort questions within each topic: due first, then random shuffle
    for t, q_list in topic_map.items():
        due_subset = [q for q in q_list if q.id in due_ids]
        other_subset = [q for q in q_list if q.id not in due_ids]
        random.shuffle(due_subset)
        random.shuffle(other_subset)
        topic_map[t] = due_subset + other_subset

    # Interleave round-robin across topics
    interleaved: list[Question] = []
    topics = list(topic_map.keys())
    random.shuffle(topics)

    idx = 0
    while len(interleaved) < limit and any(topic_map.values()):
        t = topics[idx % len(topics)]
        if topic_map[t]:
            interleaved.append(topic_map[t].pop(0))
        idx += 1

    return interleaved
