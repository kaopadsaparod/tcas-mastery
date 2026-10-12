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


def test_base_template_contains_dark_mode_elements(client):
    """Verify that base template contains theme toggle button, script, and meta."""
    res = client.get("/")
    assert res.status_code == 200
    html = res.text

    # Check for dark mode toggle button
    assert 'id="themeToggleBtn"' in html
    assert 'theme-toggle-btn' in html
    assert 'theme-toggle-icon' in html

    # Check for anti-flicker theme initialization script
    assert 'localStorage.getItem(\'tcas_theme\')' in html
    assert 'data-theme' in html


def test_dark_mode_css_definitions_present(client):
    """Verify that style.css includes [data-theme='dark'] and theme-toggle-btn definitions."""
    res = client.get("/static/css/style.css")
    assert res.status_code == 200
    css = res.text

    # Theme selector
    assert '[data-theme="dark"]' in css
    assert '--bg-page: #0b0f19;' in css
    assert '--bg-card: #111827;' in css
    assert '--text-main: #f8fafc;' in css

    # Component dark styles
    assert '.theme-toggle-btn' in css
    assert '[data-theme="dark"] .navbar' in css
    assert '[data-theme="dark"] .card' in css
    assert '[data-theme="dark"] .option-item' in css
    assert '[data-theme="dark"] .katex' in css


def test_dark_mode_js_logic_present(client):
    """Verify that app.js contains theme toggle logic and event listeners."""
    res = client.get("/static/js/app.js")
    assert res.status_code == 200
    js = res.text

    assert 'initThemeToggle' in js
    assert 'updateThemeButtonUI' in js
    assert 'tcas_theme' in js
    assert 'data-theme' in js


def test_all_major_pages_include_theme_toggle(client):
    """Verify theme toggle button appears across all major views inheriting base.html."""
    endpoints = [
        "/",
        "/practice",
        "/formulas",
        "/mock-exam",
        "/planner",
        "/progress",
        "/roadmap",
        "/drills",
        "/answer-sheet",
        "/stats",
        "/system",
    ]
    for ep in endpoints:
        resp = client.get(ep)
        assert resp.status_code == 200, f"Endpoint {ep} failed with status {resp.status_code}"
        assert 'id="themeToggleBtn"' in resp.text, f"Endpoint {ep} missing themeToggleBtn"
