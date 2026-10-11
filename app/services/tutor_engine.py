from typing import Any

from app.models.content_schema import Question
from app.services.content_loader import content_loader
from app.services.learning_path import get_skill_remediation


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
    # If hints level 1 exists, use it to frame Given & Goal
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

    # 5. Targeted Variant / Remediation
    remediation = get_skill_remediation(question.skills.primary)
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
            "title": "ขั้นที่ 5: โจทย์ฝึกซ้ำในหลักการเดียวกัน",
            "remediation_drill": remediation,
            "recommended_similar_question": similar_q,
        },
    }
