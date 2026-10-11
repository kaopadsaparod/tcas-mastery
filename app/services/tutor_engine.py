import math
import random
import uuid
from typing import Any

from app.models.content_schema import Question
from app.services.content_loader import content_loader
from app.services.grader import grade_numeric
from app.services.learning_path import get_skill_remediation
from app.services.procedural_gen import generate_random_drill
from app.services.review_engine import record_attempt


ERROR_CLASSIFICATIONS: dict[str, dict[str, str]] = {
    "unit": {
        "category": "unit",
        "title": "ข้อผิดพลาดเรื่องหน่วยและการแปลงมิติ (Unit & Dimension)",
        "description": "ลืมแปลงหน่วยให้อยู่ในระบบ SI หรือใช้หน่วยที่ขัดแย้งกันในสมการเดียวกัน",
        "strategy": "ตรวจสอบหน่วยของตัวแปรทุกตัวก่อนแทนค่า โดยเฉพาะ km/h -> m/s หรือ cm -> m",
    },
    "formula": {
        "category": "formula",
        "title": "การเลือกสมการและเงื่อนไข (Formula Selection)",
        "description": "เลือกสูตรไม่ตรงกับตัวแปรที่โจทย์กำหนด หรือใช้สูตรที่ขัดแย้งกับสภาวะของโจทย์ (เช่น ใช้สูตรความเร็วคงที่ในโจทย์ที่มีความเร่ง)",
        "strategy": "เขียนรายการตัวแปรที่รู้ค่า (Given) และตัวแปรที่ต้องการหา (Goal) ก่อน แล้วเลือกสูตรที่ไม่มีตัวแปรส่วนเกิน",
    },
    "concept": {
        "category": "concept",
        "title": "ความเข้าใจเชิงมโนทัศน์ (Physics Concept)",
        "description": "เข้าใจหลักการทางฟิสิกส์คลาดเคลื่อน เช่น ลืมคิดแรงเสียดทาน หรือสับสนระหว่างเวกเตอร์ความเร็วกับความเร่ง",
        "strategy": "วาดภาพ Free Body Diagram (FBD) และตั้งแกนอ้างอิงให้ชัดเจนก่อนเริ่มต้นคำนวณ",
    },
    "calculation": {
        "category": "calculation",
        "title": "ทักษะการคำนวณและพีชคณิต (Arithmetic & Algebra)",
        "description": "คำนวณตัวเลข ย้ายข้างสมการ หรือจัดการเลขยกกำลังผิดพลาด ทั้งที่เลือกสูตรถูกต้องแล้ว",
        "strategy": "เขียนขั้นตอนการย้ายข้างทีละบรรทัด และฝึกเทคนิคคิดเลขในใจด้วยตัวเลขลงตัว",
    },
    "reading": {
        "category": "reading",
        "title": "การตีความโจทย์และเครื่องหมายเวกเตอร์ (Reading & Signs)",
        "description": "กำหนดเครื่องหมายบวก/ลบของเวกเตอร์ขัดแย้งกับทิศทาง หรือมองข้ามเงื่อนไขสำคัญที่โจทย์ซ่อนไว้",
        "strategy": "กำหนดทิศทางบวกคงที่ตั้งแต่ต้น เช่น ให้ทิศของความเร็วต้น u เป็นบวกเสมอ",
    },
}


def classify_error_cause(error_tag: str | None, question: Question | None = None) -> dict[str, str]:
    """
    Classifies the student's mistake into one of the 5 pedagogical root causes.
    """
    if not error_tag:
        return ERROR_CLASSIFICATIONS["reading"]

    tag = error_tag.lower()
    if tag in {"no_unit_conversion", "missing_unit", "unit_error", "unit_kmh_to_ms"}:
        return ERROR_CLASSIFICATIONS["unit"]
    elif tag in {"choose_constant_accel_eq", "wrong_formula", "wrong_equation", "missing_factor_2"}:
        return ERROR_CLASSIFICATIONS["formula"]
    elif tag in {"forgot_friction", "sign_error_friction", "concept_error", "mass_error"}:
        return ERROR_CLASSIFICATIONS["concept"]
    elif tag in {"arithmetic_error", "squared_error", "rearrange_error", "math_error"}:
        return ERROR_CLASSIFICATIONS["calculation"]
    else:
        return ERROR_CLASSIFICATIONS["reading"]


