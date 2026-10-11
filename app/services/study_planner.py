from datetime import datetime, timezone
from typing import Any

from app.database import get_db
from app.services.content_loader import content_loader
from app.services.learning_path import analyze_topic_readiness
from app.services.roadmap_service import get_exam_countdown, get_roadmap_topics


def get_daily_study_plan(
    daily_minutes: int = 60,
    target_exam: str = "alevel",
) -> dict[str, Any]:
    """
    Generates a personalized, adaptive daily study schedule based on:
    - User's available daily time budget
    - Spaced repetition queue (prioritizing high-confidence misconceptions and guesses)
    - Prerequisite knowledge readiness
    - Days remaining until exam
    - Roadmap topic priorities
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
                # Focus on the unready prerequisite topic instead
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
        # All goals met, pick priority 1 for maintenance review
        focus_topic = topics[0]

    # 3. Time Allocation Partitioning
    review_min = max(10, int(daily_minutes * 0.25))
    practice_min = max(15, int(daily_minutes * 0.50))
    drill_min = max(5, int(daily_minutes * 0.15))
    quiz_min = max(5, daily_minutes - (review_min + practice_min + drill_min))

    # Assemble structured study blocks
    blocks = []

    # Block 1: Spaced Review
    due_count = len(due_items)
    high_prio_count = sum(1 for it in due_items if it.get("priority") == "high")
    blocks.append(
        {
            "block_id": "spaced_review",
            "title": "ทบทวนข้อผิดพลาดตามรอบ Spaced Repetition",
            "allocated_minutes": review_min,
            "badge": "Smart Review",
            "badge_color": "#818cf8",
            "action_url": "/practice/interleaved?mode=spaced_only",
            "action_label": f"เริ่มทบทวน ({due_count} ข้อ)",
            "details": f"มีข้อครบกำหนดทบทวน {due_count} ข้อ (ข้อที่เป็นจุดอ่อนร้ายแรง {high_prio_count} ข้อ)",
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
                "details": f"ความเชี่ยวชาญปัจจุบัน {focus_topic.get('current_mastery_pct', 0)}% (เป้าหมาย {focus_topic.get('target_score_pct', 80)}%)",
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
            "details": "ฝึกคิดเลขในใจ ตัดช้อยส์ แปลงหน่วย และเลือกสูตร เพื่อไม่ให้เสียเวลากับข้อสอบจริง",
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
            "details": "วัดความเข้าใจทันทีหลังจบรอบอ่าน เพื่อกระตุ้นสมองไม่ให้ลืมเนื้อหาที่เพิ่งฝึกไป",
            "priority": "medium",
        }
    )

    return {
        "daily_minutes": daily_minutes,
        "target_exam": target_exam,
        "days_left": days_left,
        "weeks_left": weeks_left,
        "due_reviews_count": due_count,
        "high_priority_misconceptions": len(misconceptions),
        "focus_topic": focus_topic,
        "prerequisite_alert": prereq_alert,
        "blocks": blocks,
    }
