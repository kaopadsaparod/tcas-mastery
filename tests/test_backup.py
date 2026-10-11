import pytest

from app.database import init_db
from app.services.backup_service import check_db_integrity, create_backup, list_backups


@pytest.fixture(autouse=True)
def setup_db():
    init_db()


def test_db_integrity():
    check = check_db_integrity()
    assert check["integrity_ok"] is True
    assert check["foreign_keys_ok"] is True


def test_create_and_list_backup():
    backup_file = create_backup()
    assert backup_file.exists()
    assert backup_file.suffix == ".db"
    assert backup_file.stat().st_size > 0

    backups = list_backups()
    assert len(backups) >= 1
    assert any(b["filename"] == backup_file.name for b in backups)
