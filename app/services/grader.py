import math
import re

from app.models.api_schema import SubmitAttemptResponse
from app.models.content_schema import Question

# Error tag explanation dictionary in Thai
ERROR_TAG_DESCRIPTIONS = {
    "no_unit_conversion": "ลืมแปลงหน่วย (เช่น ไม่ได้แปลง km/h เป็น m/s หรือ cm เป็น m)",
    "missing_factor_2": "ลืมตัวคูณ 2 หรือ 1/2 ในสมการ (เช่น เทอม 2as หรือ 1/2 at²)",
    "missing_factor_half": "ลืมตัวคูณ 1/2 ในสมการ",
    "sign_error": "เครื่องหมายเวกเตอร์หรือทิศทางผิด (เช่น ความเร่งเบรกหรือทิศพุ่งลงต้องติดลบ)",
    "sign_error_friction": "สับสนเครื่องหมายของแรงเสียดทาน (แรงเสียดทานต้องมีทิศต้านการเคลื่อนที่)",
    "rearrange_error": "ย้ายข้างสมการพีชคณิตผิดพลาด",
    "forgot_friction": "ลืมคิดผลของแรงเสียดทานในระบบ",
    "only_to_peak": "คำนวณเฉพาะช่วงขึ้นถึงจุดสูงสุด ยังไม่ได้คิดต่อจนถึงจุดตก",
    "return_to_cliff_level": "คิดเฉพาะเวลาที่ลอยกลับมาระดับเดิม ยังไม่ถึงพื้นหน้าผา",
    "rectangle_only": "คิดพื้นที่สี่เหลี่ยมผืนผ้าเต็มรูป โดยลืมว่าช่วงเร่ง/เบรกเป็นรูปสามเหลี่ยม",
    "triangle_only": "คิดพื้นที่สามเหลี่ยมเต็มรูป โดยลืมช่วงความเร็วคงตัว",
    "velocity_match_only": "สับสนระหว่าง 'ความเร็วเท่ากัน' กับ 'แล่นทันกัน (การกระจัดเท่ากัน)'",
    "forgot_domain_restriction": "ลืมเงื่อนไขตัวส่วนห้ามเป็นศูนย์ (เช่น x ≠ 2)",
    "cross_multiplied_denominator": "คูณไขว้ตัวแปรที่มีโอกาสติดลบทิ้งไปโดยไม่ระวังเครื่องหมายอสมการ",
    "intermediate_stage_only": "ตอบเฉพาะผลลัพธ์ของขั้นกลาง ยังไม่ได้คิดต่อจนถึงขั้นสุดท้าย",
    "inverse_ratio_flipped": "สลับเศษเป็นส่วนในอัตราส่วนผกผัน",
    "wrong_unit": "ระบุหน่วยไม่ตรงกับที่โจทย์ต้องการ หรือลืมแปลงหน่วย",
    "missing_unit": "ไม่ระบุหน่วยกำกับคำตอบ ทั้งที่โจทย์ต้องการให้ระบุหน่วย",
    "arithmetic_error": "คำนวณเลขหรือคิดเลขผิดพลาด",
    "peak_displacement_only": "ตอบระยะทางถึงจุดสูงสุด ลืมคิดการกระจัดที่แท้จริงหลังจากนั้น",
    "distance_instead_of_displacement": "สับสนระหว่าง 'ระยะทางจริง' กับ 'การกระจัด'",
}

