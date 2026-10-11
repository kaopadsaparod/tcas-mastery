import random
from typing import Any


def generate_kmh_to_ms() -> dict[str, Any]:
    """Generates a speed unit conversion drill with mental-math friendly numbers."""
    direction = random.choice(["kmh_to_ms", "ms_to_kmh"])
    multipliers = [1, 2, 3, 4, 5, 6, 7, 8]
    k = random.choice(multipliers)

    if direction == "kmh_to_ms":
        kmh = k * 18
        ms = k * 5
        return {
            "drill_type": "unit_kmh_ms",
            "stem": f"แปลงความเร็ว ${kmh}\\text{{ km/h}}$ ให้อยู่ในหน่วยเมตรต่อวินาที ($\\text{{m/s}}$)",
            "expected_answer": str(ms),
            "unit": "m/s",
            "explanation": f"วิธีคิดลัด: คูณด้วย 5/18 จะได้ ${kmh} \\times \\frac{{5}}{{18}} = {k} \\times 5 = {ms}\\text{{ m/s}}$",
            "hint": "นำตัวเลขในหน่วย km/h มาคูณด้วยเศษส่วน 5/18",
        }
    else:
        ms = k * 5
        kmh = k * 18
        return {
            "drill_type": "unit_kmh_ms",
            "stem": f"แปลงความเร็ว ${ms}\\text{{ m/s}}$ ให้อยู่ในหน่วยกิโลเมตรต่อชั่วโมง ($\\text{{km/h}}$)",
            "expected_answer": str(kmh),
            "unit": "km/h",
            "explanation": f"วิธีคิดลัด: คูณด้วย 18/5 จะได้ ${ms} \\times \\frac{{18}}{{5}} = {k} \\times 18 = {kmh}\\text{{ km/h}}$",
            "hint": "นำตัวเลขในหน่วย m/s มาคูณด้วยเศษส่วน 18/5",
        }


def generate_area_volume() -> dict[str, Any]:
    """Generates area or volume unit conversions."""
    sub_type = random.choice(["cm2_to_m2", "density_g_to_kg", "liters_to_m3"])

    if sub_type == "cm2_to_m2":
        cm2 = random.choice([200, 500, 1000, 2500, 5000])
        # 1 cm^2 = 10^-4 m^2
        m2 = cm2 * 1e-4
        return {
            "drill_type": "area_volume",
            "stem": f"พื้นที่ขนาด ${cm2}\\text{{ cm}}^2$ คิดเป็นกี่ตารางเมตร ($\\text{{m}}^2$)? (ตอบเป็นทศนิยมหรือสัญกรณ์วิทยาศาสตร์)",
            "expected_answer": str(m2),
            "unit": "m²",
            "explanation": f"จาก $1\\text{{ cm}} = 10^{{-2}}\\text{{ m}}$ ดังนั้น $1\\text{{ cm}}^2 = (10^{{-2}})^2 = 10^{{-4}}\\text{{ m}}^2$ จะได้ ${cm2} \\times 10^{{-4}} = {m2}\\text{{ m}}^2$",
            "hint": "คูณด้วย 10⁻⁴ (เนื่องจาก 1 cm = 10⁻² m แล้วยกกำลังสอง)",
        }
    elif sub_type == "density_g_to_kg":
        val = random.choice([1.0, 1.2, 2.5, 0.8, 13.6])
        ans = val * 1000
        return {
            "drill_type": "area_volume",
            "stem": f"สารมีความหนาแน่น ${val}\\text{{ g/cm}}^3$ คิดเป็นกี่กิโลกรัมต่อลูกบาศก์เมตร ($\\text{{kg/m}}^3$)?",
            "expected_answer": str(int(ans) if ans.is_integer() else ans),
            "unit": "kg/m³",
            "explanation": f"แปลงหน่วย: $1\\text{{ g/cm}}^3 = \\frac{{10^{{-3}}\\text{{ kg}}}}{{10^{{-6}}\\text{{ m}}^3}} = 10^3\\text{{ kg/m}}^3$ ดังนั้น ${val} \\times 1000 = {ans}\\text{{ kg/m}}^3$",
            "hint": "คูณด้วย 1,000 เสมอเมื่อแปลง g/cm³ เป็น kg/m³",
        }
    else:
        liters = random.choice([50, 100, 200, 500, 1500])
        m3 = liters / 1000
        return {
            "drill_type": "area_volume",
            "stem": f"น้ำปริมาตร ${liters}$ ลิตร คิดเป็นกี่ลูกบาศก์เมตร ($\\text{{m}}^3$)?",
            "expected_answer": str(m3),
            "unit": "m³",
            "explanation": f"จาก $1\\text{{ m}}^3 = 1,000$ ลิตร ดังนั้น ${liters} / 1000 = {m3}\\text{{ m}}^3$",
            "hint": "1 ลูกบาศก์เมตร เท่ากับ 1,000 ลิตร",
        }


