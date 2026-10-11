from pathlib import Path
from typing import Any

import yaml

from app.config import CONTENT_DIR
from app.models.content_schema import (
    AnswerConfig,
    ChoiceOption,
    FormulaCard,
    FullSolution,
    Hint,
    PastPaper,
    Question,
    SkillInfo,
    SolutionStep,
    SourceInfo,
    VerificationInfo,
)


class ContentLoader:
    def __init__(self, content_dir: Path = CONTENT_DIR):
        self.content_dir = content_dir
        self._questions: dict[str, Question] = {}
        self._formulas: dict[str, FormulaCard] = {}
        self._past_papers: dict[str, PastPaper] = {}
        self.reload()

    def reload(self) -> None:
        """
        Reloads all content from disk and validates schemas.
        Loads into temporary dictionaries and executes an atomic pointer swap
        to avoid exposing half-loaded or cleared state to concurrent readers.
        """
        new_questions: dict[str, Question] = {}
        new_formulas: dict[str, FormulaCard] = {}
        new_past_papers: dict[str, PastPaper] = {}

        # Load questions from subject directories
        for sub_dir in ["physics", "math", "tpat3", "tgat2", "imported"]:
            folder = self.content_dir / sub_dir
            if folder.exists():
                for yaml_file in sorted(folder.glob("*.yaml")):
                    self._load_question_file_into(yaml_file, new_questions)

        # Load formulas
        formula_folder = self.content_dir / "formulas"
        if formula_folder.exists():
            for yaml_file in sorted(formula_folder.glob("*.yaml")):
                self._load_formula_file_into(yaml_file, new_formulas)

        # Load past papers and adapt paper questions into main question catalog
        paper_folder = self.content_dir / "past_papers"
        if paper_folder.exists():
            for yaml_file in sorted(paper_folder.glob("*.yaml")):
                self._load_past_paper_file_into(yaml_file, new_past_papers, new_questions)

        # Atomic swap
        self._questions = new_questions
        self._formulas = new_formulas
        self._past_papers = new_past_papers

    def _load_question_file_into(
        self, file_path: Path, target_dict: dict[str, Question]
    ) -> None:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if isinstance(data, list):
                for item in data:
                    q = Question(**item)
                    target_dict[q.id] = q

    def _load_formula_file_into(
        self, file_path: Path, target_dict: dict[str, FormulaCard]
    ) -> None:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if isinstance(data, list):
                for item in data:
                    card = FormulaCard(**item)
                    target_dict[card.id] = card

    def _load_past_paper_file_into(
        self,
        file_path: Path,
        target_dict: dict[str, PastPaper],
        target_questions: dict[str, Question] | None = None,
    ) -> None:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if isinstance(data, dict):
                paper = PastPaper(**data)
                target_dict[paper.id] = paper

                # Adapt past paper questions into the main question bank
                if target_questions is not None and paper.questions:
                    for pq in paper.questions:
                        qid = pq.question_id or f"{paper.id}-q{pq.number}"
                        if qid not in target_questions:
                            adapted_q = self._adapt_past_paper_question(paper, pq)
                            if adapted_q is not None:
                                target_questions[qid] = adapted_q

    def _adapt_past_paper_question(self, paper: PastPaper, q: Any) -> Question | None:
        # Gating: Question must have a real non-empty stem
        if not q.stem or not str(q.stem).strip():
            return None

        qid = q.question_id or f"{paper.id}-q{q.number}"
        ans_type = q.answer_type
        correct_ans_str = str(q.correct_answer).strip()

        if not ans_type:
            if correct_ans_str.lower() in {"1", "2", "3", "4", "5", "a", "b", "c", "d", "e"}:
                ans_type = "single_choice"
            else:
                ans_type = "numeric"

        if ans_type == "single_choice":
            # Gating: Multiple choice must have authentic choice options (no dummy choices)
            if not q.options or len(q.options) < 2:
                return None

            options_list = []
            for opt in q.options:
                options_list.append(
                    ChoiceOption(
                        id=opt.id,
                        text=opt.text,
                        correct=(opt.id.strip().lower() == correct_ans_str.lower()),
                        explanation=getattr(opt, "explanation", None),
                        error_tag=getattr(opt, "error_tag", None),
                    )
                )
            ans_config = AnswerConfig(type="single_choice", options=options_list)
        else:
            ans_config = AnswerConfig(
                type="numeric",
                correct_value=correct_ans_str,
                unit=q.unit,
                tolerance=q.tolerance or 0.001,
                require_unit=q.require_unit,
            )

        sol_summary = q.solution or f"คำตอบที่ถูกต้องคือ {correct_ans_str}"
        full_sol = FullSolution(
            steps=[SolutionStep(id="s1", text=sol_summary)],
            summary=sol_summary,
        )

        # Inherit honest source and verification metadata from the past paper definition
        source_type = getattr(paper, "source_type", None) or "simulated_blueprint"
        tier = getattr(paper, "verification_tier", None) or "B"
        status = getattr(paper, "verification_status", None) or "reviewed"
        verified_by = getattr(paper, "verified_by", None) or "automated_assertion"

        return Question(
            id=qid,
            subject=paper.subject,
            topic=q.topic,
            source=SourceInfo(
                type=source_type,
                label=f"{paper.title} ข้อ {q.number}",
                exam_year=paper.year,
                item_number=q.number,
            ),
            verification=VerificationInfo(
                tier=tier,
                verified_by=verified_by,
                status=status,
            ),
            skills=SkillInfo(primary=q.skill, secondary=[]),
            stem=q.stem,
            answer=ans_config,
            difficulty=3,
            estimated_seconds=180 if paper.subject in ["physics", "math"] else 150,
            hints=[
                Hint(level=1, text="ทบทวนข้อมูลที่โจทย์กำหนดและเป้าหมายที่ต้องการหา"),
                Hint(level=2, text="เลือกกฎหรือสมการที่เหมาะสม และตรวจสอบความสอดคล้องของหน่วย"),
            ],
            solution=full_sol,
        )

    def get_all_questions(self, verified_only: bool = False) -> list[Question]:
        questions = list(self._questions.values())
        if verified_only:
            return [
                q
                for q in questions
                if q.verification.status in ["verified", "reviewed"]
                and q.verification.tier in ["A", "B", "C"]
            ]
        return questions

    def get_question_by_id(self, qid: str) -> Question | None:
        return self._questions.get(qid)

    def get_questions_by_subject(
        self, subject: str, verified_only: bool = False
    ) -> list[Question]:
        return [
            q
            for q in self.get_all_questions(verified_only=verified_only)
            if q.subject == subject
        ]

    def get_questions_by_topic(
        self, topic: str, verified_only: bool = False
    ) -> list[Question]:
        return [
            q
            for q in self.get_all_questions(verified_only=verified_only)
            if q.topic == topic
        ]

    def get_all_formulas(self) -> list[FormulaCard]:
        return list(self._formulas.values())

    def get_formula_by_id(self, fid: str) -> FormulaCard | None:
        return self._formulas.get(fid)

    def get_all_past_papers(self) -> list[PastPaper]:
        return list(self._past_papers.values())

    def get_past_papers_by_subject(self, subject: str) -> list[PastPaper]:
        return [p for p in self.get_all_past_papers() if p.subject == subject]

    def get_past_paper_by_id(self, pid: str) -> PastPaper | None:
        return self._past_papers.get(pid)


# Global singleton
content_loader = ContentLoader()