UNIT_SYNONYMS: dict[str, set[str]] = {
    "m/s": {"m/s", "ms-1", "m s-1", "m.s-1", "m s^-1", "m.s^-1", "เมตร/วินาที", "เมตรต่อวินาที", "ม./วิ"},
    "km/h": {"km/h", "km/hr", "kmh", "กิโลเมตร/ชั่วโมง", "กม./ชม."},
    "m": {"m", "meter", "meters", "เมตร"},
    "cm": {"cm", "centimeter", "เซนติเมตร", "ซม."},
    "s": {"s", "sec", "second", "seconds", "วินาที", "วิ"},
    "m/s^2": {"m/s^2", "m/s2", "ms-2", "m s-2", "m.s-2", "m s^-2", "m.s^-2", "เมตร/วินาที^2", "เมตร/วินาที²", "เมตรต่อวินาที^2"},
    "n": {"n", "newton", "newtons", "นิวตัน"},
    "j": {"j", "joule", "joules", "จูล"},
    "w": {"w", "watt", "watts", "วัตต์"},
    "kg": {"kg", "kilogram", "กิโลกรัม", "กก."},
    "g": {"g", "gram", "กรัม"},
    "cm^2": {"cm^2", "cm2", "ตร.ซม.", "ตารางเซนติเมตร"},
    "m^2": {"m^2", "m2", "ตร.ม.", "ตารางเมตร"},
    "cm^3": {"cm^3", "cm3", "ลบ.ซม.", "ลูกบาศก์เซนติเมตร"},
    "m^3": {"m^3", "m3", "ลบ.ม.", "ลูกบาศก์เมตร"},
    "kg/m^3": {"kg/m^3", "kg/m3", "กก./ลบ.ม."},
    "g/cm^3": {"g/cm^3", "g/cm3", "กรัม/ลบ.ซม."},
    "เท่า": {"เท่า", "times", "x"},
    "%": {"%", "percent", "เปอร์เซ็นต์", "ร้อยละ"},
}


def clean_unit_str(u: str) -> str:
    """Cleans a unit string for canonical comparison."""
    u = u.strip().lower()
    u = re.sub(r"\\text\{([^}]+)\}", r"\1", u)
    u = (
        u.replace(" ", "")
        .replace("²", "2")
        .replace("³", "3")
        .replace("^", "")
        .replace(".", "")
        .replace("ต่อ", "/")
    )
    return u


def units_match(u1: str, u2: str) -> bool:
    """Checks whether two unit representations are mathematically/physically equivalent."""
    c1, c2 = clean_unit_str(u1), clean_unit_str(u2)
    if c1 == c2:
        return True
    for canon, syns in UNIT_SYNONYMS.items():
        syn_cleaned = {clean_unit_str(s) for s in syns} | {clean_unit_str(canon)}
        if c1 in syn_cleaned and c2 in syn_cleaned:
            return True
    return False


NUM_UNIT_PATTERN = re.compile(
    r"^\s*([+-]?\d+(?:,\d+)*(?:\.\d+)?\s*/\s*[+-]?\d+(?:,\d+)*(?:\.\d+)?|[+-]?\d+(?:,\d+)*(?:\.\d+)?(?:[eE][+-]?\d+|[x\*×]10\^?[+-]?\d+)?)\s*(.*)$",
    re.IGNORECASE,
)


def extract_number_and_unit(raw: str) -> tuple[str, str | None]:
    """
    Separates a raw answer string into (numeric_part, detected_unit).
    Deterministically extracts the numeric value first (including scientific notation and fractions),
    leaving the remaining string as the physical unit (supporting ms-1, m.s-1, m s^-1, kg/m^3).
    """
    s = str(raw).strip()
    s = s.replace("−", "-").replace("–", "-")
    thai_digits = str.maketrans("๑๒๓๔๕๖๗๘๙๐", "1234567890")
    s = s.translate(thai_digits)

    m = NUM_UNIT_PATTERN.match(s)
    if m:
        num_str = m.group(1).strip()
        unit_str = m.group(2).strip() or None
        return num_str, unit_str

    return s, None


