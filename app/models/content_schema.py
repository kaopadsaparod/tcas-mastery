from typing import Any, Literal

from pydantic import BaseModel, Field


class SourceInfo(BaseModel):
    type: Literal["official", "textbook", "invented", "exam_prep"] = "invented"
    label: str
    exam_year: int | None = None
    round: str | None = None


class VerificationInfo(BaseModel):
    tier: Literal["A", "B", "C", "D", "E"] = "B"
    verified_by: str = "automated_assertion"
    notes: str | None = None


class SkillInfo(BaseModel):
    primary: str
    secondary: list[str] = Field(default_factory=list)


class PlanStep(BaseModel):
    prompt: str
    options: dict[str, str]  # e.g. {"a": "v = u + at", "b": "v^2 = u^2 + 2as"}
    answer: str  # e.g. "b"
    explanation: str | None = None


class Checkpoint(BaseModel):
    prompt: str
    answer: float | int | str
    skill: str | None = None
    tolerance: float | None = 0.02


class ChoiceOption(BaseModel):
    id: str  # e.g. "o1", "a", "1"
    text: str
    correct: bool = False
    error_tag: str | None = None
    explanation: str | None = None


class AnswerConfig(BaseModel):
    type: Literal["single_choice", "numeric"] = "single_choice"
    options: list[ChoiceOption] | None = None
    correct_value: float | int | str | None = None
    unit: str | None = None
    tolerance: float | None = 0.02


class Hint(BaseModel):
    level: (
        int  # 1 = Given/Find/Concept, 2 = Formula & Conditions, 3 = Guided calculation
    )
    text: str


class SolutionStep(BaseModel):
    id: str
    text: str
    math: str | None = None


class FullSolution(BaseModel):
    steps: list[SolutionStep] = Field(default_factory=list)
    summary: str | None = None
    common_mistakes: str | None = None
    sanity_check: str | None = None


class Question(BaseModel):
    id: str
    subject: str  # e.g. "physics", "math", "tpat3", "tgat2"
    topic: str  # e.g. "physics.kinematics.1d"
    source: SourceInfo
    verification: VerificationInfo
    skills: SkillInfo
    stem: str
    image_url: str | None = None
    plan_step: PlanStep | None = None
    checkpoints: list[Checkpoint] | None = None
    answer: AnswerConfig
    hints: list[Hint] = Field(default_factory=list)
    solution: FullSolution | None = None
    solution_steps: list[SolutionStep] | None = None


class FormulaCard(BaseModel):
    id: str
    subject: str
    topic: str
    title: str
    latex: str
    conditions: list[str]
    variables: dict[str, str]
    selection_cues: list[str]
    recall_questions: list[dict[str, Any]] = Field(default_factory=list)


class PastPaperQuestion(BaseModel):
    number: int
    correct_answer: str  # "1", "2", "3", "4", "5" or numeric value string
    topic: str
    skill: str
    score: float = 1.0


class PastPaper(BaseModel):
    id: str
    title: str
    subject: str
    year: int
    time_limit_min: int = 90
    questions: list[PastPaperQuestion]
