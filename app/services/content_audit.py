from typing import Any

from app.services.content_loader import content_loader


def get_content_audit_report() -> dict[str, Any]:
    """
    Performs a comprehensive academic and structural audit of all questions
    in the question bank and past paper blueprints.
    Identifies verification status, source tracking, blueprint readiness, and schema integrity.
    """
    all_questions = content_loader.get_all_questions()
    past_papers = content_loader.get_all_past_papers()

    total_bank = len(all_questions)
    verified_count = 0
    reviewed_count = 0
    draft_count = 0
    official_source_count = 0
    warnings: list[dict[str, Any]] = []

    topic_stats: dict[str, dict[str, Any]] = {}

    for q in all_questions:
        # Status
        status = getattr(q.verification, "status", "draft")
        if status == "verified":
            verified_count += 1
        elif status == "reviewed":
            reviewed_count += 1
        else:
            draft_count += 1

        # Source
        src_type = getattr(q.source, "type", "invented")
        if src_type == "official":
            official_source_count += 1

        # Topic aggregation
        top = q.topic
        if top not in topic_stats:
            topic_stats[top] = {
                "topic": top,
                "subject": q.subject,
                "total": 0,
                "verified": 0,
                "reviewed": 0,
                "draft": 0,
                "mock_ready": 0,
                "single_choice_count": 0,
                "numeric_count": 0,
            }
        topic_stats[top]["total"] += 1
        if status == "verified":
            topic_stats[top]["verified"] += 1
            topic_stats[top]["mock_ready"] += 1
        elif status == "reviewed":
            topic_stats[top]["reviewed"] += 1
            topic_stats[top]["mock_ready"] += 1
        else:
            topic_stats[top]["draft"] += 1

        if q.answer.type == "single_choice":
            topic_stats[top]["single_choice_count"] += 1
        else:
            topic_stats[top]["numeric_count"] += 1

        # Integrity checks
        if q.answer.type == "single_choice":
            correct_opts = [o for o in (q.answer.options or []) if o.correct]
            if len(correct_opts) != 1:
                warnings.append({
                    "question_id": q.id,
                    "topic": q.topic,
                    "severity": "high",
                    "issue": f"ข้อสอบปรนัยต้องมีคำตอบที่ถูก 1 ตัวเลือกพอดี (พบ {len(correct_opts)} ตัวเลือก)",
                })
            # Check error tags on wrong options
            wrong_opts_without_tag = [o for o in (q.answer.options or []) if not o.correct and not o.error_tag]
            if len(wrong_opts_without_tag) > 2:
                warnings.append({
                    "question_id": q.id,
                    "topic": q.topic,
                    "severity": "low",
                    "issue": f"ตัวเลือกที่ผิด {len(wrong_opts_without_tag)} ตัวเลือกยังไม่ได้ระบุ error_tag สำหรับวิเคราะห์จุดอ่อน",
                })
        else:
            if q.answer.correct_value is None:
                warnings.append({
                    "question_id": q.id,
                    "topic": q.topic,
                    "severity": "high",
                    "issue": "ข้อสอบอัตนัยไม่ได้ระบุ correct_value",
                })
            if q.answer.require_unit and not q.answer.unit:
                warnings.append({
                    "question_id": q.id,
                    "topic": q.topic,
                    "severity": "medium",
                    "issue": "กำหนด require_unit=True แต่ไม่ได้ระบุ expected unit",
                })

        # Missing explanation check
        if not q.solution and not any(o.explanation for o in (q.answer.options or [])):
            warnings.append({
                "question_id": q.id,
                "topic": q.topic,
                "severity": "medium",
                "issue": "ไม่มีคำอธิบายเฉลยหรือวิธีทำ (solution)",
            })

    # Past papers audit
    papers_summary = []
    total_paper_questions = 0
    for p in past_papers:
        q_count = len(p.questions)
        total_paper_questions += q_count
        single_cnt = sum(1 for q in p.questions if (q.answer_type or "single_choice") == "single_choice")
        num_cnt = sum(1 for q in p.questions if q.answer_type == "numeric")
        total_pts = sum(q.score for q in p.questions)

        is_blueprint_valid = False
        if "blueprint-30" in p.id and q_count == 30 and round(total_pts, 1) == 100.0:
            is_blueprint_valid = True
        elif "blueprint-70" in p.id and q_count == 70:
            is_blueprint_valid = True
        elif "mock" in p.id or "practice" in p.id:
            is_blueprint_valid = True

        papers_summary.append({
            "id": p.id,
            "title": p.title,
            "subject": p.subject,
            "year": p.year,
            "time_limit_min": p.time_limit_min,
            "question_count": q_count,
            "single_choice_count": single_cnt,
            "numeric_count": num_cnt,
            "max_score": round(total_pts, 1),
            "is_blueprint_valid": is_blueprint_valid,
        })

    # Topic readiness list
    topics_list = []
    for top_id, data in sorted(topic_stats.items()):
        # Ready for exam if at least 2 verified/reviewed questions
        data["is_exam_ready"] = data["mock_ready"] >= 2
        data["readiness_pct"] = round((data["mock_ready"] / data["total"] * 100), 1) if data["total"] > 0 else 0.0
        topics_list.append(data)

    mock_ready_total = verified_count + reviewed_count
    readiness_pct = round((mock_ready_total / total_bank * 100), 1) if total_bank > 0 else 0.0

    return {
        "summary": {
            "total_bank_questions": total_bank,
            "verified_count": verified_count,
            "reviewed_count": reviewed_count,
            "draft_count": draft_count,
            "mock_ready_count": mock_ready_total,
            "readiness_pct": readiness_pct,
            "official_source_count": official_source_count,
            "past_papers_count": len(past_papers),
            "total_paper_questions": total_paper_questions,
            "warnings_count": len(warnings),
        },
        "topics": topics_list,
        "past_papers": papers_summary,
        "warnings": warnings,
    }
