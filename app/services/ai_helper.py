from typing import Any

import httpx

from app.config import GEMINI_API_KEY
from app.models.content_schema import Question
from app.services.grader import ERROR_TAG_DESCRIPTIONS


def generate_ai_tutor_prompt(
    question: Question,
    user_answer: str,
    error_tag: str | None = None,
    current_step: str | None = None,
) -> str:
    """
    Constructs a context-rich prompt ready to be copied into ChatGPT/Claude/Gemini.
    Ensures zero cost and 100% user privacy unless the user explicitly copies it.
    """
    error_info = (
        f"- ข้อผิดพลาดที่ระบบตรวจพบ: {ERROR_TAG_DESCRIPTIONS.get(error_tag, error_tag)}"
        if error_tag
        else "- ผู้เรียนต้องการคำอธิบายเพิ่มเติมในข้อนี้"
    )

    solution_summary = ""
    if question.solution:
        steps_text = "\n".join([f"  {s.id}: {s.text}" for s in question.solution.steps])
        solution_summary = f"""
[เฉลยทางการที่ผ่านการตรวจสอบแล้ว]:
{steps_text}
- สรุป: {question.solution.summary or ""}
- จุดที่มักผิด: {question.solution.common_mistakes or ""}
"""

    prompt = f"""สวัสดีครับคุณครู/AI Tutor ผมกำลังฝึกทำโจทย์ข้อสอบ TCAS ข้อนี้อยู่ครับ:

[โจทย์]:
{question.stem.strip()}

[ข้อมูลของผม]:
- คำตอบที่ผมเลือกหรือตอบ: {user_answer}
{error_info}
{f"- ขั้นตอนที่ผมกำลังติดอยู่: {current_step}" if current_step else ""}
{solution_summary}
[คำขอ]:
กรุณาช่วยอธิบายทีละขั้นตอนให้ผมเข้าใจว่า:
1. เหตุใดคำตอบที่ผมเลือกถึงผิด และหลักการที่ถูกต้องคืออะไร
2. วิธีเลือกสูตรและการวิเคราะห์ตัวแปรที่ควรสังเกตในโจทย์ลักษณะนี้
(ขอคำอธิบายกระชับ ชัดเจน ใช้ภาษาที่เข้าใจง่ายสำหรับนักเรียนเตรียมสอบ TCAS ครับ)
"""
    return prompt.strip()


def generate_presolve_hint_prompt(question: Question) -> str:
    """
    Constructs a prompt to ask AI for guidance/hints during the thinking phase
    WITHOUT spoiling the final numerical or choice answer.
    """
    prompt = f"""สวัสดีครับคุณครู/AI Tutor ผมกำลังฝึกคิดโจทย์ข้อสอบ TCAS ข้อนี้ด้วยตัวเองอยู่ครับ:

[โจทย์]:
{question.stem.strip()}

[สิ่งที่ผมต้องการความช่วยเหลือ]:
1. ช่วยสรุป "สิ่งที่โจทย์กำหนดให้ (Given)" และ "สิ่งที่โจทย์ต้องการหา (Goal)"
2. แนะนำ "กรอบความคิด (Mental Framework)" หรือหลักการฟิสิกส์/คณิตศาสตร์ที่ควรใช้ในการตั้งต้น
3. มีจุดกับดักหรือข้อควรระวังใดที่ควรสังเกตเป็นพิเศษหรือไม่?

⚠️ คำขอพิเศษ: กรุณาอย่าเพิ่งบอกคำตอบสุดท้าย หรือแสดงตัวเลขผลลัพธ์สุดท้าย ขอเพียงคำใบ้และแนวทางให้ผมฝึกคำนวณต่อด้วยตัวเองครับ
"""
    return prompt.strip()


async def query_gemini_api(prompt: str, api_key: str | None = None) -> dict[str, Any]:
    """
    Optional direct call to Gemini 2.5/Flash API if an API key is provided.
    Returns the response or error details.
    """
    key = api_key or GEMINI_API_KEY
    if not key:
        return {"success": False, "error": "ไม่ได้ระบุ Gemini API Key"}

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return {"success": True, "text": text}
            else:
                return {
                    "success": False,
                    "error": f"API Error {resp.status_code}: {resp.text}",
                }
    except Exception as e:
        return {"success": False, "error": str(e)}
