import json
import uuid
from datetime import datetime, timezone
from typing import Any

from app.database import get_db
from app.services.content_loader import content_loader
from app.services.grader import grade_numeric_detailed

EXAM_BLUEPRINTS: dict[str, dict[str, Any]] = {
    "alevel_physics_practice_20": {
        "id": "alevel_physics_practice_20",
        "title": "A-Level ฟิสิกส์ (Practice Set 20 ข้อ)",
        "subject": "physics",
        "paper_id": "alevel-phy-2566-mock",
        "time_limit_min": 60,
        "max_score": 64.0,
        "pace_target_min": 3.0,
        "total_questions": 20,
        "is_official_blueprint": False,
        "description": "ชุดฝึกซ้อมจับเวลา 20 ข้อ (ปรนัย 18 ข้อ + เติมตัวเลข 2 ข้อ) สำหรับฝึกทำตามเวลาจริงและจับจุดอ่อนเบื้องต้น",
    },
    "alevel_physics_mock_30": {
        "id": "alevel_physics_mock_30",
        "title": "A-Level ฟิสิกส์ (ข้อสอบจำลองตามโครงสร้าง MyTCAS 30 ข้อ)",
        "subject": "physics",
        "paper_id": "alevel-phy-blueprint-30",
        "time_limit_min": 90,
        "max_score": 100.0,
        "pace_target_min": 3.0,
        "total_questions": 30,
        "is_official_blueprint": True,
        "description": "จำลองสอบ A-Level ฟิสิกส์ตามโครงสร้างพิมพ์เขียว MyTCAS (ปรนัย 25 ข้อ ข้อละ 3.0 คะแนน = 75 คะแนน + อัตนัยระบายตัวเลข 5 ข้อ ข้อละ 5.0 คะแนน = 25 คะแนน รวม 100 คะแนนเต็ม 90 นาที)",
    },
    "tpat3_practice_25": {
        "id": "tpat3_practice_25",
        "title": "TPAT3 (ข้อสอบจำลองชุดฝึกซ้อม 25 ข้อ)",
        "subject": "tpat3",
        "paper_id": "tpat3-practice-25",
        "time_limit_min": 60,
        "max_score": 100.0,
        "pace_target_min": 2.4,
        "total_questions": 25,
        "is_official_blueprint": False,
        "description": "ชุดฝึกซ้อมมิติสัมพันธ์ การคิดเชิงตัวเลข และกลศาสตร์เบื้องต้น 25 ข้อ (คะแนนเต็ม 100)",
    },
    "tpat3_mock_70": {
        "id": "tpat3_mock_70",
        "title": "TPAT3 (ข้อสอบจำลองตามโครงสร้าง MyTCAS 70 ข้อ)",
        "subject": "tpat3",
        "paper_id": "tpat3-blueprint-70",
        "time_limit_min": 180,
        "max_score": 100.0,
        "pace_target_min": 2.5,
        "total_questions": 70,
        "is_official_blueprint": True,
        "description": "จำลองสอบ TPAT3 เต็มรูปแบบ 70 ข้อ 180 นาที ครบ 5 ส่วนตามพิมพ์เขียว MyTCAS (ส่วนที่ 1 ความถนัด 45 ข้อ 60 คะแนน + ส่วนที่ 2 ความคิดและความสนใจ 25 ข้อ 40 คะแนน = 100 คะแนนเต็ม)",
    },
    "tgat1_mock_60": {
        "id": "tgat1_mock_60",
        "title": "TGAT1 (การสื่อสารภาษาอังกฤษ ตามโครงสร้าง MyTCAS 60 ข้อ)",
        "subject": "tgat1",
        "paper_id": "tgat1-blueprint-60",
        "time_limit_min": 60,
        "max_score": 100.0,
        "pace_target_min": 1.0,
        "total_questions": 60,
        "is_official_blueprint": True,
        "description": "จำลองสอบ TGAT1 การสื่อสารภาษาอังกฤษ 60 ข้อ 60 นาที (ทักษะการพูด 30 ข้อ 50 คะแนน + ทักษะการอ่าน 30 ข้อ 50 คะแนน รวม 100 คะแนนเต็ม)",
    },
    "tgat3_mock_60": {
        "id": "tgat3_mock_60",
        "title": "TGAT3 (สมรรถนะการทำงานในอนาคต ตามโครงสร้าง MyTCAS 60 ข้อ)",
        "subject": "tgat3",
        "paper_id": "tgat3-blueprint-60",
        "time_limit_min": 60,
        "max_score": 100.0,
        "pace_target_min": 1.0,
        "total_questions": 60,
        "is_official_blueprint": True,
        "description": "จำลองสอบ TGAT3 สมรรถนะการทำงานในอนาคต 60 ข้อ 60 นาที ครบ 4 ส่วน (การสร้างคุณค่าและนวัตกรรม, การแก้ไขปัญหาที่ซับซ้อน, การบริหารจัดการอารมณ์, การเป็นพลเมืองที่มีส่วนร่วมของสังคม รวม 100 คะแนนเต็ม)",
    },
}

