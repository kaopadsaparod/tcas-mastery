import json
import uuid
from datetime import datetime, timezone
from typing import Any

from app.database import get_db
from app.services.learning_path import analyze_topic_readiness
from app.services.roadmap_service import get_exam_countdown, get_roadmap_topics


def calculate_dynamic_time_allocation(
    total_minutes: int,
    due_count: int = 0,
    misc_count: int = 0,
) -> dict[str, int]:
    """
    Dynamically balances time ratios based on learner's review backlog:
    - High backlog (due >= 6 or misconceptions >= 2): expands review to 35%, reduces practice to 35%
    - Low backlog (due <= 2): shrinks review to 15%, expands practice to 55%
    - Moderate backlog: 25% review, 45% practice
    Drill & Quiz stay at 15% each, with exact minute conservation.
    """
    total_minutes = max(20, min(180, total_minutes))
    if due_count >= 6 or misc_count >= 2:
        rev_ratio = 0.35
        prac_ratio = 0.35
        drill_ratio = 0.15
        quiz_ratio = 0.15
    elif due_count <= 2:
        rev_ratio = 0.15
        prac_ratio = 0.55
        drill_ratio = 0.15
        quiz_ratio = 0.15
    else:
        rev_ratio = 0.25
        prac_ratio = 0.45
        drill_ratio = 0.15
        quiz_ratio = 0.15

    review_min = max(5, int(total_minutes * rev_ratio))
    practice_min = max(10, int(total_minutes * prac_ratio))
    drill_min = max(5, int(total_minutes * drill_ratio))
    quiz_min = max(5, total_minutes - (review_min + practice_min + drill_min))

    diff = total_minutes - (review_min + practice_min + drill_min + quiz_min)
    practice_min += diff

    return {
        "review_minutes": review_min,
        "practice_minutes": practice_min,
        "drill_minutes": drill_min,
        "quiz_minutes": quiz_min,
    }


