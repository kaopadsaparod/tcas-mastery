import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from app.config import BACKUPS_DIR, DB_PATH
from app.database import get_db

BACKUP_FILENAME_REGEX = re.compile(r"^tcas_backup_\d{8}_\d{6}_\d+\.db$")


def create_backup() -> Path:
    """
    Executes SQLite VACUUM INTO on an isolated autocommit connection
    with parameter binding to create a consistent live backup.
    Guaranteed to run outside any open transaction.
    """
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    backup_file = BACKUPS_DIR / f"tcas_backup_{timestamp}.db"
    backup_file.unlink(missing_ok=True)

    # Dedicated connection with isolation_level=None to guarantee autocommit mode
    conn = sqlite3.connect(str(DB_PATH), timeout=15.0, isolation_level=None)
    try:
        conn.execute("VACUUM INTO ?", (str(backup_file),))
    finally:
        conn.close()

    return backup_file


def list_backups() -> list[dict[str, Any]]:
    """Lists all available backup files sorted by creation time."""
    if not BACKUPS_DIR.exists():
        return []

    backups = []
    for f in sorted(
        BACKUPS_DIR.glob("*.db"), key=lambda p: p.stat().st_mtime, reverse=True
    ):
        if not BACKUP_FILENAME_REGEX.match(f.name):
            continue
        stat = f.stat()
        backups.append(
            {
                "filename": f.name,
                "path": str(f),
                "size_kb": round(stat.st_size / 1024, 2),
                "created_at": datetime.fromtimestamp(stat.st_mtime).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            }
        )
    return backups


def check_db_integrity() -> dict[str, Any]:
    """Runs SQLite PRAGMA integrity_check and foreign_key_check."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check;")
        integrity = cursor.fetchall()
        integrity_ok = len(integrity) == 1 and integrity[0][0] == "ok"

        cursor.execute("PRAGMA foreign_key_check;")
        fk_violations = cursor.fetchall()
        fk_ok = len(fk_violations) == 0

    return {
        "integrity_ok": integrity_ok,
        "foreign_keys_ok": fk_ok,
        "integrity_message": integrity[0][0] if integrity else "unknown",
        "fk_violations_count": len(fk_violations),
    }


def delete_backup(filename: str) -> bool:
    """
    Safely deletes a backup file inside BACKUPS_DIR.
    Enforces regex pattern check, resolved parent path containment check,
    and ensures file existence before deletion.
    """
    if not filename or not BACKUP_FILENAME_REGEX.match(filename):
        return False

    target = (BACKUPS_DIR / filename).resolve()
    if target.parent != BACKUPS_DIR.resolve():
        return False

    if target.is_file() and target.suffix == ".db":
        target.unlink()
        return True

    return False