def normalize_numeric_string(raw: str) -> float | None:
    """
    Normalizes a numeric string into a float.
    Handles:
    - Unicode minus '−' (U+2212) -> '-'
    - Thousands commas '1,000' -> '1000'
    - Fractions '3/4' -> 0.75
    - Scientific notation '2e3', '2*10^3', '2x10^3', '2×10^3' -> 2000.0
    - Thai digits '๑๒.๕' -> 12.5
    """
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None

    num_part, _ = extract_number_and_unit(s)
    s = num_part.replace(" ", "").replace(",", "")

    # Handle scientific notation variants like 2*10^3, 2x10^3, 2×10^3, 2*10**3
    sci_pattern = r"^([+-]?\d+(?:\.\d+)?)(?:[x\*×]10\^?([+-]?\d+)|e([+-]?\d+))$"
    sci_match = re.match(sci_pattern, s, re.IGNORECASE)
    if sci_match:
        base = float(sci_match.group(1))
        exp = sci_match.group(2) or sci_match.group(3)
        return base * (10 ** int(exp))

    # Handle fractions like '3/4' or '-1/2'
    if "/" in s:
        try:
            parts = s.split("/")
            if len(parts) == 2:
                num = float(parts[0])
                denom = float(parts[1])
                if denom != 0:
                    return num / denom
        except (ValueError, ZeroDivisionError):
            pass

    # Standard float parsing
    try:
        return float(s)
    except ValueError:
        return None


class NumericGradeResult(tuple):
    """
    Custom tuple subclass for full backward compatibility:
    Can be unpacked as `is_correct, error_tag = grade_numeric_detailed(...)`
    while also exposing rich attributes: .is_correct, .error_tag, .numeric_status, .unit_status.
    """
    is_correct: bool
    error_tag: str | None
    numeric_status: str  # 'correct', 'incorrect', 'invalid_number'
    unit_status: str     # 'correct', 'wrong_unit', 'missing_unit', 'not_required'

    def __new__(
        cls,
        is_correct: bool,
        error_tag: str | None,
        numeric_status: str = "correct",
        unit_status: str = "not_required",
    ):
        obj = super().__new__(cls, (is_correct, error_tag))
        obj.is_correct = is_correct
        obj.error_tag = error_tag
        obj.numeric_status = numeric_status
        obj.unit_status = unit_status
        return obj


def grade_numeric_detailed(
    user_input: str,
    expected_value: float | str,
    tolerance: float = 0.005,
    expected_unit: str | None = None,
    require_unit: bool = False,
) -> NumericGradeResult:
    """
    Deterministically grades numeric input, taking expected_unit and require_unit into account.
    Returns NumericGradeResult which behaves as (is_correct, error_tag).
    If user specifies a unit that differs from expected_unit, marks as wrong with 'no_unit_conversion'.
    If require_unit is True and no unit was given, marks as wrong with 'missing_unit'.
    """
    if user_input is None:
        return NumericGradeResult(
            False,
            None,
            numeric_status="invalid_number",
            unit_status="missing_unit" if require_unit else "not_required",
        )

    _, user_unit = extract_number_and_unit(str(user_input))

    # Evaluate unit status
    unit_status = "not_required"
    if expected_unit:
        if user_unit:
            if units_match(user_unit, expected_unit):
                unit_status = "correct"
            else:
                unit_status = "wrong_unit"
        else:
            if require_unit:
                unit_status = "missing_unit"
            else:
                unit_status = "not_required"

    u_val = normalize_numeric_string(user_input)
    if u_val is None:
        return NumericGradeResult(
            False, "arithmetic_error", numeric_status="invalid_number", unit_status=unit_status
        )
    e_val = normalize_numeric_string(str(expected_value))
    if e_val is None:
        return NumericGradeResult(
            False, None, numeric_status="invalid_number", unit_status=unit_status
        )

    if e_val == 0:
        is_numeric_ok = abs(u_val) < 1e-9
    else:
        # Scale absolute tolerance proportionally so small scientific values (e.g. 2e-6, 1.6e-19)
        # do not accept 0 or 5e-5 as correct
        scaled_abs_tol = min(1e-12, tolerance * abs(e_val))
        is_numeric_ok = math.isclose(u_val, e_val, rel_tol=tolerance, abs_tol=scaled_abs_tol)

    numeric_status = "correct" if is_numeric_ok else "incorrect"

    if unit_status == "wrong_unit":
        return NumericGradeResult(
            False, "no_unit_conversion", numeric_status=numeric_status, unit_status=unit_status
        )
    elif unit_status == "missing_unit":
        return NumericGradeResult(
            False, "missing_unit", numeric_status=numeric_status, unit_status=unit_status
        )
    elif not is_numeric_ok:
        return NumericGradeResult(
            False, "arithmetic_error", numeric_status=numeric_status, unit_status=unit_status
        )
    else:
        return NumericGradeResult(
            True, None, numeric_status=numeric_status, unit_status=unit_status
        )