def generate_kinematics_5eq() -> dict[str, Any]:
    """Generates procedural 1D kinematics drills with guaranteed neat integer answers."""
    pattern = random.choice(
        ["rest_accel_s", "braking_stop_s", "free_fall_peak_time", "rest_accel_v"]
    )

    if pattern == "rest_accel_s":
        a = random.choice([2, 4, 6])
        t = random.choice([3, 4, 5])
        # s = 0.5 * a * t^2
        s = int(0.5 * a * (t**2))
        return {
            "drill_type": "kinematics_5eq",
            "stem": f"วัตถุเริ่มเคลื่อนที่จากหยุดนิ่ง ($u=0$) ด้วยความเร่งคงตัว $a = {a}\\text{{ m/s}}^2$ เมื่อเวลาผ่านไป $t = {t}\\text{{ s}}$ วัตถุจะเคลื่อนที่ได้ระยะทางกี่เมตร?",
            "expected_answer": str(s),
            "unit": "m",
            "explanation": f"ใช้สูตร $s = ut + \\frac{{1}}{{2}}at^2$ แทนค่า $s = 0 + \\frac{{1}}{{2}}({a})({t}^2) = {s}\\text{{ m}}$",
            "hint": "เริ่มจากหยุดนิ่ง u = 0 พจน์แรกจึงเป็นศูนย์",
        }
    elif pattern == "braking_stop_s":
        u = random.choice([10, 20, 30])
        a = random.choice([2, 5])
        # v^2 = u^2 + 2as => 0 = u^2 - 2as => s = u^2 / (2a)
        s = int((u**2) / (2 * a))
        return {
            "drill_type": "kinematics_5eq",
            "stem": f"รถยนต์แล่นด้วยความเร็ว $u = {u}\\text{{ m/s}}$ แล้วแตะเบรกด้วยความหน่วง $a = -{a}\\text{{ m/s}}^2$ จนหยุดนิ่ง จงหาระยะเบรก (ระยะทางจนหยุด)",
            "expected_answer": str(s),
            "unit": "m",
            "explanation": f"ใช้สูตร $v^2 = u^2 + 2as$ เมื่อ $v=0 \\implies 0 = {u}^2 + 2(-{a})s \\implies {2 * a}s = {u**2} \\implies s = {s}\\text{{ m}}$",
            "hint": "ใช้สูตรที่ไม่มีตัวแปรเวลา t: v² = u² + 2as",
        }
    elif pattern == "free_fall_peak_time":
        u = random.choice([10, 20, 30, 40, 50])
        t = u // 10
        return {
            "drill_type": "kinematics_5eq",
            "stem": f"โยนก้อนหินขึ้นตรงๆ ในแนวดิ่งด้วยความเร็วต้น $u = {u}\\text{{ m/s}}$ ก้อนหินจะใช้เวลากี่วินาทีในการขึ้นถึงจุดสูงสุด? (กำหนด $g = 10\\text{{ m/s}}^2$)",
            "expected_answer": str(t),
            "unit": "s",
            "explanation": f"ที่จุดสูงสุด $v = 0$ จาก $v = u - gt \\implies 0 = {u} - 10t \\implies t = {t}\\text{{ s}}$",
            "hint": "จุดสูงสุดความเร็วปลาย v = 0",
        }
    else:  # rest_accel_v
        a = random.choice([3, 5, 8])
        t = random.choice([4, 6, 8])
        v = a * t
        return {
            "drill_type": "kinematics_5eq",
            "stem": f"วัตถุออกตัวจากหยุดนิ่งด้วยความเร่ง $a = {a}\\text{{ m/s}}^2$ เมื่อเวลาผ่านไป $t = {t}\\text{{ s}}$ จะมีความเร็วกี่ m/s?",
            "expected_answer": str(v),
            "unit": "m/s",
            "explanation": f"ใช้สูตร $v = u + at = 0 + ({a})({t}) = {v}\\text{{ m/s}}$",
            "hint": "v = u + at",
        }


