import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


if load_dotenv:
    load_dotenv()


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "data.db"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))

SERVERCHAN_KEY = os.getenv("SERVERCHAN_KEY", "")
ENABLE_NOTIFY = os.getenv("ENABLE_NOTIFY", "false").lower() in {"1", "true", "yes", "on"}

RUN_INTERVAL_HOURS = int(os.getenv("RUN_INTERVAL_HOURS", "6"))
