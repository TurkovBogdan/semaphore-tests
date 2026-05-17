import os
import time
import pytest

from src.config import DEFAULT_PORT, write_config, _load_env
from src.database import reset_database
from src.server import SemaphoreServer

_load_env()

_server: SemaphoreServer | None = None


def get_server() -> SemaphoreServer:
    global _server
    if _server is None:
        config = write_config(port=DEFAULT_PORT)
        reset_database(config)
        _server = SemaphoreServer(port=DEFAULT_PORT, config_path=config)
        _server.start()
    return _server


# ─── session fixtures ────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def semaphore_server():
    server = get_server()
    yield server
    server.stop()


@pytest.fixture(scope="session")
def base_url(semaphore_server):
    return semaphore_server.base_url


# ─── test group fixtures ────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def _handle_clean_db(request, semaphore_server):
    if request.node.get_closest_marker("clean_db"):
        semaphore_server.restart_clean()


@pytest.fixture(autouse=True)
def _handle_seeded(request, semaphore_server):
    marker = request.node.get_closest_marker("seeded")
    if marker is None:
        return
    seed_name = marker.kwargs.get("seed") or marker.args[0]
    semaphore_server.restart_clean()

    import importlib
    seed_module = importlib.import_module(f"src.seeds.{seed_name}")
    seed_module.run(semaphore_server.base_url)


@pytest.fixture(autouse=True)
def _handle_clean_browser(request, context):
    if request.node.get_closest_marker("clean_browser"):
        context.clear_cookies()


@pytest.fixture(autouse=True)
def _assert_no_console_errors(page):
    errors: list[str] = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    yield
    assert errors == [], f"Console errors during test: {errors}"


# ─── browser fixtures ───────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def browser_type_launch_args(pytestconfig):
    headed_cli = pytestconfig.getoption("--headed", default=False)
    headed_env = os.environ.get("SEMAPHORE_TEST_HEADED", "false").lower() == "true"
    headed = headed_cli or headed_env

    slow_mo = int(os.environ.get("SEMAPHORE_TEST_SLOWMO", "0"))

    args = {"headless": not headed}
    if slow_mo > 0:
        args["slow_mo"] = slow_mo
    return args


@pytest.fixture(autouse=True, scope="session")
def _pause_after_tests(browser):
    yield
    pause = int(os.environ.get("SEMAPHORE_TEST_PAUSE", "0"))
    if pause > 0:
        time.sleep(pause)
