from datetime import datetime, timedelta, timezone
from typing import Any

from app.database import get_db
from app.services.mock_exam import get_mock_exam_history
from app.services.roadmap_service import get_roadmap_topics
from app.services.tutor_engine import classify_error_cause


def get_progress_report() -> dict[str, Any]:
    """
    Assembles a comprehensive Exam Readiness & Progress Report
    answering the 4 vital pedagogical questions:
    1. รู้เรื่องอะไรแล้ว (First-attempt accuracy & sample size evidence)
    2. ยังอ่อนตรงไหน (Weak topics, skills, and error tag breakdown)
    3. กำลังดีขึ้นหรือไม่ (7-day historical progress comparison)
    4. พร้อมสอบแค่ไหน (Blueprint mock exam projection with uncertainty margin)
    """
    now = datetime.now(timezone.utc)
    seven_days_ago = (now - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    fourteen_days_ago = (now - timedelta(days=14)).strftime("%Y-%m-%d %H:%M:%S")

    # 1. Competency Evidence from Attempts
    with get_db() as conn:
        cursor = conn.cursor()

        # Unique questions count and first-attempt accuracy
        cursor.execute("""
            WITH RankedAttempts AS (
                SELECT question_id, is_correct, created_at,
                       ROW_NUMBER() OVER (PARTITION BY question_id ORDER BY created_at ASC) as first_rn,
                       ROW_NUMBER() OVER (PARTITION BY question_id ORDER BY created_at DESC) as recent_rn
                FROM attempts
            )
            SELECT
                COUNT(DISTINCT question_id) as total_unique_q,
                SUM(CASE WHEN first_rn = 1 AND is_correct = 1 THEN 1 ELSE 0 END) as first_correct,
                SUM(CASE WHEN recent_rn = 1 AND is_correct = 1 THEN 1 ELSE 0 END) as recent_correct
            FROM RankedAttempts;
        """)
        row = cursor.fetchone()
        unique_q_count = row["total_unique_q"] or 0
        first_correct = row["first_correct"] or 0
        recent_correct = row["recent_correct"] or 0

        first_attempt_acc = round((first_correct / unique_q_count * 100), 1) if unique_q_count > 0 else 0.0
        recent_acc = round((recent_correct / unique_q_count * 100), 1) if unique_q_count > 0 else 0.0

        # Recent 7 days vs previous 7 days comparison
        cursor.execute(
            """
            SELECT COUNT(*) as cnt,
                   SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct_cnt
            FROM attempts
            WHERE created_at >= ?
        """,
            (seven_days_ago,),
        )
        r_this_week = cursor.fetchone()
        this_week_total = r_this_week["cnt"] or 0
        this_week_correct = r_this_week["correct_cnt"] or 0
        this_week_acc = round((this_week_correct / this_week_total * 100), 1) if this_week_total > 0 else 0.0

        cursor.execute(
            """
            SELECT COUNT(*) as cnt,
                   SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct_cnt
            FROM attempts
            WHERE created_at >= ? AND created_at < ?
        """,
            (fourteen_days_ago, seven_days_ago),
        )
        r_prev_week = cursor.fetchone()
        prev_week_total = r_prev_week["cnt"] or 0
        prev_week_correct = r_prev_week["correct_cnt"] or 0
        prev_week_acc = round((prev_week_correct / prev_week_total * 100), 1) if prev_week_total > 0 else 0.0

        # Error tag distribution breakdown
        cursor.execute("""
            SELECT error_tag, COUNT(*) as cnt
            FROM attempts
            WHERE is_correct = 0 AND error_tag IS NOT NULL AND error_tag != ''
            GROUP BY error_tag
            ORDER BY cnt DESC
            LIMIT 10
        """)
        error_rows = cursor.fetchall()

    # Process Error Categories
    error_cat_counts: dict[str, int] = {"concept": 0, "formula": 0, "unit": 0, "calculation": 0, "reading": 0}
    total_tagged_errors = 0
    top_error_tags = []

    for r in error_rows:
        etag = r["error_tag"]
        cnt = r["cnt"]
        total_tagged_errors += cnt
        cat_info = classify_error_cause(etag)
        cat_key = cat_info.get("category", "reading")
        error_cat_counts[cat_key] = error_cat_counts.get(cat_key, 0) + cnt
        top_error_tags.append({
            "tag": etag,
            "category": cat_key,
            "category_title": cat_info.get("title", ""),
            "count": cnt,
        })

    error_breakdown = []
    for cat_k, cnt in error_cat_counts.items():
        pct = round((cnt / total_tagged_errors * 100), 1) if total_tagged_errors > 0 else 0.0
        error_breakdown.append({
            "category": cat_k,
            "title": classify_error_cause(cat_k)["title"],
            "count": cnt,
            "percent": pct,
        })
    error_breakdown.sort(key=lambda x: x["count"], reverse=True)

    # 2. Topic Readiness & Mastery Evidence from Roadmap
    topics = get_roadmap_topics()
    mastered_topics = [t for t in topics if t.get("is_goal_met") and t.get("mastery_confidence") in {"high", "moderate"}]
    weak_topics = [t for t in topics if not t.get("is_goal_met") and t.get("total_attempts", 0) >= 2]
    untested_topics = [t for t in topics if t.get("total_attempts", 0) == 0]

    # 3. Trajectory analysis
    if this_week_total == 0:
        trajectory_status = "inactive"
        trajectory_message = "สัปดาห์นี้ยังไม่มีการบันทึกการฝึกทำโจทย์ เริ่มต้นฝึกวันนี้เพื่อสร้างแนวโน้มพัฒนาการ"
    elif prev_week_total == 0:
        trajectory_status = "new_start"
        trajectory_message = f"สัปดาห์แรกของการฝึกทำโจทย์ ({this_week_total} ข้อ, ความแม่นยำ {this_week_acc}%) ฝึกต่อเนื่องเพื่อเปรียบเทียบแนวโน้ม"
    elif this_week_acc > prev_week_acc + 5:
        trajectory_status = "improving"
        trajectory_message = f"ความแม่นยำเพิ่มขึ้นจากสัปดาห์ก่อน (+{round(this_week_acc - prev_week_acc, 1)}%) สะท้อนว่าเริ่มจำหลักการได้แม่นขึ้น"
    elif this_week_acc < prev_week_acc - 5:
        trajectory_status = "needs_focus"
        trajectory_message = f"ความแม่นยำลดลงจากสัปดาห์ก่อน ({this_week_acc}% เทียบกับ {prev_week_acc}%) อาจเป็นเพราะเริ่มทำโจทย์บทที่ยากขึ้น แนะนำเสริมพื้นฐาน"
    else:
        trajectory_status = "steady"
        trajectory_message = f"ความแม่นยำทรงตัวสม่ำเสมอ ({this_week_acc}%) มุ่งเน้นเพิ่มจำนวนโจทย์ที่ไม่เคยเห็นเพื่อเตรียมสอบ"

    # 4. Exam Readiness Index
    mock_history = get_mock_exam_history()
    mock_count = len(mock_history)
    avg_mock_pct = round(sum(m["score_percent"] for m in mock_history) / mock_count, 1) if mock_count > 0 else 0.0

    # Uncertainty calculation
    if mock_count == 0 or unique_q_count < 15:
        confidence_level = "low"
        uncertainty_margin = 15.0
        readiness_label = "ข้อมูลยังไม่เพียงพอสำหรับการประเมินขั้นสูง"
        readiness_badge = "Needs More Data"
        readiness_score = round(max(first_attempt_acc, avg_mock_pct), 1)
    elif mock_count < 3 or unique_q_count < 40:
        confidence_level = "moderate"
        uncertainty_margin = 8.0
        readiness_label = "ประเมินความพร้อมเบื้องต้น (ความเชื่อมั่นระดับปานกลาง)"
        readiness_badge = "Moderate Confidence"
        readiness_score = round((avg_mock_pct * 0.6) + (first_attempt_acc * 0.4), 1)
    else:
        confidence_level = "high"
        uncertainty_margin = 4.0
        readiness_label = "ประเมินความพร้อมระดับสูงจากหลักฐานการสอบจริง"
        readiness_badge = "High Confidence"
        readiness_score = round((avg_mock_pct * 0.7) + (recent_acc * 0.3), 1)

    # Actionable Next Steps
    next_steps = []
    if weak_topics:
        next_steps.append(f"โฟกัสบทที่เป็นจุดอ่อนอันดับ 1: {weak_topics[0]['topic_name']} (แม่นยำเพียง {weak_topics[0]['recent_accuracy']}%)")
    if error_breakdown and error_breakdown[0]["percent"] > 25:
        next_steps.append(f"ลดสาเหตุผิดพลาดหลัก: {error_breakdown[0]['title']} (คิดเป็น {error_breakdown[0]['percent']}% ของข้อที่ผิด)")
    if mock_count < 2:
        next_steps.append("ทำ Full Mock Exam อย่างน้อย 1 ชุดตามเวลาจริง (90 นาที) เพื่อวัดความเร็ว Pace และสร้างสถิติอ้างอิง")
    if untested_topics:
        next_steps.append(f"ยังมีบทที่ยังไม่เคยแตะ {len(untested_topics)} บท (เช่น {untested_topics[0]['topic_name']}) ให้เพิ่มใน Planner สัปดาห์นี้")

    return {
        "competency": {
            "unique_questions_tested": unique_q_count,
            "total_attempts": unique_q_count,
            "first_attempt_accuracy": first_attempt_acc,
            "recent_accuracy": recent_acc,
            "overall_accuracy": recent_acc,
            "honest_mastery_pct": first_attempt_acc,
            "mastered_topics_count": len(mastered_topics),
            "mastered_topics": mastered_topics,
        },
        "weaknesses": {
            "weak_topics_count": len(weak_topics),
            "weak_topics": weak_topics,
            "top_error_tags": top_error_tags[:5],
            "top_misconceptions": top_error_tags[:5],
            "error_distribution": error_breakdown,
        },
        "trajectory": {
            "status": trajectory_status,
            "message": trajectory_message,
            "this_week_total": this_week_total,
            "this_week_accuracy": this_week_acc,
            "prev_week_total": prev_week_total,
            "prev_week_accuracy": prev_week_acc,
            "predicted_score_range": f"{max(0.0, readiness_score - uncertainty_margin):.1f}% - {min(100.0, readiness_score + uncertainty_margin):.1f}%",
            "uncertainty_margin": uncertainty_margin,
            "evidence_level": confidence_level,
        },
        "readiness": {
            "score": readiness_score,
            "confidence_level": confidence_level,
            "uncertainty_margin": uncertainty_margin,
            "label": readiness_label,
            "badge": readiness_badge,
            "mock_exams_taken": mock_count,
            "average_mock_score_pct": avg_mock_pct,
        },
        "next_steps": next_steps,
        "recommendations": next_steps,
    }