def generate_fractions_powers() -> dict[str, Any]:
    """Generates physics scaling, proportion and ratio drills."""
    problem_type = random.choice(
        ["kinetic_energy_ratio", "wire_resistance_ratio", "gravitational_ratio"]
    )

    if problem_type == "kinetic_energy_ratio":
        m_factor = random.choice([2, 3])
        v_factor = random.choice([2, 3])
        ans = m_factor * (v_factor**2)
        return {
            "drill_type": "fractions_powers",
            "stem": f"หากวัตถุหนึ่งมีมวลเพิ่มเป็น {m_factor} เท่า และมีอัตราเร็วเพิ่มเป็น {v_factor} เท่า พลังงานจลน์ ($E_k = \\frac{{1}}{{2}}mv^2$) จะเพิ่มขึ้นเป็นกี่เท่าของเดิม?",
            "expected_answer": str(ans),
            "unit": "เท่า",
            "explanation": f"จาก $E_k \\propto m v^2$ จะได้สัดส่วน $\\frac{{E_{{k2}}}}{{E_{{k1}}}} = ({m_factor}) \\times ({v_factor})^2 = {m_factor} \\times {v_factor**2} = {ans}$ เท่า",
            "hint": "ระวังตัวแปร v มีกำลังสอง ทำให้ต้องนำตัวคูณของ v มายกกำลังสองก่อนคูณกับมวล",
        }
    elif problem_type == "wire_resistance_ratio":
        r_factor = random.choice([2, 3])
        # R = rho * L / A = rho * L / (pi * r^2) => R proportional to 1 / r^2
        # If r increases by r_factor, R becomes 1 / (r_factor^2)
        denom = r_factor**2
        return {
            "drill_type": "fractions_powers",
            "stem": f"ลวดตัวนำทรงกระบอกยาวเท่าเดิม หากรัศมีหน้าตัดเพิ่มเป็น {r_factor} เท่า ความต้านทานไฟฟ้าจะเปลี่ยนเป็นเศษส่วนเท่าใดของเดิม? (ตอบในรูปเศษส่วน เช่น 1/4 หรือ 1/9)",
            "expected_answer": f"1/{denom}",
            "unit": "เท่า",
            "explanation": f"จาก $R = \\rho \\frac{{L}}{{A}}$ โดย $A = \\pi r^2 \\implies R \\propto \\frac{{1}}{{r^2}}$ เมื่อรัศมีเป็น {r_factor} เท่า พื้นที่ $A$ จะเป็น ${r_factor}^2 = {denom}$ เท่า ดังนั้น $R$ จะลดลงเหลือ $1/{denom}$ เท่า",
            "hint": "พื้นที่หน้าตัดเป็นสัดส่วนกับรัศมียกกำลังสอง (A ∝ r²)",
        }
    else:
        dist_factor = random.choice([2, 3])
        ans_denom = dist_factor**2
        return {
            "drill_type": "fractions_powers",
            "stem": f"หากระยะห่างระหว่างมวลสองก้อนเพิ่มขึ้นเป็น {dist_factor} เท่า แรงดึงดูดระหว่างมวล ($F = G\\frac{{m_1 m_2}}{{R^2}}$) จะลดลงเหลือเศษส่วนเท่าใดของเดิม? (ตอบในรูปเศษส่วน เช่น 1/4 หรือ 1/9)",
            "expected_answer": f"1/{ans_denom}",
            "unit": "เท่า",
            "explanation": f"จาก $F \\propto \\frac{{1}}{{R^2}}$ เมื่อระยะห่างเป็น {dist_factor} เท่า แรงจะลดลงเป็น $\\frac{{1}}{{{dist_factor}^2}} = 1/{ans_denom}$ เท่า",
            "hint": "กฎแรงโน้มถ่วงแปรผกผันกับระยะทางยกกำลังสอง",
        }


def generate_random_drill(drill_type: str | None = None) -> dict[str, Any]:
    """Generates a procedural drill for the specified type or a random one."""
    generators = {
        "unit_kmh_ms": generate_kmh_to_ms,
        "area_volume": generate_area_volume,
        "kinematics_5eq": generate_kinematics_5eq,
        "fractions_powers": generate_fractions_powers,
    }
    if drill_type in generators:
        return generators[drill_type]()
    chosen = random.choice(list(generators.values()))
    return chosen()