def build_tutor_breakdown(
    question: Question,
    user_answer: str | None = None,
    error_tag: str | None = None,
) -> dict[str, Any]:
    """
    Constructs a 5-step pedagogical explanation breakdown
    tailored to guiding the student's thinking process after an error.
    """
    # 1. Given & Goal
    stem = question.stem
    h1 = next((h.text for h in question.hints if h.level == 1), None)
    given_goal_text = h1 or f"วิเคราะห์ข้อมูลจากโจทย์: {stem[:120]}..."

    # 2. Principle & Formula
    plan_prompt = question.plan_step.prompt if question.plan_step else None
    plan_explanation = question.plan_step.explanation if question.plan_step else None
    principle_text = (
        plan_explanation
        or "เลือกกฎหรือสมการฟิสิกส์ที่ตรงกับเงื่อนไข โดยตัดตัวแปรที่โจทย์ไม่ได้ระบุหรือไม่ต้องการหาออกไป"
    )

    # 3. Step-by-Step Substitution & Units
    steps_data = []
    if question.solution and question.solution.steps:
        for s in question.solution.steps:
            steps_data.append({"id": s.id, "text": s.text, "math": s.math})
    elif question.solution_steps:
        for s in question.solution_steps:
            steps_data.append({"id": s.id, "text": s.text, "math": s.math})
    else:
        summary = question.solution.summary if question.solution else "ดูเฉลยละเอียดประจำข้อ"
        steps_data.append({"id": "s1", "text": summary, "math": None})

    # 4. Sanity Check
    sanity_text = (
        question.solution.sanity_check
        if question.solution and question.solution.sanity_check
        else "ตรวจสอบความสมเหตุสมผล: ทิศทาง เครื่องหมายเวกเตอร์ และขนาดของตัวเลขอยู่ในช่วงที่เป็นไปได้ในชีวิตจริงหรือไม่"
    )

    # 5. Targeted Variant & Root Cause Analysis
    classification = classify_error_cause(error_tag, question)
    remediation = get_skill_remediation(question.skills.primary)

    # Find a different question measuring the same skill or topic
    similar_q = None
    all_qs = content_loader.get_all_questions()
    for q in all_qs:
        if q.id != question.id and q.topic == question.topic:
            similar_q = {
                "id": q.id,
                "stem": q.stem[:80] + ("..." if len(q.stem) > 80 else ""),
                "skill": q.skills.primary,
            }
            break

    return {
        "question_id": question.id,
        "topic": question.topic,
        "primary_skill": question.skills.primary,
        "error_tag": error_tag,
        "error_classification": classification,
        "step_1_given_goal": {
            "title": "ขั้นที่ 1: สิ่งที่โจทย์กำหนดและสิ่งที่ถามหา",
            "content": given_goal_text,
        },
        "step_2_principle": {
            "title": "ขั้นที่ 2: หลักการและสูตรที่เกี่ยวข้อง",
            "prompt": plan_prompt,
            "content": principle_text,
        },
        "step_3_substitution": {
            "title": "ขั้นที่ 3: แทนค่าทีละขั้นและตรวจสอบหน่วย",
            "steps": steps_data,
        },
        "step_4_sanity_check": {
            "title": "ขั้นที่ 4: การตรวจความสมเหตุสมผลของคำตอบ",
            "content": sanity_text,
        },
        "step_5_variant": {
            "title": "ขั้นที่ 5: แบบฝึกซ่อมจุดอ่อนและโจทย์ใหม่วัดทักษะเดิม",
            "error_analysis": classification,
            "remediation_drill": remediation,
            "recommended_similar_question": similar_q,
        },
    }


