import subprocess
import time
import signal
import requests
from pathlib import Path

from src.config import (
    SEMAPHORE_BIN,
    CONFIG_PATH,
    DEFAULT_PORT,
    write_config,
)
from src.database import reset_database


class SemaphoreServer:
    def __init__(self, port: int = DEFAULT_PORT, config_path: Path | None = None):
        self.port = port
        self.config_path = config_path or CONFIG_PATH
        self.process: subprocess.Popen | None = None

    @property
    def base_url(self) -> str:
        return f"http://localhost:{self.port}"

    def start(self, timeout: float = 15.0) -> None:
        if self.is_running():
            return

        if not self.config_path.exists():
            write_config(port=self.port)

        self.process = subprocess.Popen(
            [str(SEMAPHORE_BIN), "server", "--config", str(self.config_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                resp = requests.get(f"{self.base_url}/api/ping", timeout=1)
                if resp.status_code == 200:
                    return
            except requests.ConnectionError:
                pass
            time.sleep(0.3)

        self.stop()
        raise RuntimeError(f"Semaphore did not start within {timeout}s")

    def stop(self) -> None:
        if self.process is None:
            return
        self.process.send_signal(signal.SIGTERM)
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait()
        self.process = None

    def restart_clean(self) -> None:
        self.stop()
        reset_database(self.config_path)
        self.start()

    def is_running(self) -> bool:
        if self.process is None:
            return False
        return self.process.poll() is None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *exc):
        self.stop()
