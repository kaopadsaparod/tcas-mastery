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


def verify_backup_file(backup_path: Path | str) -> dict[str, Any]:
    """
    Connects to an existing backup file directly to verify its integrity,
    checking PRAGMA integrity_check, PRAGMA foreign_key_check, and verifying essential tables.
    """
    p = Path(backup_path).resolve()
    if not p.is_file():
        return {"valid": False, "error": f"Backup file does not exist: {p.name}"}

    conn = sqlite3.connect(str(p), timeout=5.0)
    try:
        cur = conn.cursor()
        cur.execute("PRAGMA integrity_check;")
        res = cur.fetchall()
        integrity_ok = len(res) == 1 and res[0][0] == "ok"

        cur.execute("PRAGMA foreign_key_check;")
        fk_violations = cur.fetchall()
        fk_ok = len(fk_violations) == 0

        # Verify key tables exist
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = {row[0] for row in cur.fetchall()}
        required_tables = {"attempts", "review_queue", "topic_priorities"}
        missing_tables = required_tables - tables

        valid = integrity_ok and fk_ok and (len(missing_tables) == 0)
        return {
            "valid": valid,
            "integrity_ok": integrity_ok,
            "fk_ok": fk_ok,
            "missing_tables": list(missing_tables),
            "tables_found": list(tables),
            "message": "Backup integrity verified successfully" if valid else "Corrupt or incomplete backup",
        }
    except Exception as e:
        return {"valid": False, "error": str(e)}
    finally:
        conn.close()


def restore_backup(filename: str) -> dict[str, Any]:
    """
    Restores the live database from a verified backup file using the SQLite backup API.
    Pre-validates the backup file to guarantee zero corruption before swapping.
    """
    if not filename or not BACKUP_FILENAME_REGEX.match(filename):
        return {"success": False, "error": "Invalid backup filename format"}

    backup_path = (BACKUPS_DIR / filename).resolve()
    if backup_path.parent != BACKUPS_DIR.resolve() or not backup_path.is_file():
        return {"success": False, "error": "Backup file not found in authorized directory"}

    # 1. Pre-validation of backup file
    verification = verify_backup_file(backup_path)
    if not verification.get("valid"):
        return {
            "success": False,
            "error": f"Cannot restore invalid backup: {verification.get('error') or verification.get('message')}",
        }

    # 2. SQLite Online Backup API to safely restore into active database
    src_conn = sqlite3.connect(str(backup_path), timeout=10.0)
    dest_conn = sqlite3.connect(str(DB_PATH), timeout=15.0)
    try:
        src_conn.backup(dest_conn)
        # Verify restored DB integrity
        dest_cur = dest_conn.cursor()
        dest_cur.execute("PRAGMA integrity_check;")
        chk = dest_cur.fetchall()
        if not (len(chk) == 1 and chk[0][0] == "ok"):
            return {"success": False, "error": "Restored database failed integrity check"}

        return {"success": True, "message": f"Successfully restored database from {filename}"}
    except Exception as e:
        return {"success": False, "error": f"Restore failed: {str(e)}"}
    finally:
        src_conn.close()
        dest_conn.close()
