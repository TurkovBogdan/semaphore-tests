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


def _remove_db_files() -> None:
    """Delete the SQLite database and its WAL/SHM sidecars.

    Removing only ``database.sqlite`` while leaving a stale ``-wal`` behind lets the
    next migrate replay old committed transactions (resurrecting data / corrupting the
    file). Always wipe all three so a reset yields a truly clean database.
    """
    for suffix in ("", "-wal", "-shm", "-journal"):
        path = DB_PATH.with_name(DB_PATH.name + suffix)
        if path.exists():
            path.unlink()


def reset_database(config_path: Path | None = None) -> None:
    config_path = config_path or CONFIG_PATH

    _remove_db_files()

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
    _remove_db_files()
    if TMP_PATH.exists():
        import shutil
        shutil.rmtree(TMP_PATH, ignore_errors=True)
    TMP_PATH.mkdir(parents=True, exist_ok=True)
