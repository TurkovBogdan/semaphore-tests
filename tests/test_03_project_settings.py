import pytest
from playwright.sync_api import Page, expect

from src.pages import sidebar, settings
from src.session import login


@pytest.mark.seeded(seed="empty_project")
class TestProjectRename:

    def test_rename_project_and_rename_back(self, page: Page, base_url: str):
        login(page, base_url)
        page.goto(f"{base_url}/project/1/settings")
        page.wait_for_url(lambda url: "/settings" in url, timeout=5000)

        name_input = page.locator(settings.SETTINGS_PROJECT_NAME)
        expect(name_input).to_be_visible()

        name_input.fill("TestProject2")
        page.locator(settings.SETTINGS_SAVE).click()
        page.wait_for_load_state("networkidle")

        expect(page.locator(sidebar.SIDEBAR_CURRENT_PROJECT)).to_contain_text("TestProject2")

        page.reload()
        page.wait_for_load_state("networkidle")
        expect(page.locator(settings.SETTINGS_PROJECT_NAME)).to_have_value("TestProject2")

        name_input = page.locator(settings.SETTINGS_PROJECT_NAME)
        name_input.fill("TestProject")
        page.locator(settings.SETTINGS_SAVE).click()
        page.wait_for_load_state("networkidle")

        expect(page.locator(sidebar.SIDEBAR_CURRENT_PROJECT)).to_contain_text("TestProject")
