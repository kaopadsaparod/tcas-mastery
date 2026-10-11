import json
import uuid
from datetime import datetime, timezone
from typing import Any

from app.database import get_db
from app.services.content_loader import content_loader
from app.services.grader import grade_numeric

EXAM_BLUEPRINTS: dict[str, dict[str, Any]] = {
    "alevel_physics": {
        "id": "alevel_physics",
        "title": "A-Level ฟิสิกส์ (ชุดจำลองมาตรฐาน TCAS)",
        "subject": "physics",
        "time_limit_min": 90,
        "max_score": 100.0,
        "pace_target_min": 3.0,
        "description": "จำลองสภาพแวดล้อมสอบ A-Level ฟิสิกส์ 90 นาที ไม่แสดงเฉลยระหว่างทำ จับเวลาถอยหลัง และสรุปผลวิเคราะห์จุดอ่อนอย่างละเอียด",
    },
    "tpat3": {
        "id": "tpat3",
        "title": "TPAT3 ความถนัดด้านวิทยาศาสตร์ เทคโนโลยี และวิศวกรรมศาสตร์",
        "subject": "tpat3",
        "time_limit_min": 180,
        "max_score": 100.0,
        "pace_target_min": 2.5,
        "description": "จำลองสอบ TPAT3 เต็มรูปแบบ 180 นาที เน้นทดสอบการคิดเชิงตัวเลข มิติสัมพันธ์ และตรรกะเชิงวิทยาศาสตร์",
    },
}


def start_mock_exam(exam_type: str = "alevel_physics") -> dict[str, Any]:
    """
    Initializes a new full mock exam session with official blueprints.
    Prepares questions in exam order, stripping all answers and hints.
    """
    blueprint = EXAM_BLUEPRINTS.get(exam_type, EXAM_BLUEPRINTS["alevel_physics"])
    session_id = uuid.uuid4().hex[:12]

    # Gather questions for this exam
    # First priority: check if past paper exists for this subject
    past_papers = content_loader.get_past_papers_by_subject(blueprint["subject"])
    exam_questions = []

    if past_papers:
        paper = past_papers[0]
        for q in paper.questions:
            # Look up corresponding question details in content bank if possible, or build basic item
            full_q = content_loader.get_question_by_id(f"phy-kin-000{q.number}")
            if full_q:
                options_data = []
                if full_q.answer.options:
                    for opt in full_q.answer.options:
                        options_data.append({"id": opt.id, "text": opt.text})

                exam_questions.append(
                    {
                        "number": q.number,
                        "question_id": full_q.id,
                        "stem": full_q.stem,
                        "topic": full_q.topic,
                        "skill": full_q.skills.primary,
                        "answer_type": full_q.answer.type,
                        "options": options_data,
                        "unit": full_q.answer.unit,
                        "score": q.score,
                    }
                )
            else:
                exam_questions.append(
                    {
                        "number": q.number,
                        "question_id": f"mock-q-{q.number}",
                        "stem": f"ข้อสอบข้อที่ {q.number} ({q.topic})",
                        "topic": q.topic,
                        "skill": q.skill,
                        "answer_type": q.answer_type or "single_choice",
                        "options": [
                            {"id": "1", "text": "ตัวเลือก 1"},
                            {"id": "2", "text": "ตัวเลือก 2"},
                            {"id": "3", "text": "ตัวเลือก 3"},
                            {"id": "4", "text": "ตัวเลือก 4"},
                            {"id": "5", "text": "ตัวเลือก 5"},
                        ] if (q.answer_type or "single_choice") == "single_choice" else None,
                        "unit": q.unit,
                        "score": q.score,
                    }
                )
    else:
        # Fallback to questions from content loader matching subject
        qs = [q for q in content_loader.get_all_questions() if q.subject == blueprint["subject"]]
        for i, q in enumerate(qs, 1):
            options_data = []
            if q.answer.options:
                for opt in q.answer.options:
                    options_data.append({"id": opt.id, "text": opt.text})

            exam_questions.append(
                {
                    "number": i,
                    "question_id": q.id,
                    "stem": q.stem,
                    "topic": q.topic,
                    "skill": q.skills.primary,
                    "answer_type": q.answer.type,
                    "options": options_data,
                    "unit": q.answer.unit,
                    "score": 3.0 if q.answer.type == "single_choice" else 5.0,
                }
            )

    total_q = len(exam_questions)
    max_score = sum(q["score"] for q in exam_questions) or 100.0

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO mock_exam_sessions (
                session_id, exam_type, title, time_limit_min,
                status, total_questions, max_score, answers_json, flagged_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                session_id,
                blueprint["id"],
                blueprint["title"],
                blueprint["time_limit_min"],
                "in_progress",
                total_q,
                max_score,
                json.dumps({}),
                json.dumps([]),
            ),
        )

    return {
        "session_id": session_id,
        "exam_type": blueprint["id"],
        "title": blueprint["title"],
        "time_limit_min": blueprint["time_limit_min"],
        "time_limit_sec": blueprint["time_limit_min"] * 60,
        "total_questions": total_q,
        "max_score": max_score,
        "pace_target_min": blueprint["pace_target_min"],
        "questions": exam_questions,
    }


