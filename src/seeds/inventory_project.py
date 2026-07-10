"""Seed: a project with an access key and two inventories (static + file).

Used by inventory CRUD/modal tests. Both inventories carry an ``ssh_key_id`` so the
edit form loads in a valid state (the UI requires user credentials).
"""

from src.seeds.api import SemaphoreAPI
from src.config import DEFAULT_PROJECT_NAME

STATIC_INVENTORY_NAME = "Static Inventory"
FILE_INVENTORY_NAME = "File Inventory"
STATIC_INVENTORY_BODY = "[all]\nlocalhost ansible_connection=local"
FILE_INVENTORY_PATH = "inventory/hosts"


def run(base_url: str) -> dict:
    api = SemaphoreAPI(base_url)
    project = api.create_project(DEFAULT_PROJECT_NAME)
    project_id = project["id"]

    key = api.create_key_login(project_id, "Test Creds", login="deploy", password="secret")
    key_id = key["id"]

    static_inv = api.create_inventory(
        project_id, STATIC_INVENTORY_NAME, type="static",
        inventory=STATIC_INVENTORY_BODY, ssh_key_id=key_id,
    )
    file_inv = api.create_inventory(
        project_id, FILE_INVENTORY_NAME, type="file",
        inventory=FILE_INVENTORY_PATH, ssh_key_id=key_id,
    )

    return {
        "project": project,
        "key": key,
        "static_inventory": static_inv,
        "file_inventory": file_inv,
    }
