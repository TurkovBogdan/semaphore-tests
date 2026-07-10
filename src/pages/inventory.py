"""Selectors for the project Inventory page and its modals.

The Inventory form (InventoryForm.vue) has no data-testid on its fields, so the
fields are addressed positionally by their order in the form. With the default
config (no project_runners feature) the visible inputs are, in order:

    0 — name (text)
    1 — user credentials (ssh_key_id, autocomplete)
    2 — sudo credentials (become_key_id, autocomplete)
    3 — type (select)
    4 — file path (text)      # only when type == File
    5 — repository (select)   # only when type == File
"""

# ── inventory list page ──
NEW_INVENTORY_BTN = ".v-toolbar__content button.primary"   # "New Inventory" menu activator
TABLE_ROWS = "table tbody tr"
ROW_EDIT_ICON = ".mdi-pencil"      # scope to a row
ROW_DELETE_ICON = ".mdi-delete"    # scope to a row

# ── open menu / dropdown options (app choices, v-select, v-autocomplete) ──
# Vuetify appends each open menu as a new .v-menu__content overlay; when two are
# briefly visible at once, scope to the last (newest) one to avoid cross-indexing.
MENU_CONTENT = ".v-menu__content:visible"
MENU_ITEM = ".v-menu__content:visible .v-list-item"
# inventory type order is fixed in InventoryForm.vue data()
TYPE_STATIC_IDX = 0
TYPE_STATIC_YAML_IDX = 1
TYPE_FILE_IDX = 2

# ── create / edit dialog (EditDialog + InventoryForm) ──
DIALOG = ".item-dialog"
DIALOG_SAVE = "[data-testid='editDialog-save']"
DIALOG_CLOSE = "[data-testid='editDialog-close']"
FORM_INPUT = ".item-dialog .v-input"   # positional fields, see module docstring
NAME_IDX = 0
USER_CREDENTIALS_IDX = 1
TYPE_IDX = 3
FILE_PATH_IDX = 4

# ── delete confirmation (YesNoDialog) ──
CONFIRM_DIALOG = ".v-dialog--active"
CONFIRM_YES = ".v-dialog--active button:last-of-type"
