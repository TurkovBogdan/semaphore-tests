import pytest
from playwright.sync_api import Page, BrowserContext, expect

from src.config import DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASS
from src.pages import login as login_page
from src.session import login, clear_session


@pytest.mark.clean_db
class TestAuthRequired:

    def test_root_redirects_to_login(self, page: Page, base_url: str):
        page.goto(base_url)
        expect(page).to_have_url(f"{base_url}/auth/login?return=%2F")

    def test_login_page_has_form(self, page: Page, base_url: str):
        page.goto(f"{base_url}/auth/login")
        expect(page.locator(login_page.LOGIN_USERNAME)).to_be_visible()
        expect(page.locator(login_page.LOGIN_PASSWORD)).to_be_visible()
        expect(page.locator(login_page.LOGIN_SIGNIN)).to_be_visible()

    def test_api_requires_auth(self, page: Page, base_url: str):
        response = page.request.get(f"{base_url}/api/projects")
        assert response.status == 401

    def test_ping_is_public(self, page: Page, base_url: str):
        response = page.request.get(f"{base_url}/api/ping")
        assert response.status == 200
        assert response.text() == "pong"


@pytest.mark.clean_db
class TestLogin:

    def test_wrong_credentials_rejected(self, page: Page, base_url: str):
        page.goto(f"{base_url}/auth/login")
        page.locator(login_page.LOGIN_USERNAME).fill("wrong")
        page.locator(login_page.LOGIN_PASSWORD).fill("wrong")
        page.locator(login_page.LOGIN_SIGNIN).click()
        expect(page).to_have_url(f"{base_url}/auth/login", timeout=3000)

    def test_valid_login_redirects_to_app(self, page: Page, base_url: str):
        login(page, base_url)
        expect(page).not_to_have_url(f"{base_url}/auth/login")

    def test_session_persists_after_login(self, page: Page, base_url: str):
        login(page, base_url)
        response = page.request.get(f"{base_url}/api/projects")
        assert response.status == 200

    def test_cleared_session_requires_reauth(self, page: Page, context: BrowserContext, base_url: str):
        login(page, base_url)
        clear_session(context)
        page.goto(base_url)
        expect(page).to_have_url(f"{base_url}/auth/login?return=%2F")

    def test_authenticated_user_redirected_from_login(self, page: Page, base_url: str):
        login(page, base_url)
        page.goto(f"{base_url}/auth/login")
        page.wait_for_url(lambda url: "/auth/login" not in url, timeout=5000)