# Backward compatibility aliases
EXAM_BLUEPRINTS["alevel_physics"] = EXAM_BLUEPRINTS["alevel_physics_mock_30"]
EXAM_BLUEPRINTS["tpat3"] = EXAM_BLUEPRINTS["tpat3_practice_25"]
EXAM_BLUEPRINTS["tgat1"] = EXAM_BLUEPRINTS["tgat1_mock_60"]
EXAM_BLUEPRINTS["tgat3"] = EXAM_BLUEPRINTS["tgat3_mock_60"]


def _sanitize_question_for_client(q: dict[str, Any]) -> dict[str, Any]:
    """Returns a client-safe dictionary of the question, stripping answers and solutions."""
    return {
        "number": q["number"],
        "question_id": q["question_id"],
        "stem": q["stem"],
        "topic": q["topic"],
        "skill": q["skill"],
        "answer_type": q["answer_type"],
        "options": q.get("options"),
        "unit": q.get("unit"),
        "score": q["score"],
    }


def start_mock_exam(exam_type: str = "alevel_physics_practice_20") -> dict[str, Any]:
    """
    Initializes a new full mock exam session with official blueprints.
    Freezes a complete question snapshot into questions_json in SQLite,
    ensuring that what is displayed, saved, graded, and reported are identical.
    """
    blueprint = EXAM_BLUEPRINTS.get(exam_type, EXAM_BLUEPRINTS["alevel_physics_practice_20"])
    session_id = uuid.uuid4().hex[:12]

    paper_id = blueprint.get("paper_id")
    paper = content_loader.get_past_paper_by_id(paper_id) if paper_id else None

    # Fallback to subject past paper if specific paper_id is not yet defined
    if not paper:
        subject_papers = content_loader.get_past_papers_by_subject(blueprint["subject"])
        if subject_papers:
            paper = subject_papers[0]

    exam_questions: list[dict[str, Any]] = []

    if paper and paper.questions:
        for q in paper.questions:
            # Check if linked to a full question in content library
            full_q = None
            if q.question_id:
                full_q = content_loader.get_question_by_id(q.question_id)

            stem = q.stem
            options = None
            if q.options:
                options = [{"id": opt.id, "text": opt.text} for opt in q.options]

            if full_q:
                if not stem:
                    stem = full_q.stem
                if not options and full_q.answer.options:
                    options = [{"id": opt.id, "text": opt.text} for opt in full_q.answer.options]

            if not stem:
                stem = f"ข้อสอบข้อที่ {q.number} ({q.topic})"

            # Answer type detection
            ans_type = q.answer_type
            if not ans_type:
                if str(q.correct_answer).strip() in {"1", "2", "3", "4", "5", "a", "b", "c", "d", "e"}:
                    ans_type = "single_choice"
                else:
                    ans_type = "numeric"

            if ans_type == "single_choice" and not options:
                options = [{"id": str(i), "text": f"ตัวเลือก {i}"} for i in range(1, 6)]

            exam_questions.append(
                {
                    "number": q.number,
                    "question_id": q.question_id or f"{paper.id}-q{q.number}",
                    "stem": stem,
                    "topic": q.topic,
                    "skill": q.skill,
                    "answer_type": ans_type,
                    "options": options,
                    "correct_answer": str(q.correct_answer).strip(),
                    "tolerance": q.tolerance or 0.001,
                    "unit": q.unit,
                    "require_unit": q.require_unit,
                    "score": q.score,
                    "solution": q.solution,
                }
            )
    else:
        # Fallback from question bank by subject
        qs = [q for q in content_loader.get_all_questions() if q.subject == blueprint["subject"]]
        for i, q in enumerate(qs, 1):
            opts = None
            if q.answer.options:
                opts = [{"id": opt.id, "text": opt.text} for opt in q.answer.options]

            correct_ans = ""
            if q.answer.type == "single_choice":
                correct_opt = next((o.id for o in (q.answer.options or []) if o.correct), "1")
                correct_ans = correct_opt
            else:
                correct_ans = str(q.answer.correct_value or 0)

            exam_questions.append(
                {
                    "number": i,
                    "question_id": q.id,
                    "stem": q.stem,
                    "topic": q.topic,
                    "skill": q.skills.primary,
                    "answer_type": q.answer.type,
                    "options": opts,
                    "correct_answer": correct_ans,
                    "tolerance": q.answer.tolerance or 0.001,
                    "unit": q.answer.unit,
                    "require_unit": q.answer.require_unit,
                    "score": 3.2 if q.answer.type == "single_choice" else 4.0,
                    "solution": q.solution.summary if q.solution else None,
                }
            )

    total_q = len(exam_questions)
    max_score = sum(q["score"] for q in exam_questions) or blueprint["max_score"]

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO mock_exam_sessions (
                session_id, exam_type, title, time_limit_min,
                status, total_questions, max_score, questions_json,
                answers_json, flagged_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                session_id,
                blueprint["id"],
                blueprint["title"],
                blueprint["time_limit_min"],
                "in_progress",
                total_q,
                round(max_score, 1),
                json.dumps(exam_questions, ensure_ascii=False),
                json.dumps({}),
                json.dumps([]),
            ),
        )

    # Return sanitized questions for client
    client_questions = [_sanitize_question_for_client(q) for q in exam_questions]

    return {
        "session_id": session_id,
        "exam_type": blueprint["id"],
        "title": blueprint["title"],
        "time_limit_min": blueprint["time_limit_min"],
        "time_limit_sec": blueprint["time_limit_min"] * 60,
        "total_questions": total_q,
        "max_score": round(max_score, 1),
        "pace_target_min": blueprint["pace_target_min"],
        "questions": client_questions,
    }


