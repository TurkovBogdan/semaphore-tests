import json
import os
import secrets
import base64
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VENDOR_DIR = PROJECT_ROOT / "vendor"
SEMAPHORE_BIN = VENDOR_DIR / "semaphore"
DATA_DIR = PROJECT_ROOT / ".testdata"
DB_PATH = DATA_DIR / "database.sqlite"
CONFIG_PATH = DATA_DIR / "config.json"
TMP_PATH = DATA_DIR / "tmp"
ENV_FILE = PROJECT_ROOT / ".env"


def _load_env() -> None:
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


_load_env()

DEFAULT_PORT = int(os.environ.get("SEMAPHORE_TEST_PORT", "3100"))
DEFAULT_HOST = os.environ.get("SEMAPHORE_TEST_HOST", "localhost")
DEFAULT_ADMIN_USER = os.environ.get("SEMAPHORE_TEST_ADMIN_USER", "admin")
DEFAULT_ADMIN_PASS = os.environ.get("SEMAPHORE_TEST_ADMIN_PASS", "admin123")
DEFAULT_ADMIN_EMAIL = os.environ.get("SEMAPHORE_TEST_ADMIN_EMAIL", "admin@test.local")

DEFAULT_PROJECT_NAME = os.environ.get("SEMAPHORE_TEST_PROJECT_NAME", "TestProject")
DEFAULT_DEMO_PROJECT_NAME = os.environ.get("SEMAPHORE_TEST_DEMO_PROJECT_NAME", "DemoProject")


def _random_key(nbytes: int = 32) -> str:
    return base64.b64encode(secrets.token_bytes(nbytes)).decode()


def generate_config(
    port: int = DEFAULT_PORT,
    db_path: Path | None = None,
    tmp_path: Path | None = None,
) -> dict:
    db_path = db_path or DB_PATH
    tmp_path = tmp_path or TMP_PATH
    return {
        "sqlite": {
            "host": str(db_path),
        },
        "dialect": "sqlite",
        "port": f":{port}",
        "tmp_path": str(tmp_path),
        "cookie_hash": _random_key(),
        "cookie_encryption": _random_key(),
        "access_key_encryption": _random_key(),
        "demo_mode": False,
    }


def write_config(
    port: int = DEFAULT_PORT,
    db_path: Path | None = None,
    tmp_path: Path | None = None,
) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (tmp_path or TMP_PATH).mkdir(parents=True, exist_ok=True)

    cfg = generate_config(port=port, db_path=db_path, tmp_path=tmp_path)
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2))
    return CONFIG_PATH
