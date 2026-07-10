import pytest
from playwright.sync_api import Page, expect

from src.pages import inventory
from src.seeds.inventory_project import (
    STATIC_INVENTORY_NAME,
    FILE_INVENTORY_NAME,
)
from src.session import login

PROJECT_INVENTORY_URL = "/project/1/inventory"


def _open_inventory(page: Page, base_url: str) -> None:
    login(page, base_url)
    page.goto(f"{base_url}{PROJECT_INVENTORY_URL}")
    page.wait_for_url(lambda url: "/inventory" in url, timeout=5000)
    page.wait_for_load_state("networkidle")


def _open_new_inventory_dialog(page: Page) -> None:
    """Open the 'New Inventory' menu and pick the (only) Ansible app → edit dialog."""
    page.locator(inventory.NEW_INVENTORY_BTN).click()
    page.locator(inventory.MENU_ITEM).first.click()
    expect(page.locator(inventory.DIALOG_SAVE)).to_be_visible()


def _pick_option(page: Page, field_index: int, *, index: int | None = None, text: str | None = None) -> None:
    """Open a v-select/v-autocomplete field and choose an option by index or by text.

    Scoped to the newest open menu so a still-closing previous menu can't shift indices.
    """
    page.locator(inventory.FORM_INPUT).nth(field_index).locator("input").first.click()
    menu = page.locator(inventory.MENU_CONTENT).last
    expect(menu.locator(".v-list-item").first).to_be_visible()
    if text is not None:
        menu.locator(".v-list-item", has_text=text).click()
    else:
        menu.locator(".v-list-item").nth(index).click()


@pytest.mark.seeded(seed="inventory_project")
class TestInventoryModal:

    def test_new_inventory_modal_opens_and_closes(self, page: Page, base_url: str):
        _open_inventory(page, base_url)

        _open_new_inventory_dialog(page)
        expect(page.locator(inventory.DIALOG)).to_be_visible()
        expect(page.locator(inventory.DIALOG_SAVE)).to_be_visible()
        expect(page.locator(inventory.DIALOG_CLOSE)).to_be_visible()

        page.locator(inventory.DIALOG_CLOSE).click()
        expect(page.locator(inventory.DIALOG_SAVE)).to_be_hidden()


@pytest.mark.seeded(seed="inventory_project")
class TestCreateInventory:

    def test_create_file_inventory(self, page: Page, base_url: str):
        _open_inventory(page, base_url)
        _open_new_inventory_dialog(page)

        name = "Created Inventory"
        path = "created/hosts"
        page.locator(inventory.FORM_INPUT).nth(inventory.NAME_IDX).locator("input").fill(name)
        _pick_option(page, inventory.USER_CREDENTIALS_IDX, text="Test Creds")
        _pick_option(page, inventory.TYPE_IDX, index=inventory.TYPE_FILE_IDX)
        page.locator(inventory.FORM_INPUT).nth(inventory.FILE_PATH_IDX).locator("input").fill(path)

        page.locator(inventory.DIALOG_SAVE).click()
        expect(page.locator(inventory.DIALOG_SAVE)).to_be_hidden()

        expect(page.locator(inventory.TABLE_ROWS, has_text=name)).to_be_visible()

        items = page.request.get(f"{base_url}/api/project/1/inventory").json()
        created = [i for i in items if i["name"] == name]
        assert len(created) == 1
        assert created[0]["type"] == "file"
        assert created[0]["inventory"] == path


@pytest.mark.seeded(seed="inventory_project")
class TestEditInventory:

    def test_edit_inventory_name(self, page: Page, base_url: str):
        _open_inventory(page, base_url)

        row = page.locator(inventory.TABLE_ROWS, has_text=STATIC_INVENTORY_NAME)
        row.locator(inventory.ROW_EDIT_ICON).click()

        name_input = page.locator(inventory.FORM_INPUT).nth(inventory.NAME_IDX).locator("input")
        expect(name_input).to_have_value(STATIC_INVENTORY_NAME)

        new_name = "Renamed Inventory"
        name_input.fill(new_name)
        page.locator(inventory.DIALOG_SAVE).click()
        expect(page.locator(inventory.DIALOG_SAVE)).to_be_hidden()

        expect(page.locator(inventory.TABLE_ROWS, has_text=new_name)).to_be_visible()
        expect(page.locator(inventory.TABLE_ROWS, has_text=STATIC_INVENTORY_NAME)).to_have_count(0)

        items = page.request.get(f"{base_url}/api/project/1/inventory").json()
        names = {i["name"] for i in items}
        assert new_name in names
        assert STATIC_INVENTORY_NAME not in names


@pytest.mark.seeded(seed="inventory_project")
class TestDeleteInventory:

    def test_delete_inventory_via_confirm_dialog(self, page: Page, base_url: str):
        _open_inventory(page, base_url)
        expect(page.locator(inventory.TABLE_ROWS)).to_have_count(2)

        row = page.locator(inventory.TABLE_ROWS, has_text=FILE_INVENTORY_NAME)
        row.locator(inventory.ROW_DELETE_ICON).click()

        expect(page.locator(inventory.CONFIRM_DIALOG)).to_be_visible()
        page.locator(inventory.CONFIRM_YES).click()

        expect(page.locator(inventory.TABLE_ROWS, has_text=FILE_INVENTORY_NAME)).to_have_count(0)
        expect(page.locator(inventory.TABLE_ROWS)).to_have_count(1)

        items = page.request.get(f"{base_url}/api/project/1/inventory").json()
        names = {i["name"] for i in items}
        assert FILE_INVENTORY_NAME not in names
        assert STATIC_INVENTORY_NAME in names
