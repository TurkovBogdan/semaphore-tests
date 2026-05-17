import subprocess
from pathlib import Path

from src.config import (
    SEMAPHORE_BIN,
    CONFIG_PATH,
    DATA_DIR,
    DB_PATH,
    TMP_PATH,
    DEFAULT_ADMIN_USER,
    DEFAULT_ADMIN_PASS,
    DEFAULT_ADMIN_EMAIL,
    write_config,
)


def reset_database(config_path: Path | None = None) -> None:
    config_path = config_path or CONFIG_PATH

    if DB_PATH.exists():
        DB_PATH.unlink()

    if not config_path.exists():
        write_config()

    _run_migrate(config_path)
    _create_admin_user(config_path)


def _run_migrate(config_path: Path) -> None:
    subprocess.run(
        [str(SEMAPHORE_BIN), "migrate", "--config", str(config_path)],
        check=True,
        capture_output=True,
        text=True,
    )


def _create_admin_user(
    config_path: Path,
    login: str = DEFAULT_ADMIN_USER,
    password: str = DEFAULT_ADMIN_PASS,
    email: str = DEFAULT_ADMIN_EMAIL,
    name: str = "Test Admin",
) -> None:
    subprocess.run(
        [
            str(SEMAPHORE_BIN), "user", "add",
            "--config", str(config_path),
            "--login", login,
            "--name", name,
            "--email", email,
            "--password", password,
            "--admin",
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def clean_data() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
    if TMP_PATH.exists():
        import shutil
        shutil.rmtree(TMP_PATH, ignore_errors=True)
    TMP_PATH.mkdir(parents=True, exist_ok=True)
