from typing import Any

from pydantic import BaseModel


class SubmitAttemptRequest(BaseModel):
    question_id: str
    user_answer: str
    confidence: str = "sure"  # 'sure', 'unsure', 'guessed'
    hints_opened: int = 0  # 0, 1, 2, 3
    plan_step_answer: str | None = None
    time_spent_sec: float = 0.0
    review_time_sec: float = 0.0


class SubmitAttemptResponse(BaseModel):
    is_correct: bool
    status: str  # 'correct_first_try', 'correct_assisted', 'wrong'
    error_tag: str | None = None
    error_tag_description: str | None = None
    explanation: str | None = None
    correct_answer: str
    plan_step_correct: bool | None = None
    next_review_interval_days: int
    pace_status: str | None = None  # 'fast', 'optimal', 'slow', 'untracked'
    pace_target_sec: float | None = None
    pace_feedback: str | None = None


class ProceduralSubmitRequest(BaseModel):
    drill_type: str
    question_stem: str
    user_answer: str
    expected_answer: str
    expected_unit: str | None = None
    tolerance: float = 0.001
    time_spent_sec: float = 0.0


class ProceduralSubmitResponse(BaseModel):
    is_correct: bool
    normalized_user_answer: str
    expected_answer: str
    explanation: str
    error_tag: str | None = None


class AnswerSheetSubmitRequest(BaseModel):
    paper_id: str
    answers: dict[str, str]  # {"1": "3", "2": "1", ...}
    time_taken_min: float = 0.0


class AnswerSheetSubmitResponse(BaseModel):
    paper_id: str
    paper_title: str
    total_questions: int
    correct_count: int
    total_score: float
    max_score: float
    score_percent: float
    breakdown_by_topic: dict[str, dict[str, Any]]
    detailed_results: list[dict[str, Any]]


class FormulaRecallSubmitRequest(BaseModel):
    formula_id: str
    question_index: int
    user_answer: str


class FormulaRecallSubmitResponse(BaseModel):
    is_correct: bool
    correct_answer: str
    explanation: str