def get_mock_exam_session(session_id: str) -> dict[str, Any] | None:
    """Retrieves session record from database, unpacking JSON fields."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM mock_exam_sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        if not row:
            return None
        res = dict(row)
        res["questions"] = json.loads(res.get("questions_json") or "[]")
        res["answers"] = json.loads(res.get("answers_json") or "{}")
        res["flagged"] = json.loads(res.get("flagged_json") or "[]")
        res["report"] = json.loads(res.get("report_json") or "{}")
        return res


def get_mock_exam_sanitized_questions(session_id: str) -> list[dict[str, Any]]:
    """Retrieves client-safe questions from session snapshot."""
    sess = get_mock_exam_session(session_id)
    if not sess:
        return []
    questions = sess.get("questions", [])
    return [_sanitize_question_for_client(q) for q in questions]


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
            (json.dumps(answers, ensure_ascii=False), json.dumps(flagged), time_spent_min, session_id),
        )
        return cursor.rowcount > 0


def submit_mock_exam(
    session_id: str,
    answers: dict[str, str],
    time_spent_min: float = 0.0,
) -> dict[str, Any]:
    """
    Submits a mock exam session, grades strictly using the session's question snapshot,
    and produces an audited diagnostic report. Idempotent if already submitted.
    """
    sess = get_mock_exam_session(session_id)
    if not sess:
        raise ValueError(f"Session not found: {session_id}")

    # Idempotent guard: if already completed, return existing report
    if sess["status"] == "completed" and sess.get("report"):
        return sess["report"]

    exam_type = sess["exam_type"]
    blueprint = EXAM_BLUEPRINTS.get(exam_type, EXAM_BLUEPRINTS["alevel_physics_practice_20"])

    # Merge newly submitted answers with previously autosaved answers
    saved_answers = sess.get("answers", {})
    all_answers = {**saved_answers, **answers}

    session_questions: list[dict[str, Any]] = sess.get("questions", [])

    # Backward compatibility fallback if old session had empty questions_json
    if not session_questions:
        past_papers = content_loader.get_past_papers_by_subject(blueprint["subject"])
        paper_questions = past_papers[0].questions if past_papers else []
        for q in paper_questions:
            session_questions.append({
                "number": q.number,
                "question_id": q.question_id or f"mock-q-{q.number}",
                "stem": q.stem or f"ข้อสอบข้อที่ {q.number} ({q.topic})",
                "topic": q.topic,
                "skill": q.skill,
                "answer_type": q.answer_type or ("single_choice" if str(q.correct_answer) in {"1", "2", "3", "4", "5"} else "numeric"),
                "options": [{"id": opt.id, "text": opt.text} for opt in (q.options or [])],
                "correct_answer": str(q.correct_answer).strip(),
                "tolerance": q.tolerance or 0.001,
                "unit": q.unit,
                "require_unit": q.require_unit,
                "score": q.score,
            })

    total_score = 0.0
    correct_count = 0
    max_score = sess["max_score"]
    total_q = len(session_questions)

    detailed_results = []
    topic_breakdown: dict[str, dict[str, Any]] = {}

    for q in session_questions:
        num = q["number"]
        num_str = str(num)
        user_ans = all_answers.get(num_str, "").strip()
        expected_ans = str(q.get("correct_answer", "")).strip()
        score_weight = float(q.get("score", 1.0))
        topic = q.get("topic", "general")
        skill = q.get("skill", "general_problem_solving")
        ans_type = q.get("answer_type", "single_choice")
        tol = float(q.get("tolerance") or 0.001)
        unit = q.get("unit")
        req_unit = bool(q.get("require_unit", False))

        is_correct = False
        error_tag = None

        if user_ans:
            if ans_type == "single_choice":
                # Strict exact match only: choice 3 cannot match 3.05!
                is_correct = (user_ans.lower() == expected_ans.lower())
                if not is_correct:
                    error_tag = "wrong_choice"
            else:
                grade_res = grade_numeric_detailed(
                    user_ans,
                    expected_ans,
                    tolerance=tol,
                    expected_unit=unit,
                    require_unit=req_unit,
                )
                is_correct = grade_res.is_correct
                error_tag = grade_res.error_tag

        earned = score_weight if is_correct else 0.0
        if is_correct:
            correct_count += 1
            total_score += earned

        # Topic aggregation
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
                "number": num,
                "question_id": q.get("question_id"),
                "stem": q.get("stem"),
                "user_answer": user_ans,
                "correct_answer": expected_ans,
                "is_correct": is_correct,
                "error_tag": error_tag,
                "score_earned": earned,
                "max_score": score_weight,
                "topic": topic,
                "skill": skill,
                "unit": unit,
            }
        )

    score_pct = round((total_score / max_score * 100), 1) if max_score > 0 else 0.0
    avg_pace_min = round(time_spent_min / total_q, 2) if total_q > 0 else 0.0
    pace_status = "optimal" if avg_pace_min <= blueprint.get("pace_target_min", 3.0) else "slow"

    report = {
        "session_id": session_id,
        "title": sess["title"],
        "exam_type": exam_type,
        "time_spent_min": round(time_spent_min, 1),
        "total_questions": total_q,
        "correct_count": correct_count,
        "total_score": round(total_score, 1),
        "max_score": round(max_score, 1),
        "score_percent": score_pct,
        "avg_pace_min": avg_pace_min,
        "target_pace_min": blueprint.get("pace_target_min", 3.0),
        "pace_status": pace_status,
        "topic_breakdown": topic_breakdown,
        "detailed_results": detailed_results,
    }

    # Persist report and finalize session state
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
                json.dumps(all_answers, ensure_ascii=False),
                json.dumps(report, ensure_ascii=False),
                now_iso,
                session_id,
            ),
        )

    # Link mock exam attempts to learning history and spaced repetition queue
    from app.services.review_engine import record_attempt

    time_per_q = round((time_spent_min * 60.0) / total_q, 1) if total_q > 0 else 0.0
    for res in detailed_results:
        qid = res.get("question_id")
        user_ans = res.get("user_answer")
        if not qid or not user_ans:
            continue
        try:
            record_attempt(
                question_id=qid,
                subject=blueprint.get("subject", "physics"),
                topic=res.get("topic", "general"),
                user_answer=user_ans,
                is_correct=res.get("is_correct", False),
                status="correct_first_try" if res.get("is_correct") else "wrong",
                confidence="sure",
                error_tag=res.get("error_tag"),
                time_spent_sec=time_per_q,
            )
        except Exception:
            pass

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
