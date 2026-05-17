from playwright.sync_api import Page, BrowserContext

from src.config import DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASS
from src.pages import login as login_page


def clear_session(context: BrowserContext) -> None:
    context.clear_cookies()


def login(page: Page, base_url: str, username: str = DEFAULT_ADMIN_USER, password: str = DEFAULT_ADMIN_PASS) -> None:
    page.goto(f"{base_url}/auth/login")
    page.wait_for_load_state("networkidle")
    page.locator(login_page.LOGIN_USERNAME).fill(username)
    page.locator(login_page.LOGIN_PASSWORD).fill(password)
    page.locator(login_page.LOGIN_SIGNIN).click()
    page.wait_for_url(lambda url: "/auth/login" not in url, timeout=10000)


def logout(page: Page, base_url: str) -> None:
    page.request.post(f"{base_url}/api/auth/logout")
    clear_session(page.context)
