import json
from typing import Any

from app.database import get_db
from app.models.api_schema import AnswerSheetSubmitResponse
from app.models.content_schema import PastPaper
from app.services.grader import grade_numeric


def grade_answer_sheet(
    paper: PastPaper, submitted_answers: dict[str, str], time_taken_min: float = 0.0
) -> AnswerSheetSubmitResponse:
    """
    Evaluates paper exam responses entered via the answer sheet interface.
    Computes score, percentage, breakdown by topic, and stores submission history in SQLite.
    """
    total_score = 0.0
    max_score = 0.0
    correct_count = 0
    total_questions = len(paper.questions)

    breakdown_by_topic: dict[str, dict[str, Any]] = {}
    detailed_results = []

    for q in paper.questions:
        q_num_str = str(q.number)
        user_ans = submitted_answers.get(q_num_str, "").strip()
        expected_ans = str(q.correct_answer).strip()
        max_score += q.score

        # Check correctness: exact match or numeric tolerance match
        is_correct = False
        if user_ans:
            if user_ans.lower() == expected_ans.lower():
                is_correct = True
            elif grade_numeric(user_ans, expected_ans, tolerance=0.02):
                is_correct = True
        score_earned = q.score if is_correct else 0.0
        if is_correct:
            correct_count += 1
            total_score += score_earned

        # Update topic breakdown
        if q.topic not in breakdown_by_topic:
            breakdown_by_topic[q.topic] = {
                "topic": q.topic,
                "total_questions": 0,
                "correct_count": 0,
                "score_earned": 0.0,
                "max_score": 0.0,
            }

        breakdown_by_topic[q.topic]["total_questions"] += 1
        breakdown_by_topic[q.topic]["max_score"] += q.score
        if is_correct:
            breakdown_by_topic[q.topic]["correct_count"] += 1
            breakdown_by_topic[q.topic]["score_earned"] += score_earned

        detailed_results.append(
            {
                "number": q.number,
                "user_answer": user_ans,
                "correct_answer": expected_ans,
                "is_correct": is_correct,
                "topic": q.topic,
                "skill": q.skill,
                "score_earned": score_earned,
                "max_score": q.score,
            }
        )

    score_percent = round((total_score / max_score * 100), 2) if max_score > 0 else 0.0

    # Save to SQLite
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO answer_sheet_submissions (
                paper_id, paper_title, total_questions, correct_count,
                score_percent, answers_json, details_json, time_taken_min
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                paper.id,
                paper.title,
                total_questions,
                correct_count,
                score_percent,
                json.dumps(submitted_answers),
                json.dumps(detailed_results),
                time_taken_min,
            ),
        )

    return AnswerSheetSubmitResponse(
        paper_id=paper.id,
        paper_title=paper.title,
        total_questions=total_questions,
        correct_count=correct_count,
        total_score=total_score,
        max_score=max_score,
        score_percent=score_percent,
        breakdown_by_topic=breakdown_by_topic,
        detailed_results=detailed_results,
    )
