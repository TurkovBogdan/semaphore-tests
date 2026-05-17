"""HTTP client for Semaphore API — used by seed functions to populate test data."""

import requests

from src.config import DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASS


class SemaphoreAPI:
    def __init__(self, base_url: str, username: str = DEFAULT_ADMIN_USER, password: str = DEFAULT_ADMIN_PASS):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self._login(username, password)

    def _login(self, username: str, password: str) -> None:
        r = self.session.post(f"{self.base_url}/api/auth/login", json={"auth": username, "password": password})
        r.raise_for_status()

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _project_url(self, project_id: int, resource: str) -> str:
        return self._url(f"/api/project/{project_id}/{resource}")

    # ── projects ──

    def create_project(self, name: str, **kwargs) -> dict:
        r = self.session.post(self._url("/api/projects"), json={"name": name, **kwargs})
        r.raise_for_status()
        return r.json()

    # ── access keys ──

    def create_key_none(self, project_id: int, name: str) -> dict:
        return self._create_key(project_id, {"name": name, "type": "none", "project_id": project_id})

    def create_key_login(self, project_id: int, name: str, login: str, password: str) -> dict:
        return self._create_key(project_id, {
            "name": name, "type": "login_password", "project_id": project_id,
            "login_password": {"login": login, "password": password},
        })

    def create_key_ssh(self, project_id: int, name: str, login: str, private_key: str, passphrase: str = "") -> dict:
        return self._create_key(project_id, {
            "name": name, "type": "ssh", "project_id": project_id,
            "ssh": {"login": login, "passphrase": passphrase, "private_key": private_key},
        })

    def create_key_string(self, project_id: int, name: str, value: str) -> dict:
        return self._create_key(project_id, {
            "name": name, "type": "string", "project_id": project_id, "string": value,
        })

    def _create_key(self, project_id: int, payload: dict) -> dict:
        r = self.session.post(self._project_url(project_id, "keys"), json=payload)
        r.raise_for_status()
        return r.json()

    # ── repositories ──

    def create_repository(self, project_id: int, name: str, git_url: str, git_branch: str, ssh_key_id: int) -> dict:
        r = self.session.post(self._project_url(project_id, "repositories"), json={
            "name": name, "project_id": project_id,
            "git_url": git_url, "git_branch": git_branch, "ssh_key_id": ssh_key_id,
        })
        r.raise_for_status()
        return r.json()

    # ── inventory ──

    def create_inventory(self, project_id: int, name: str, type: str, inventory: str, **kwargs) -> dict:
        r = self.session.post(self._project_url(project_id, "inventory"), json={
            "name": name, "project_id": project_id,
            "type": type, "inventory": inventory, **kwargs,
        })
        r.raise_for_status()
        return r.json()

    # ── environment ──

    def create_environment(self, project_id: int, name: str, json_vars: str = "{}", env: str | None = None, **kwargs) -> dict:
        r = self.session.post(self._project_url(project_id, "environment"), json={
            "name": name, "project_id": project_id,
            "json": json_vars, "env": env, **kwargs,
        })
        r.raise_for_status()
        return r.json()

    # ── templates ──

    def create_template(self, project_id: int, name: str, repository_id: int, app: str = "ansible", **kwargs) -> dict:
        r = self.session.post(self._project_url(project_id, "templates"), json={
            "name": name, "project_id": project_id,
            "repository_id": repository_id, "app": app, **kwargs,
        })
        r.raise_for_status()
        return r.json()

    # ── views ──

    def create_view(self, project_id: int, title: str, **kwargs) -> dict:
        r = self.session.post(self._project_url(project_id, "views"), json={
            "title": title, "project_id": project_id, **kwargs,
        })
        r.raise_for_status()
        return r.json()

    # ── schedules ──

    def create_schedule(self, project_id: int, name: str, template_id: int, cron_format: str, **kwargs) -> dict:
        r = self.session.post(self._project_url(project_id, "schedules"), json={
            "name": name, "project_id": project_id,
            "template_id": template_id, "cron_format": cron_format, **kwargs,
        })
        r.raise_for_status()
        return r.json()

    # ── tasks ──

    def run_task(self, project_id: int, template_id: int, **kwargs) -> dict:
        r = self.session.post(self._project_url(project_id, "tasks"), json={
            "template_id": template_id, "project_id": project_id, **kwargs,
        })
        r.raise_for_status()
        return r.json()

    # ── generic GET/list ──

    def list_projects(self) -> list[dict]:
        r = self.session.get(self._url("/api/projects"))
        r.raise_for_status()
        return r.json()

    def list_keys(self, project_id: int) -> list[dict]:
        r = self.session.get(self._project_url(project_id, "keys"))
        r.raise_for_status()
        return r.json()

    def list_repositories(self, project_id: int) -> list[dict]:
        r = self.session.get(self._project_url(project_id, "repositories"))
        r.raise_for_status()
        return r.json()

    def list_inventory(self, project_id: int) -> list[dict]:
        r = self.session.get(self._project_url(project_id, "inventory"))
        r.raise_for_status()
        return r.json()

    def list_environments(self, project_id: int) -> list[dict]:
        r = self.session.get(self._project_url(project_id, "environment"))
        r.raise_for_status()
        return r.json()

    def list_templates(self, project_id: int) -> list[dict]:
        r = self.session.get(self._project_url(project_id, "templates"))
        r.raise_for_status()
        return r.json()

    def list_views(self, project_id: int) -> list[dict]:
        r = self.session.get(self._project_url(project_id, "views"))
        r.raise_for_status()
        return r.json()

    def list_schedules(self, project_id: int) -> list[dict]:
        r = self.session.get(self._project_url(project_id, "schedules"))
        r.raise_for_status()
        return r.json()