def grade_numeric(
    user_input: str,
    expected_value: float | str,
    tolerance: float = 0.005,
    expected_unit: str | None = None,
    require_unit: bool = False,
) -> bool:
    """Grades a numeric user input against an expected value with percentage tolerance and optional unit validation."""
    res = grade_numeric_detailed(
        user_input, expected_value, tolerance, expected_unit, require_unit=require_unit
    )
    return res.is_correct


def grade_attempt(
    question: Question,
    user_answer: str,
    hints_opened: int = 0,
    confidence: str = "sure",
    plan_step_answer: str | None = None,
) -> SubmitAttemptResponse:
    """
    Deterministically grades an attempt on a question without calling AI.
    Separates honest mastery from assisted mastery and identifies mistake tags.
    """
    user_clean = user_answer.strip()
    is_correct = False
    error_tag = None
    explanation = None
    correct_answer_str = ""

    # Plan step check
    plan_step_correct = None
    if question.plan_step and plan_step_answer:
        plan_step_correct = (
            plan_step_answer.strip().lower()
            == question.plan_step.answer.strip().lower()
        )

    if question.answer.type == "single_choice":
        options = question.answer.options or []
        # Find correct option
        correct_opt = next((o for o in options if o.correct), None)
        if correct_opt:
            correct_answer_str = f"{correct_opt.id}: {correct_opt.text}"

        # Match user choice either by ID ('o1', 'a', etc.) or text
        matched_opt = None
        for o in options:
            if (
                user_clean.lower() == o.id.lower()
                or user_clean.lower() == o.text.strip().lower()
            ):
                matched_opt = o
                break

        if matched_opt:
            is_correct = matched_opt.correct
            error_tag = matched_opt.error_tag
            explanation = matched_opt.explanation
        else:
            is_correct = False
            explanation = "ตัวเลือกที่เลือกไม่ตรงกับตัวเลือกใด"

    elif question.answer.type == "numeric":
        expected = question.answer.correct_value
        tol = question.answer.tolerance if question.answer.tolerance is not None else 0.01
        exp_unit = question.answer.unit
        req_unit = getattr(question.answer, "require_unit", False)
        is_correct, unit_err = grade_numeric_detailed(
            user_clean, expected, tol, expected_unit=exp_unit, require_unit=req_unit
        )
        if not is_correct and unit_err:
            error_tag = unit_err

        correct_answer_str = f"{expected} {question.answer.unit or ''}".strip()
        explanation = (
            question.solution.summary
            if question.solution
            else f"คำตอบที่ถูกต้องคือ {correct_answer_str}"
        )

    # Determine status
    if is_correct:
        if hints_opened > 0:
            status = "correct_assisted"
            next_interval = 1  # review soon because help was used
        else:
            status = "correct_first_try"
            next_interval = 3 if confidence == "sure" else 1
    else:
        status = "wrong"
        next_interval = 1

    error_desc = ERROR_TAG_DESCRIPTIONS.get(error_tag, "") if error_tag else None

    return SubmitAttemptResponse(
        is_correct=is_correct,
        status=status,
        error_tag=error_tag,
        error_tag_description=error_desc,
        explanation=explanation,
        correct_answer=correct_answer_str,
        plan_step_correct=plan_step_correct,
        next_review_interval_days=next_interval,
    )
