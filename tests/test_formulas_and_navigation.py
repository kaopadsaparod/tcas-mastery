import pytest
from fastapi.testclient import TestClient

from app.database import init_db
from app.main import app
from app.services.content_loader import content_loader
from app.services.mock_exam import start_mock_exam, submit_mock_exam


@pytest.fixture(autouse=True)
def setup_app():
    init_db()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_math_and_physics_formulas_loading():
    """Verify that both physics and math formulas are properly loaded and partitioned."""
    all_formulas = content_loader.get_all_formulas()
    assert len(all_formulas) >= 15, f"Expected at least 15 formula cards, got {len(all_formulas)}"

    physics_cards = [f for f in all_formulas if f.subject == "physics"]
    math_cards = [f for f in all_formulas if f.subject == "math"]

    assert len(physics_cards) >= 8, f"Expected at least 8 physics cards, got {len(physics_cards)}"
    assert len(math_cards) >= 8, f"Expected at least 8 math cards, got {len(math_cards)}"

    # Check required fields
    for card in all_formulas:
        assert card.id.startswith("form-")
        assert card.title
        assert card.latex
        assert len(card.conditions) >= 1
        assert len(card.variables) >= 1
        assert len(card.selection_cues) >= 1
        assert len(card.recall_questions) >= 1
        for q in card.recall_questions:
            assert "prompt" in q
            assert "options" in q
            assert "answer" in q
            assert q["answer"] in q["options"]


def test_formulas_page_and_subject_filtering(client):
    """Verify /formulas endpoint renders successfully and supports subject filtering."""
    # Default (all)
    res_all = client.get("/formulas")
    assert res_all.status_code == 200
    html_all = res_all.text
    assert "รวมสูตรที่ต้องรู้ (ฟิสิกส์ & คณิตศาสตร์)" in html_all
    assert "กลับหน้าหลัก" in html_all
    assert "ฟิสิกส์" in html_all
    assert "คณิตศาสตร์" in html_all

    # Physics filter
    res_phy = client.get("/formulas?subject=physics")
    assert res_phy.status_code == 200
    html_phy = res_phy.text
    assert "⚡ ฟิสิกส์" in html_phy

    # Math filter
    res_math = client.get("/formulas?subject=math")
    assert res_math.status_code == 200
    html_math = res_math.text
    assert "📐 คณิตศาสตร์" in html_math


def test_formula_recall_submission_math_and_physics(client):
    """Test active recall quiz submission for both physics and math formula cards."""
    # Physics recall
    payload_phy = {
        "formula_id": "form-kin-01",
        "question_index": 0,
        "user_answer": "b",
    }
    res_phy = client.post("/api/formulas/submit", json=payload_phy)
    assert res_phy.status_code == 200
    data_phy = res_phy.json()
    assert data_phy["is_correct"] is True

    # Math recall
    payload_math = {
        "formula_id": "form-mat-quad-01",
        "question_index": 0,
        "user_answer": "b",
    }
    res_math = client.post("/api/formulas/submit", json=payload_math)
    assert res_math.status_code == 200
    data_math = res_math.json()
    assert data_math["is_correct"] is True

    # Wrong answer
    payload_wrong = {
        "formula_id": "form-mat-quad-01",
        "question_index": 0,
        "user_answer": "a",
    }
    res_wrong = client.post("/api/formulas/submit", json=payload_wrong)
    assert res_wrong.status_code == 200
    data_wrong = res_wrong.json()
    assert data_wrong["is_correct"] is False
    assert data_wrong["correct_answer"] == "b"


def test_practice_page_easy_back_navigation(client):
    """Verify that the practice review page includes clear top and post-review back navigation."""
    res = client.get("/practice/phy-kin-0001")
    assert res.status_code == 200
    html = res.text
    # Top navigation
    assert "◀ ย้อนกลับ" in html
    assert "goSmartBack()" in html
    assert "📚 คลังโจทย์" in html
    assert "🏠 หน้าหลัก" in html
    # Post-review actions
    assert "postReviewActionSection" in html
    assert "ทบทวนข้อนี้เสร็จสิ้นแล้ว!" in html
    assert "floatingBackBtn" in html


def test_mock_exam_report_back_navigation_and_review_links(client):
    """Verify mock exam report has top/bottom back navigation and per-question review links."""
    session_data = start_mock_exam("tpat3_practice_25")
    session_id = session_data["session_id"]

    submit_res = submit_mock_exam(
        session_id=session_id,
        answers={"1": "1", "2": "2"},
        time_spent_min=25.0,
    )

    report_res = client.get(f"/mock-exam/{session_id}/report")
    assert report_res.status_code == 200
    html = report_res.text
    # Back navigation
    assert "◀ กลับหน้ารวมข้อสอบจำลอง" in html
    assert "🏠 กลับหน้าหลัก (Dashboard)" in html
    # Review column and link
    assert "ทบทวนเฉลย" in html
    assert "🔍 ทบทวน ➔" in html


def test_answer_sheet_back_navigation(client):
    """Verify answer sheet page provides easy back navigation."""
    res = client.get("/answer-sheet/alevel-phy-2566-mock")
    assert res.status_code == 200
    html = res.text
    assert "◀ กลับหน้ารวมกระดาษคำตอบ" in html
    assert "🏠 หน้าหลัก" in html