def generate_skill_variant(question_id: str) -> dict[str, Any]:
    """
    Generates a brand-new, unseen variant question that tests the exact same skill
    as the missed question, ensuring the student does not simply memorize the answer key.
    """
    orig_q = content_loader.get_question_by_id(question_id)
    if not orig_q:
        raise ValueError(f"Question not found: {question_id}")

    skill = orig_q.skills.primary
    variant_id = f"var-{uuid.uuid4().hex[:8]}"

    # Procedural skill variants for unit conversions and 1D kinematics
    if "kmh" in skill or "unit" in skill:
        drill = generate_random_drill("unit_kmh_ms")
        return {
            "variant_id": variant_id,
            "original_question_id": orig_q.id,
            "skill": skill,
            "topic": orig_q.topic,
            "type": "numeric",
            "stem": drill["stem"],
            "expected_answer": drill["expected_answer"],
            "unit": drill["unit"],
            "tolerance": 0.001,
            "hint": drill.get("hint"),
            "explanation": drill.get("explanation"),
        }
    elif "accel" in skill or "kinematics" in skill or "free_fall" in skill:
        drill = generate_random_drill("kinematics_5eq")
        return {
            "variant_id": variant_id,
            "original_question_id": orig_q.id,
            "skill": skill,
            "topic": orig_q.topic,
            "type": "numeric",
            "stem": drill["stem"],
            "expected_answer": drill["expected_answer"],
            "unit": drill["unit"],
            "tolerance": 0.001,
            "hint": drill.get("hint"),
            "explanation": drill.get("explanation"),
        }
    else:
        # Fallback to scaling / proportions variant
        drill = generate_random_drill("fractions_powers")
        return {
            "variant_id": variant_id,
            "original_question_id": orig_q.id,
            "skill": skill,
            "topic": orig_q.topic,
            "type": "numeric",
            "stem": drill["stem"],
            "expected_answer": drill["expected_answer"],
            "unit": drill.get("unit"),
            "tolerance": 0.001,
            "hint": drill.get("hint"),
            "explanation": drill.get("explanation"),
        }


def evaluate_remediation_variant(
    original_question_id: str,
    user_answer: str,
    expected_answer: str,
    tolerance: float = 0.001,
    expected_unit: str | None = None,
) -> dict[str, Any]:
    """
    Evaluates the student's solution to the remediation variant question.
    If solved correctly: records success and updates honest mastery in the DB.
    If missed: records attempt and prioritizes for urgent Spaced Review.
    """
    orig_q = content_loader.get_question_by_id(original_question_id)
    topic = orig_q.topic if orig_q else "general"
    subject = orig_q.subject if orig_q else "physics"

    is_correct = grade_numeric(
        user_answer,
        expected_answer,
        tolerance=tolerance,
        expected_unit=expected_unit,
    )

    status = "remediation_passed" if is_correct else "remediation_failed"

    # Persist attempt to SQLite to update Honest Mastery and Spaced Repetition queue
    queue_rec = record_attempt(
        question_id=original_question_id,
        subject=subject,
        topic=topic,
        user_answer=user_answer,
        is_correct=is_correct,
        status=status,
        confidence="sure" if is_correct else "guessed",
        hints_opened=0,
    )

    if is_correct:
        feedback = "🎉 ยอดเยี่ยมมาก! คุณทำโจทย์ใหม่ที่วัดทักษะเดิมผ่านเรียบร้อย แสดงว่าเข้าใจหลักการจริง ระบบปรับคะแนนความแม่นยำและเลื่อนรอบทบทวนความจำให้แล้ว"
    else:
        feedback = "💡 ยังคำนวณไม่ถูกต้อง ระบบได้นำหัวข้อนี้เข้าคิวทบทวนเร่งด่วนใน Study Planner วันนี้ เพื่อให้คุณได้ฝึกซ้ำจนมั่นใจ"

    return {
        "is_correct": is_correct,
        "status": status,
        "feedback": feedback,
        "next_review_interval_days": queue_rec["interval_days"],
        "next_review_at": queue_rec["next_review_at"],
    }
