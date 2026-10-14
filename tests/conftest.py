import pytest
from app.services import pdf_importer
from app.services.content_loader import content_loader


@pytest.fixture(autouse=True)
def isolate_imported_content(tmp_path, monkeypatch):
    """
    Prevents pytest runs from modifying content/imported/custom_questions.yaml.
    Redirects IMPORTED_CONTENT_DIR to a temporary directory for each test run.
    """
    temp_import_dir = tmp_path / "imported"
    temp_import_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(pdf_importer, "IMPORTED_CONTENT_DIR", temp_import_dir)
    yield
    # Reload content loader after test to restore clean state
    content_loader.reload()
