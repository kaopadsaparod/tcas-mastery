from app.services.content_loader import content_loader


def test_questions_schema_valid():
    """Verify all questions load and conform to schema."""
    questions = content_loader.get_all_questions()
    assert len(questions) >= 6, "Expected at least 6 core questions"

    for q in questions:
        assert q.id, "Question must have an ID"
        assert q.stem.strip(), f"Question {q.id} stem is empty"
        assert q.subject in ["physics", "math", "tpat3", "tgat1", "tgat2", "tgat3"]
        assert q.verification.tier in ["A", "B", "C", "D", "E"]

        if q.answer.type == "single_choice":
            assert q.answer.options is not None and len(q.answer.options) >= 2
            correct_opts = [opt for opt in q.answer.options if opt.correct]
            assert len(correct_opts) == 1, (
                f"Question {q.id} must have exactly one correct option"
            )
        elif q.answer.type == "numeric":
            assert q.answer.correct_value is not None, (
                f"Question {q.id} must have a correct_value"
            )


def test_formula_cards_schema_valid():
    """Verify all formula cards load and have valid recall questions."""
    formulas = content_loader.get_all_formulas()
    assert len(formulas) >= 4, "Expected at least 4 formula cards"

    for card in formulas:
        assert card.id
        assert card.title
        assert card.latex
        assert len(card.conditions) >= 1
        assert len(card.variables) >= 1
        assert len(card.recall_questions) >= 1


def test_past_papers_schema_valid():
    """Verify past paper data loads cleanly."""
    papers = content_loader.get_all_past_papers()
    assert len(papers) >= 1, "Expected at least 1 past paper"

    for p in papers:
        assert p.id
        assert p.subject in ["physics", "math", "tpat3", "tgat1", "tgat2", "tgat3"]
        assert len(p.questions) >= 10
        assert p.time_limit_min > 0