def get_daily_study_plan(
    daily_minutes: int = 60,
    target_exam: str = "alevel",
) -> dict[str, Any]:
    """
    Generates a personalized, dynamically balanced daily study schedule based on:
    - User's available daily time budget (30, 45, 60, 90, 120 min)
    - Urgent spaced repetition queue items (adjusting review time up or down dynamically)
    - Prerequisite knowledge readiness DAG
    - Days remaining until exam
    - Roadmap topic priorities
    Guarantees sum of block minutes exactly equals daily_minutes.
    """
    countdown = get_exam_countdown()
    days_left = countdown["alevel_days_left"] if target_exam == "alevel" else countdown["tpat_days_left"]
    weeks_left = countdown["alevel_weeks_left"] if target_exam == "alevel" else countdown["tpat_weeks_left"]

    # Clamp daily minutes between 20 and 180
    daily_minutes = max(20, min(180, daily_minutes))

    # 1. Fetch Due Review Queue Items
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT question_id, subject, topic, next_review_at, interval_days,
                   repetition_count, priority, last_error_tag
            FROM review_queue
            WHERE next_review_at <= ? OR next_review_at IS NULL
            ORDER BY
                CASE WHEN priority = 'high' THEN 1
                     WHEN priority = 'normal' THEN 2
                     ELSE 3 END ASC,
                next_review_at ASC
            LIMIT 10
        """,
            (now_iso,),
        )
        due_items = [dict(r) for r in cursor.fetchall()]

        # High priority misconceptions (sure but wrong)
        cursor.execute("""
            SELECT question_id, topic, error_tag
            FROM attempts
            WHERE is_correct = 0 AND confidence = 'sure'
            ORDER BY id DESC
            LIMIT 5
        """)
        misconceptions = [dict(r) for r in cursor.fetchall()]

    due_count = len(due_items)
    misc_count = len(misconceptions)

    # 2. Identify Focus Topic based on Roadmap & Prerequisites
    topics = get_roadmap_topics()
    focus_topic = None
    prereq_alert = None

    for t in topics:
        if not t["is_goal_met"]:
            readiness = analyze_topic_readiness(t["topic_id"])
            if not readiness["is_ready"]:
                # Recommend fixing prerequisite first
                prereq_alert = {
                    "target_topic": t["topic_name"],
                    "unready_prereq": readiness["unready_prerequisites"][0]["topic_name"],
                    "message": readiness["message"],
                }
                focus_topic = {
                    "topic_id": readiness["unready_prerequisites"][0]["topic_id"],
                    "topic_name": readiness["unready_prerequisites"][0]["topic_name"],
                    "is_prerequisite_fix": True,
                    "target_score_pct": 80.0,
                    "current_mastery_pct": readiness["unready_prerequisites"][0]["mastery_pct"],
                }
                break
            else:
                focus_topic = t
                break

    if not focus_topic and topics:
        focus_topic = topics[0]

    # 3. Dynamic Time Balancing using modular calculation
    alloc = calculate_dynamic_time_allocation(daily_minutes, due_count, misc_count)
    review_min = alloc["review_minutes"]
    practice_min = alloc["practice_minutes"]
    drill_min = alloc["drill_minutes"]
    quiz_min = alloc["quiz_minutes"]

    blocks = []

    # Block 1: Spaced Review
    blocks.append(
        {
            "block_id": "spaced_review",
            "title": "ทบทวนข้อผิดพลาดตามรอบ Spaced Repetition",
            "allocated_minutes": review_min,
            "badge": "Smart Review",
            "badge_color": "#818cf8",
            "action_url": "/practice/interleaved?mode=spaced_only",
            "action_label": f"เริ่มทบทวน ({due_count} ข้อ)",
            "details": f"มีข้อครบกำหนดทบทวน {due_count} ข้อ (จุดอ่อนร้ายแรง {misc_count} ข้อ) จัดสรรเวลา {review_min} นาที",
            "priority": "high",
        }
    )

    # Block 2: Concept Practice on Focus Topic
    if focus_topic:
        is_prereq = focus_topic.get("is_prerequisite_fix", False)
        blocks.append(
            {
                "block_id": "concept_practice",
                "title": f"ฝึกทำโจทย์บทเรียนหลัก: {focus_topic.get('topic_name')}",
                "allocated_minutes": practice_min,
                "badge": "เสริมฐานราก" if is_prereq else "ลุยบทเป้าหมาย",
                "badge_color": "#f59e0b" if is_prereq else "#10b981",
                "action_url": f"/practice?topic={focus_topic.get('topic_id')}",
                "action_label": "เข้าสู่ห้องฝึกโจทย์ ➔",
                "details": f"ความเชี่ยวชาญปัจจุบัน {focus_topic.get('current_mastery_pct', 0)}% (เป้าหมาย {focus_topic.get('target_score_pct', 80)}%) จัดสรรเวลา {practice_min} นาที",
                "priority": "high",
            }
        )

    # Block 3: Procedural Speed Drill
    blocks.append(
        {
            "block_id": "speed_drill",
            "title": "ฝึกคิดเลขเร็ว & คัดเลือกสมการ (Procedural Drill)",
            "allocated_minutes": drill_min,
            "badge": "ฝึกความไว",
            "badge_color": "#06b6d4",
            "action_url": "/drills",
            "action_label": "สุ่มแบบฝึกหัดคำนวณ ➔",
            "details": f"ฝึกคิดเลขในใจ ตัดช้อยส์ แปลงหน่วย และเลือกสูตร จัดสรรเวลา {drill_min} นาที",
            "priority": "medium",
        }
    )

    # Block 4: Micro-Quiz
    blocks.append(
        {
            "block_id": "micro_quiz",
            "title": "ทดสอบความคงทนระยะสั้น (5-Minute Retention Quiz)",
            "allocated_minutes": quiz_min,
            "badge": "Active Recall",
            "badge_color": "#ec4899",
            "action_url": "/practice/interleaved?limit=3",
            "action_label": "ทำ Micro-Quiz 3 ข้อ ➔",
            "details": f"วัดความเข้าใจทันทีหลังจบรอบอ่าน จัดสรรเวลา {quiz_min} นาที",
            "priority": "medium",
        }
    )

    return {
        "daily_minutes": daily_minutes,
        "target_exam": target_exam,
        "days_left": days_left,
        "weeks_left": weeks_left,
        "due_reviews_count": due_count,
        "high_priority_misconceptions": misc_count,
        "focus_topic": focus_topic,
        "prerequisite_alert": prereq_alert,
        "blocks": blocks,
    }


def start_study_session(
    target_exam: str = "alevel",
    daily_minutes: int = 60,
    planned_minutes: int | None = None,
    blocks: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Initializes a logged study session for today."""
    minutes = planned_minutes if planned_minutes is not None else daily_minutes
    session_id = f"study-{uuid.uuid4().hex[:10]}"
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO study_sessions (session_id, target_exam, daily_minutes, blocks_completed_json, status)
            VALUES (?, ?, ?, '[]', 'in_progress')
        """,
            (session_id, target_exam, minutes),
        )
    return {
        "session_id": session_id,
        "status": "in_progress",
        "daily_minutes": minutes,
        "planned_minutes": minutes,
    }


def log_study_block(
    session_id: str,
    block_id: str | None = None,
    time_spent_min: float = 0.0,
    status: str = "completed",
    notes: str = "",
    block_index: int | None = None,
    action: str | None = None,
) -> dict[str, Any]:
    """Logs completion or skipping of an individual block within a study session."""
    effective_status = action if action is not None else status
    effective_block_id = block_id if block_id is not None else f"block_{block_index if block_index is not None else 0}"

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT blocks_completed_json, total_time_spent_min FROM study_sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Study session not found: {session_id}")

        blocks = json.loads(row["blocks_completed_json"] or "[]")
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        block_entry = {
            "block_id": effective_block_id,
            "block_index": block_index,
            "time_spent_min": round(time_spent_min, 1),
            "status": effective_status,
            "notes": notes,
            "timestamp": now_iso,
        }
        blocks.append(block_entry)

        new_total_time = round((row["total_time_spent_min"] or 0.0) + time_spent_min, 1)

        cursor.execute(
            """
            UPDATE study_sessions
            SET blocks_completed_json = ?, total_time_spent_min = ?
            WHERE session_id = ?
        """,
            (json.dumps(blocks, ensure_ascii=False), new_total_time, session_id),
        )

    return {
        "session_id": session_id,
        "blocks_count": len(blocks),
        "total_time_spent_min": new_total_time,
        "completed_blocks": blocks,
    }


def finish_study_session(
    session_id: str,
    notes: str = "",
    actual_minutes: float | None = None,
    summary_notes: str = "",
) -> dict[str, Any]:
    """Finalizes a study session as completed."""
    final_notes = summary_notes if summary_notes else notes
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    with get_db() as conn:
        cursor = conn.cursor()
        if actual_minutes is not None:
            cursor.execute(
                """
                UPDATE study_sessions
                SET status = 'completed', completed_at = ?, notes = ?, total_time_spent_min = ?
                WHERE session_id = ?
            """,
                (now_iso, final_notes, float(actual_minutes), session_id),
            )
        else:
            cursor.execute(
                """
                UPDATE study_sessions
                SET status = 'completed', completed_at = ?, notes = ?
                WHERE session_id = ?
            """,
                (now_iso, final_notes, session_id),
            )
    return {
        "session_id": session_id,
        "status": "completed",
        "completed_at": now_iso,
        "actual_minutes": actual_minutes,
    }


def get_study_session_history(limit: int = 10) -> list[dict[str, Any]]:
    """Retrieves recent completed study sessions."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT session_id, target_exam, daily_minutes, blocks_completed_json,
                   total_time_spent_min, status, notes, created_at, completed_at
            FROM study_sessions
            ORDER BY id DESC
            LIMIT ?
        """,
            (limit,),
        )
        res = []
        for r in cursor.fetchall():
            d = dict(r)
            completed_blocks = json.loads(d.get("blocks_completed_json") or "[]")
            d["blocks_completed"] = completed_blocks
            d["completed_blocks"] = completed_blocks
            d["planned_minutes"] = d.get("daily_minutes")
            d["actual_minutes"] = d.get("total_time_spent_min")
            res.append(d)
        return res
