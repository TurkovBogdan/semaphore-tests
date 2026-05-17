import pytest
from playwright.sync_api import Page, expect

from src.config import DEFAULT_PROJECT_NAME, DEFAULT_DEMO_PROJECT_NAME
from src.pages import new_project, sidebar, dashboard
from src.session import login


@pytest.mark.clean_db
class TestNewProjectPage:

    def test_empty_db_shows_new_project_form(self, page: Page, base_url: str):
        login(page, base_url)
        page.wait_for_url(lambda url: "/project/new" in url, timeout=5000)
        expect(page.locator(new_project.NEW_PROJECT_NAME)).to_be_visible()
        expect(page.locator(new_project.NEW_PROJECT_NAV_NEW)).to_be_visible()
        expect(page.locator(new_project.NEW_PROJECT_NAV_RESTORE)).to_be_visible()


@pytest.mark.clean_db
class TestCreateEmptyProject:

    def test_create_empty_project(self, page: Page, base_url: str):
        login(page, base_url)
        page.wait_for_url(lambda url: "/project/new" in url, timeout=10000)
        page.locator(new_project.NEW_PROJECT_NAME).fill(DEFAULT_PROJECT_NAME)
        page.locator(new_project.NEW_PROJECT_CREATE).click()
        page.wait_for_url(lambda url: "/project/" in url and "/history" in url, timeout=10000)

        expect(page.locator(sidebar.SIDEBAR_CURRENT_PROJECT)).to_contain_text(DEFAULT_PROJECT_NAME)

        for endpoint in ["templates", "inventory", "repositories"]:
            resp = page.request.get(f"{base_url}/api/project/1/{endpoint}")
            assert resp.status == 200
            assert resp.json() == [], f"{endpoint} should be empty"

        resp = page.request.get(f"{base_url}/api/project/1/keys")
        assert resp.status == 200
        keys = resp.json()
        assert len(keys) == 1 and keys[0]["type"] == "none"


@pytest.mark.clean_db
class TestCreateDemoProject:

    def test_create_demo_project(self, page: Page, base_url: str):
        login(page, base_url)
        page.wait_for_url(lambda url: "/project/new" in url, timeout=10000)
        page.locator(new_project.NEW_PROJECT_NAME).fill(DEFAULT_DEMO_PROJECT_NAME)
        page.locator(new_project.NEW_PROJECT_CREATE_DEMO).click()
        page.wait_for_url(lambda url: "/project/" in url and "/history" in url, timeout=10000)

        expect(page.locator(sidebar.SIDEBAR_CURRENT_PROJECT)).to_contain_text(DEFAULT_DEMO_PROJECT_NAME)
        expect(page.locator(dashboard.DASHBOARD_HISTORY)).to_be_visible()
        expect(page.locator(dashboard.DASHBOARD_SETTINGS)).to_be_visible()

        expect(page.locator(sidebar.SIDEBAR_TEMPLATES)).to_be_visible()
        expect(page.locator(sidebar.SIDEBAR_INVENTORY)).to_be_visible()
        expect(page.locator(sidebar.SIDEBAR_ENVIRONMENT)).to_be_visible()
        expect(page.locator(sidebar.SIDEBAR_KEYS)).to_be_visible()
        expect(page.locator(sidebar.SIDEBAR_INTEGRATIONS)).to_be_visible()
        expect(page.locator(sidebar.SIDEBAR_TEAM)).to_be_visible()

        page.locator(sidebar.SIDEBAR_TEMPLATES).click()
        page.wait_for_url(lambda url: "/templates" in url, timeout=5000)
        rows = page.locator("table tbody tr")
        expect(rows.first).to_be_visible()
        assert rows.count() > 2

        page.locator(sidebar.SIDEBAR_INVENTORY).click()
        page.wait_for_url(lambda url: "/inventory" in url, timeout=5000)
        rows = page.locator("table tbody tr")
        expect(rows.first).to_be_visible()
        assert rows.count() > 2

        page.locator(sidebar.SIDEBAR_KEYS).click()
        page.wait_for_url(lambda url: "/keys" in url, timeout=5000)
        rows = page.locator("table tbody tr")
        expect(rows.first).to_be_visible()
        assert rows.count() >= 1

        page.locator(sidebar.SIDEBAR_REPOSITORIES).click()
        page.wait_for_url(lambda url: "/repositories" in url, timeout=5000)
        rows = page.locator("table tbody tr")
        expect(rows.first).to_be_visible()
        assert rows.count() >= 1
