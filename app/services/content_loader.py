from pathlib import Path

import yaml

from app.config import CONTENT_DIR
from app.models.content_schema import FormulaCard, PastPaper, Question


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

        # Load past papers
        paper_folder = self.content_dir / "past_papers"
        if paper_folder.exists():
            for yaml_file in sorted(paper_folder.glob("*.yaml")):
                self._load_past_paper_file_into(yaml_file, new_past_papers)

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
        self, file_path: Path, target_dict: dict[str, PastPaper]
    ) -> None:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if isinstance(data, dict):
                paper = PastPaper(**data)
                target_dict[paper.id] = paper

    def get_all_questions(self, verified_only: bool = False) -> list[Question]:
        questions = list(self._questions.values())
        if verified_only:
            return [q for q in questions if q.verification.tier in ["A", "B", "C"]]
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