def get_mock_exam_session(session_id: str) -> dict[str, Any] | None:
    """Retrieves session record from database."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM mock_exam_sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        if not row:
            return None
        res = dict(row)
        res["answers"] = json.loads(res.get("answers_json") or "{}")
        res["flagged"] = json.loads(res.get("flagged_json") or "[]")
        res["report"] = json.loads(res.get("report_json") or "{}")
        return res


def save_mock_exam_progress(
    session_id: str,
    answers: dict[str, str],
    flagged: list[Any],
    time_spent_min: float,
) -> bool:
    """Persists intermediate answers and flagged states during active exam."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE mock_exam_sessions
            SET answers_json = ?, flagged_json = ?, time_spent_min = ?
            WHERE session_id = ? AND status = 'in_progress'
        """,
            (json.dumps(answers), json.dumps(flagged), time_spent_min, session_id),
        )
        return cursor.rowcount > 0


def submit_mock_exam(
    session_id: str,
    answers: dict[str, str],
    time_spent_min: float = 0.0,
) -> dict[str, Any]:
    """
    Submits a mock exam session, grades all questions strictly,
    and produces a comprehensive diagnostic performance report.
    """
    sess = get_mock_exam_session(session_id)
    if not sess:
        raise ValueError(f"Session not found: {session_id}")

    exam_type = sess["exam_type"]
    blueprint = EXAM_BLUEPRINTS.get(exam_type, EXAM_BLUEPRINTS["alevel_physics"])

    # Load past paper reference questions
    past_papers = content_loader.get_past_papers_by_subject(blueprint["subject"])
    paper_questions = past_papers[0].questions if past_papers else []
    paper_map = {str(q.number): q for q in paper_questions}

    total_score = 0.0
    correct_count = 0
    max_score = sess["max_score"]
    total_q = sess["total_questions"]

    detailed_results = []
    topic_breakdown: dict[str, dict[str, Any]] = {}

    for i in range(1, total_q + 1):
        num_str = str(i)
        user_ans = answers.get(num_str, "").strip()
        q_ref = paper_map.get(num_str)

        # Lookup expected answer
        if q_ref:
            expected_ans = str(q_ref.correct_answer).strip()
            score_weight = q_ref.score
            topic = q_ref.topic
            skill = q_ref.skill
            ans_type = q_ref.answer_type or ("single_choice" if expected_ans in {"1", "2", "3", "4", "5"} else "numeric")
            tol = q_ref.tolerance or 0.001
            unit = q_ref.unit
        else:
            # Fallback
            full_q = content_loader.get_question_by_id(f"phy-kin-000{i}")
            if full_q:
                score_weight = 3.0 if full_q.answer.type == "single_choice" else 5.0
                topic = full_q.topic
                skill = full_q.skills.primary
                ans_type = full_q.answer.type
                tol = full_q.answer.tolerance or 0.001
                unit = full_q.answer.unit
                if full_q.answer.type == "single_choice":
                    correct_opt = next((o.id for o in (full_q.answer.options or []) if o.correct), "1")
                    expected_ans = correct_opt
                else:
                    expected_ans = str(full_q.answer.correct_value)
            else:
                expected_ans = "1"
                score_weight = 3.0
                topic = "general"
                skill = "problem_solving"
                ans_type = "single_choice"
                tol = 0.001
                unit = None

        # Grade answer strictly based on type
        is_correct = False
        if user_ans:
            if ans_type == "single_choice":
                # Strict exact match only! E.g. choice 3 cannot match 3.05!
                is_correct = (user_ans.lower() == expected_ans.lower())
            else:
                is_correct = grade_numeric(user_ans, expected_ans, tolerance=tol, expected_unit=unit)

        earned = score_weight if is_correct else 0.0
        if is_correct:
            correct_count += 1
            total_score += earned

        # Topic summary
        if topic not in topic_breakdown:
            topic_breakdown[topic] = {
                "topic": topic,
                "total_items": 0,
                "correct_items": 0,
                "score_earned": 0.0,
                "max_score": 0.0,
            }
        topic_breakdown[topic]["total_items"] += 1
        topic_breakdown[topic]["max_score"] += score_weight
        if is_correct:
            topic_breakdown[topic]["correct_items"] += 1
            topic_breakdown[topic]["score_earned"] += earned

        detailed_results.append(
            {
                "number": i,
                "user_answer": user_ans,
                "correct_answer": expected_ans,
                "is_correct": is_correct,
                "score_earned": earned,
                "max_score": score_weight,
                "topic": topic,
                "skill": skill,
            }
        )

    score_pct = round((total_score / max_score * 100), 1) if max_score > 0 else 0.0
    avg_pace_min = round(time_spent_min / total_q, 2) if total_q > 0 else 0.0
    pace_status = "optimal" if avg_pace_min <= blueprint["pace_target_min"] else "slow"

    # Assemble comprehensive report
    report = {
        "session_id": session_id,
        "title": sess["title"],
        "time_spent_min": round(time_spent_min, 1),
        "total_questions": total_q,
        "correct_count": correct_count,
        "total_score": round(total_score, 1),
        "max_score": round(max_score, 1),
        "score_percent": score_pct,
        "avg_pace_min": avg_pace_min,
        "target_pace_min": blueprint["pace_target_min"],
        "pace_status": pace_status,
        "topic_breakdown": topic_breakdown,
        "detailed_results": detailed_results,
    }

    # Save to SQLite
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE mock_exam_sessions
            SET status = 'completed',
                correct_count = ?,
                total_score = ?,
                score_percent = ?,
                time_spent_min = ?,
                answers_json = ?,
                report_json = ?,
                completed_at = ?
            WHERE session_id = ?
        """,
            (
                correct_count,
                round(total_score, 1),
                score_pct,
                round(time_spent_min, 1),
                json.dumps(answers),
                json.dumps(report),
                now_iso,
                session_id,
            ),
        )

    return report


def get_mock_exam_history() -> list[dict[str, Any]]:
    """Returns past completed mock exam sessions for progress tracking."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT session_id, exam_type, title, total_questions, correct_count,
                   total_score, max_score, score_percent, time_spent_min, completed_at
            FROM mock_exam_sessions
            WHERE status = 'completed'
            ORDER BY id DESC
            LIMIT 20
        """)
        return [dict(r) for r in cursor.fetchall()]
