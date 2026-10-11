import logging
import os
from pathlib import Path

logger = logging.getLogger("tcas")

BASE_DIR = Path(__file__).resolve().parent.parent

# Support moving data outside OneDrive / synced directories via TCAS_DATA_DIR env
env_data_dir = os.getenv("TCAS_DATA_DIR")
if env_data_dir:
    DATA_DIR = Path(env_data_dir).resolve()
else:
    DATA_DIR = BASE_DIR / "data"

DB_PATH = DATA_DIR / "tcas.db"
BACKUPS_DIR = DATA_DIR / "backups"
SOURCES_DIR = DATA_DIR / "sources"
ASSETS_DIR = DATA_DIR / "assets"
CONTENT_DIR = BASE_DIR / "content"

# Detect if DATA_DIR resides within OneDrive to alert user of WAL lock contention
IS_ONEDRIVE_PATH = "onedrive" in str(DATA_DIR).lower()
if IS_ONEDRIVE_PATH:
    logger.warning(
        "WARNING: Data directory '%s' appears to be inside a OneDrive synced folder. "
        "OneDrive sync can disrupt SQLite WAL files (tcas.db-wal / -shm). "
        "Set TCAS_DATA_DIR to an unsynced path (e.g. %%LOCALAPPDATA%%\\tcas_data) to avoid disk I/O errors.",
        DATA_DIR,
    )

# Ensure runtime directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
SOURCES_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
CONTENT_DIR.mkdir(parents=True, exist_ok=True)

APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
APP_PORT = int(os.getenv("APP_PORT", "8000"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TCAS_ACCESS_PIN = os.getenv("TCAS_ACCESS_PIN", "").strip()

# Allowed host names for Trusted Host / DNS rebinding protection
ALLOWED_HOSTS_CONF = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,testserver").strip()
ALLOWED_HOSTS = [h.strip() for h in ALLOWED_HOSTS_CONF.split(",") if h.strip()]
