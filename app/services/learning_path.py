from typing import Any

from app.services.roadmap_service import get_roadmap_topics

# Directed Acyclic Graph (DAG) of topic prerequisites in TCAS Physics & Math
TOPIC_PREREQUISITES: dict[str, list[str]] = {
    "physics.kinematics.1d": ["physics.vectors"],
    "physics.forces_energy": ["physics.kinematics.1d", "physics.vectors"],
    "physics.work_energy": ["physics.forces_energy"],
    "physics.momentum": ["physics.forces_energy", "physics.kinematics.1d"],
    "physics.circular_shm": ["physics.forces_energy", "physics.kinematics.1d"],
    "physics.waves": ["physics.circular_shm"],
    "physics.electricity": ["physics.forces_energy", "physics.work_energy"],
    "physics.electromagnetism": ["physics.electricity"],
    "physics.modern_physics": ["physics.waves", "physics.work_energy"],
    "math.functions_algebra": ["math.algebra.basics"],
    "math.calculus": ["math.functions_algebra"],
    "tpat3.quantitative": ["math.algebra.basics", "physics.kinematics.1d"],
}

# Skill remediation lookup: when a student misses a specific skill, what fundamental drill is needed?
SKILL_REMEDIATION_MAP: dict[str, dict[str, str]] = {
    "choose_constant_accel_eq": {
        "title": "ฝึกคัดเลือกสมการการเคลื่อนที่ 5 สมการ (Kinematics 5-EQ Drill)",
        "drill_type": "kinematics_5eq",
        "concept": "จำแนกตัวแปร u, v, a, s, t และเลือกสมการที่ไม่มีตัวแปรส่วนเกิน",
    },
    "unit_kmh_to_ms": {
        "title": "ฝึกแปลงหน่วย km/h เป็น m/s ในใจ (Unit Conversion Drill)",
        "drill_type": "kmh_to_ms",
        "concept": "คูณด้วย 5/18 เมื่อแปลง km/h -> m/s และคูณด้วย 18/5 เมื่อแปลง m/s -> km/h",
    },
    "vt_graph_interpretation": {
        "title": "ฝึกวิเคราะห์พื้นที่ใต้กราฟและความชัน v-t (Graph Analysis)",
        "drill_type": "area_volume",
        "concept": "ความชันคือความเร่ง a, พื้นที่ใต้กราฟ v-t คือการกระจัด s (คิดแยกสามเหลี่ยม/สี่เหลี่ยม)",
    },
    "sign_convention": {
        "title": "ทบทวนการกำหนดเครื่องหมายเวกเตอร์ (+ / -)",
        "drill_type": "kinematics_5eq",
        "concept": "กำหนดทิศการเคลื่อนที่ต้นเป็นบวก เวกเตอร์ที่สวนทาง (ความหน่วง, แรงต้าน, g พุ่งลง) ต้องติดลบ",
    },
}


def get_prerequisites_for_topic(topic_id: str) -> list[str]:
    """Returns the list of direct prerequisite topic IDs for a given topic."""
    return TOPIC_PREREQUISITES.get(topic_id, [])


def analyze_topic_readiness(topic_id: str) -> dict[str, Any]:
    """
    Checks if a student is academically prepared to tackle a target topic
    based on their current mastery of its prerequisite topics.
    """
    prereqs = get_prerequisites_for_topic(topic_id)
    if not prereqs:
        return {
            "topic_id": topic_id,
            "has_prerequisites": False,
            "is_ready": True,
            "prerequisites": [],
            "status": "ready",
            "message": "บทเรียนนี้เป็นพื้นฐาน สามารถเริ่มศึกษาได้ทันที",
        }

    roadmap = {t["topic_id"]: t for t in get_roadmap_topics()}
    prereq_details = []
    unready_prereqs = []

    for p_id in prereqs:
        p_stat = roadmap.get(p_id)
        if p_stat:
            mastery = p_stat.get("current_mastery_pct", 0.0)
            unique_q = p_stat.get("unique_questions_attempted", 0)
            is_mastered = mastery >= 60.0 and unique_q >= 2
            p_info = {
                "topic_id": p_id,
                "topic_name": p_stat.get("topic_name", p_id),
                "mastery_pct": mastery,
                "unique_questions": unique_q,
                "is_passed": is_mastered,
            }
        else:
            # Topic not yet initialized in roadmap priorities
            p_info = {
                "topic_id": p_id,
                "topic_name": p_id,
                "mastery_pct": 0.0,
                "unique_questions": 0,
                "is_passed": False,
            }

        prereq_details.append(p_info)
        if not p_info["is_passed"]:
            unready_prereqs.append(p_info)

    is_ready = len(unready_prereqs) == 0
    if is_ready:
        msg = "คุณมีพื้นฐานบทก่อนหน้าครบถ้วน พร้อมเริ่มเรียนบทนี้ได้อย่างมีประสิทธิภาพ"
        status = "ready"
    else:
        unready_names = ", ".join(f"'{p['topic_name']}'" for p in unready_prereqs)
        msg = f"ควรทบทวนพื้นฐานใน {unready_names} ให้ได้คะแนนอย่างน้อย 60% ก่อน เพื่อไม่ให้สะดุดเวลาทำโจทย์ขั้นสูง"
        status = "prerequisites_needed"

    return {
        "topic_id": topic_id,
        "has_prerequisites": True,
        "is_ready": is_ready,
        "prerequisites": prereq_details,
        "unready_prerequisites": unready_prereqs,
        "status": status,
        "message": msg,
    }


def get_skill_remediation(skill_id: str) -> dict[str, str] | None:
    """Returns targeted remediation advice and drill recommendation for a weak skill."""
    return SKILL_REMEDIATION_MAP.get(skill_id)
