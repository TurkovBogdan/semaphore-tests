# TESTS.md — test index

Complete index of all E2E tests. Each entry: test name, what it verifies, marker.
Updated every time tests are added, removed, or renamed.

## tests/test_01_auth.py

### TestAuthRequired `@clean_db`

| Test | Verifies |
|------|----------|
| `test_root_redirects_to_login` | Unauthenticated `/` redirects to `/auth/login` |
| `test_login_page_has_form` | Login page renders username, password, signin controls |
| `test_api_requires_auth` | `/api/projects` returns 401 without session |
| `test_ping_is_public` | `/api/ping` returns 200 "pong" without auth |

### TestLogin `@clean_db`

| Test | Verifies |
|------|----------|
| `test_wrong_credentials_rejected` | Invalid credentials keep user on login page |
| `test_valid_login_redirects_to_app` | Correct credentials redirect away from login |
| `test_session_persists_after_login` | Authenticated session grants API access |
| `test_cleared_session_requires_reauth` | Clearing cookies forces re-authentication |
| `test_authenticated_user_redirected_from_login` | Authenticated user redirected away from `/auth/login` |

## tests/test_02_new_project.py

### TestNewProjectPage `@clean_db`

| Test | Verifies |
|------|----------|
| `test_empty_db_shows_new_project_form` | Empty DB shows new project form, nav links to new/restore |

### TestCreateEmptyProject `@clean_db`

| Test | Verifies |
|------|----------|
| `test_create_empty_project` | Empty project created, all sections (templates, inventory, keys, repos) are empty |

### TestCreateDemoProject `@clean_db`

| Test | Verifies |
|------|----------|
| `test_create_demo_project` | Demo project created with dashboard, sidebar, templates, inventory, keys, repositories |

## tests/test_03_project_settings.py

### TestProjectRename `@seeded(seed="empty_project")`

| Test | Verifies |
|------|----------|
| `test_rename_project_and_rename_back` | Project renamed via settings, sidebar reflects change, rename reverts correctly |
