import pytest
from fastapi.testclient import TestClient

from app.database import init_db
from app.main import app


@pytest.fixture(autouse=True)
def setup_app():
    init_db()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_dashboard_route(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "TCAS Mastery" in res.text


def test_practice_list_route(client):
    res = client.get("/practice")
    assert res.status_code == 200
    assert "phy-kin-0001" in res.text


def test_practice_detail_route(client):
    res = client.get("/practice/phy-kin-0001")
    assert res.status_code == 200
    assert "72" in res.text


def test_api_submit_attempt(client):
    payload = {
        "question_id": "phy-kin-0001",
        "user_answer": "o1",
        "confidence": "sure",
        "hints_opened": 0,
        "plan_step_answer": "b",
        "time_spent_sec": 35.0,
        "review_time_sec": 0.0,
    }
    res = client.post("/api/submit-attempt", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["is_correct"] is True
    assert data["status"] == "correct_first_try"
    assert "ai_prompt" in data


def test_drills_route(client):
    res = client.get("/drills")
    assert res.status_code == 200


def test_api_new_drill(client):
    res = client.get("/api/drills/new?drill_type=unit_kmh_ms")
    assert res.status_code == 200
    data = res.json()
    assert data["drill_type"] == "unit_kmh_ms"


def test_api_submit_drill(client):
    payload = {
        "drill_type": "unit_kmh_ms",
        "question_stem": "72 km/h",
        "user_answer": "20",
        "expected_answer": "20",
        "time_spent_sec": 5.0,
    }
    res = client.post("/api/drills/submit", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["is_correct"] is True


def test_formulas_route(client):
    res = client.get("/formulas")
    assert res.status_code == 200


def test_api_submit_formula(client):
    payload = {"formula_id": "form-kin-01", "question_index": 0, "user_answer": "b"}
    res = client.post("/api/formulas/submit", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["is_correct"] is True


def test_answer_sheet_routes(client):
    res = client.get("/answer-sheet")
    assert res.status_code == 200

    res_detail = client.get("/answer-sheet/alevel-phy-2566-mock")
    assert res_detail.status_code == 200

    # Submit sample
    payload = {
        "paper_id": "alevel-phy-2566-mock",
        "answers": {"1": "2", "2": "4", "3": "1"},
        "time_taken_min": 15.0,
    }
    res_sub = client.post("/api/answer-sheet/submit", json=payload)
    assert res_sub.status_code == 200
    data = res_sub.json()
    assert data["correct_count"] >= 3
    assert data["score_percent"] > 0


def test_stats_and_system_routes(client):
    res_stats = client.get("/stats")
    assert res_stats.status_code == 200

    res_sys = client.get("/system")
    assert res_sys.status_code == 200

    res_bk = client.post("/api/backup/create")
    assert res_bk.status_code == 200
    assert res_bk.json()["success"] is True
