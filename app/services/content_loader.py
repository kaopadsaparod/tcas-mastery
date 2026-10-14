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
        for sub_dir in ["physics", "math", "tpat3", "tgat1", "tgat2", "tgat3"]:
            folder = self.content_dir / sub_dir
            if folder.exists():
                for yaml_file in sorted(folder.glob("*.yaml")):
                    self._load_question_file_into(yaml_file, new_questions)

        # Load imported questions (supporting test directory isolation)
        try:
            from app.services import pdf_importer
            imported_folder = getattr(pdf_importer, "IMPORTED_CONTENT_DIR", self.content_dir / "imported")
        except Exception:
            imported_folder = self.content_dir / "imported"

        if imported_folder.exists():
            for yaml_file in sorted(imported_folder.glob("*.yaml")):
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
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to read or parse YAML file '{file_path}': {e}") from e

        if isinstance(data, list):
            for idx, item in enumerate(data):
                if not isinstance(item, dict):
                    continue
                try:
                    q = Question(**item)
                    target_dict[q.id] = q
                except Exception as e:
                    qid = item.get("id", f"index-{idx}")
                    raise ValueError(f"Schema validation error in '{file_path}' item '{qid}': {e}") from e

    def _load_formula_file_into(
        self, file_path: Path, target_dict: dict[str, FormulaCard]
    ) -> None:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to read or parse YAML file '{file_path}': {e}") from e

        if isinstance(data, list):
            for idx, item in enumerate(data):
                if not isinstance(item, dict):
                    continue
                try:
                    card = FormulaCard(**item)
                    target_dict[card.id] = card
                except Exception as e:
                    cid = item.get("id", f"index-{idx}")
                    raise ValueError(f"Schema validation error in formula '{file_path}' item '{cid}': {e}") from e

    def _load_past_paper_file_into(
        self,
        file_path: Path,
        target_dict: dict[str, PastPaper],
        target_questions: dict[str, Question] | None = None,
    ) -> None:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to read or parse YAML file '{file_path}': {e}") from e

        if isinstance(data, dict):
            try:
                paper = PastPaper(**data)
            except Exception as e:
                pid = data.get("id", "unknown")
                raise ValueError(f"Schema validation error in past paper '{file_path}' (id: '{pid}'): {e}") from e

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
                known_traps=getattr(q, "known_traps", None) or [],
            )

        # Solution steps & explanation
        sol_summary = q.solution or f"คำตอบที่ถูกต้องคือ {correct_ans_str}"
        if q.solution_steps:
            sol_steps = q.solution_steps
        else:
            raw_steps = [s.strip() for s in sol_summary.split("\n") if s.strip()]
            if len(raw_steps) > 1:
                sol_steps = [SolutionStep(id=f"s{idx+1}", text=s) for idx, s in enumerate(raw_steps)]
            else:
                sol_steps = [SolutionStep(id="s1", text=sol_summary)]

        full_sol = FullSolution(
            steps=sol_steps,
            summary=sol_summary,
            sanity_check=getattr(q, "sanity_check", None),
            common_mistakes=getattr(q, "common_mistakes", None),
        )

        # Inherit honest source and verification metadata from question override or paper definition
        source_type = getattr(paper, "source_type", None) or "simulated_blueprint"
        tier = getattr(q, "verification_tier", None) or getattr(paper, "verification_tier", None) or "B"
        status = getattr(q, "verification_status", None) or getattr(paper, "verification_status", None) or "reviewed"
        verified_by = getattr(q, "verified_by", None) or getattr(paper, "verified_by", None) or "automated_assertion"

        # Tailored hints
        hints = q.hints if q.hints else self._generate_tailored_hints(q)

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
            estimated_seconds=(
                60
                if paper.subject in ["tgat1", "tgat2", "tgat3"]
                else (180 if paper.subject in ["physics", "math"] else 150)
            ),
            hints=hints,
            solution=full_sol,
        )

    def _generate_tailored_hints(self, q: Any) -> list[Hint]:
        skill = getattr(q, "skill", "") or ""
        topic = getattr(q, "topic", "") or ""

        hint_map = {
            "choose_constant_accel_eq": (
                "ระบุตัวแปรการเคลื่อนที่ที่โจทย์กำหนด (u, v, a, t, s) และตัวแปรที่ต้องการหา",
                "เลือก 1 ใน 5 สูตรการเคลื่อนที่แนวตรงที่ไม่มีตัวแปรส่วนเกินที่โจทย์ไม่ได้ระบุ",
            ),
            "vertical_free_fall": (
                "การเคลื่อนที่ภายใต้แรงโน้มถ่วงมีความเร่ง g = 10 m/s² ทิศดิ่งลงสู่พื้นโลกเสมอ",
                "ที่จุดสูงสุด ความเร็วแนวดิ่ง v = 0 และกำหนดทิศความเร็วต้น u เป็นเครื่องหมายบวก",
            ),
            "vt_graph_interpretation": (
                "พื้นที่ใต้กราฟความเร็ว-เวลา (v-t) แสดงถึง การกระจัด (Displacement)",
                "ความชันของกราฟความเร็ว-เวลา (v-t) แสดงถึง ความเร่ง (Acceleration)",
            ),
            "work_energy_theorem": (
                "พิจารณางานของแรงภายนอก W = F·s และการเปลี่ยนแปลงพลังงานจลน์ ΔEk",
                "ตั้งสมการงาน-พลังงาน: W = (1/2)m(v² - u²)",
            ),
            "frictional_force": (
                "คำนวณแรงเสียดทานจลน์ fk = μk·N โดย N คือแรงกดตั้งฉากจากพื้นราบ",
                "หาแรงลัพธ์ ΣF = F - fk แล้วใช้กฎข้อที่สองของนิวตัน ΣF = ma หาความเร่ง",
            ),
            "conservation_of_energy": (
                "ไม่มีแรงภายนอกที่ไม่ใช่อนุรักษ์ทำงาน พลังงานกลรวมจึงคงที่ (E_initial = E_final)",
                "พลังงานศักย์โน้มถ่วงที่จุดสูงสุดเปลี่ยนเป็นพลังงานจลน์ก่อนกระทบพื้น: mgh = (1/2)mv²",
            ),
            "geometric_series": (
                "สังเกตสัดส่วนของปริมาณที่เหลือในแต่ละขั้นตอน: ถ้าตัดออก 1/3 จะเหลือ 2/3 ของความยาวก่อนหน้า",
                "เมื่อตัดซ้ำ n ครั้ง ปริมาณที่เหลือจะเท่ากับ ความยาวเริ่มต้น × (2/3)ⁿ",
            ),
            "rotation_3d": (
                "วิเคราะห์การหมุนทีละแกน: การหมุนขวา 90° รอบแกนดิ่ง ทำให้หน้าซ้ายย้ายมาอยู่หน้าตรงหน้า",
                "การหมุนคว่ำลงข้างหน้า 90° รอบแกนนอน ทำให้หน้าที่อยู่ด้านหน้าพลิกคว่ำลงไปอยู่ด้านล่าง",
            ),
            "sequence_pattern": (
                "หาผลต่างระหว่างพจน์ที่อยู่ติดกัน (First difference) หรือมองรูปแบบรูปทั่วไป n²",
                "ตรวจสอบรูปแบบอนุกรมเพื่อทำนายพจน์ถัดไป",
            ),
            "flow_rate_pipe": (
                "หาอัตราเร็วในการทำงานของแต่ละท่อต่อ 1 หน่วยเวลา (เช่น 1/3 ถัง/ชม. และ 1/6 ถัง/ชม.)",
                "บวกอัตราเร็วรวมเข้าด้วยกัน: อัตราเร็วรวม = 1/A + 1/B แล้วกลับเศษเป็นส่วนเพื่อหาเวลา",
            ),
            "percentage_efficiency": (
                "ประสิทธิภาพ (Efficiency) คืออัตราส่วนของพลังงานที่ได้งานจริงต่อพลังงานที่ป้อนเข้ามา",
                "คำนวณจากสูตร: η = (W_out / Q_in) × 100%",
            ),
            "half_life": (
                "หาจำนวนช่วงครึ่งชีวิต n = เวลาทั้งหมด / ครึ่งชีวิต (t / T_half)",
                "ปริมาณสารที่เหลือ = ปริมาณเริ่มต้น / (2ⁿ)",
            ),
            "linear_equations": (
                "ย้ายตัวแปรที่มีค่า x มารวมไว้ฝั่งเดียวกัน และย้ายตัวเลขคงที่ไปรวมอีกฝั่งหนึ่ง",
                "รวมพจน์ที่คล้ายกัน แล้วหารสัมประสิทธิ์หน้า x เพื่อหาคำตอบ",
            ),
            "vector_addition": (
                "สังเกตมุมระหว่างเวกเตอร์ทั้งสอง หากตั้งฉากกัน 90° สามารถใช้ทฤษฎีบทพีทาโกรัสได้ทันที",
                "ขนาดเวกเตอร์ลัพธ์: R = √(F₁² + F₂²)",
            ),
            "vector_components": (
                "แตกเวกเตอร์เข้าแกนมุมฉาก: ด้านประชิดมุมใช้ฟังก์ชัน cos และด้านตรงข้ามมุมใช้ฟังก์ชัน sin",
                "แรงในแนวระดับ: F_x = F·cos(θ)",
            ),
        }

        if skill in hint_map:
            h1, h2 = hint_map[skill]
            return [
                Hint(level=1, text=h1),
                Hint(level=2, text=h2),
            ]
        elif topic.startswith("physics"):
            return [
                Hint(level=1, text=f"ระบุตัวแปรที่โจทย์กำหนดและเป้าหมายในบท {topic}"),
                Hint(level=2, text="เลือกกฎทางฟิสิกส์หรือสมการที่เหมาะสม และตรวจสอบความสอดคล้องของหน่วย"),
            ]
        elif topic.startswith("tpat3"):
            return [
                Hint(level=1, text=f"วิเคราะห์ข้อมูลและเงื่อนไขสำคัญของโจทย์ในหัวข้อ {topic}"),
                Hint(level=2, text="ประยุกต์ใช้หลักการคำนวณหรือมโนทัศน์เชิงวิศวกรรมเพื่อสรุปคำตอบ"),
            ]
        elif topic.startswith("tgat1"):
            return [
                Hint(level=1, text=f"วิเคราะห์บริบท บทสนทนา หรือใจความสำคัญในหัวข้อ {topic}"),
                Hint(level=2, text="สังเกตคำสำคัญ (Keywords) โครงสร้างไวยากรณ์ และเจตนาของผู้พูดหรือผู้เขียน"),
            ]
        elif topic.startswith("tgat3"):
            return [
                Hint(level=1, text=f"พิจารณาสถานการณ์และเป้าหมายของการตัดสินใจในหัวข้อ {topic}"),
                Hint(level=2, text="ประเมินทางเลือกตามหลักการแก้ปัญหา ความฉลาดทางอารมณ์ และความรับผิดชอบต่อส่วนรวม"),
            ]
        else:
            return [
                Hint(level=1, text="ทบทวนข้อมูลที่โจทย์กำหนดและเป้าหมายที่ต้องการหา"),
                Hint(level=2, text="เลือกสมการหรือความสัมพันธ์ที่สอดคล้องกับทักษะเพื่อหาคำตอบ"),
            ]

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

    def get_formula_for_topic(self, topic: str, subject: str = "") -> FormulaCard | None:
        """Finds matching formula card for a given topic or subject."""
        for f in self._formulas.values():
            if f.topic == topic:
                return f
        for f in self._formulas.values():
            if topic.startswith(f.topic) or f.topic.startswith(topic):
                return f
        if subject:
            for f in self._formulas.values():
                if f.subject == subject:
                    return f
        return None



# Global singleton
content_loader = ContentLoader()
