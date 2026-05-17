---
title: Semaphore REST API — CRUD payloads
date: 2026-05-18
description: "Exact JSON payloads for creating entities via the Semaphore REST API. Used to write seed functions."
tags: [semaphore, api, seeds]
---

## Auth

### Login — `POST /api/auth/login`

Cookie-based session. Response sets `semaphore` cookie (used in all subsequent requests).

```json
{"auth": "username_or_email", "password": "password"}
```

Response: 204 No Content + `Set-Cookie: semaphore=...`

Alternative: `Authorization: Bearer <token>` header (API tokens).

---

## Entities (creation order)

### Project — `POST /api/projects`

```json
{
  "name": "string (required)",
  "type": "string (optional)",
  "alert": false,
  "alert_chat": null,
  "max_parallel_tasks": 0
}
```

Response: 201 + Project object (has `id`).

### AccessKey — `POST /api/project/{project_id}/keys`

Types: `ssh`, `login_password`, `none`, `string`.

**none** (simplest — no credentials):
```json
{"name": "string", "type": "none", "project_id": 1}
```

**login_password**:
```json
{
  "name": "string", "type": "login_password", "project_id": 1,
  "login_password": {"login": "user", "password": "pass"}
}
```

**ssh**:
```json
{
  "name": "string", "type": "ssh", "project_id": 1,
  "ssh": {"login": "user", "passphrase": "", "private_key": "PEM string"}
}
```

**string** (vault password, etc.):
```json
{"name": "string", "type": "string", "project_id": 1, "string": "value"}
```

### Repository — `POST /api/project/{project_id}/repositories`

```json
{
  "name": "string",
  "project_id": 1,
  "git_url": "https://github.com/user/repo.git",
  "git_branch": "main",
  "ssh_key_id": 1
}
```

`ssh_key_id` — ID of an AccessKey (even type `none`).

### Inventory — `POST /api/project/{project_id}/inventory`

Types: `static`, `static-yaml`, `file`, `terraform-workspace`, `tofu-workspace`, `terragrunt-workspace`.

**static** (INI format):
```json
{
  "name": "string", "project_id": 1, "type": "static",
  "inventory": "[all]\nlocalhost ansible_connection=local",
  "ssh_key_id": null, "become_key_id": null
}
```

**static-yaml**:
```json
{
  "name": "string", "project_id": 1, "type": "static-yaml",
  "inventory": "all:\n  hosts:\n    localhost:\n      ansible_connection: local"
}
```

**file** (path in repo):
```json
{"name": "string", "project_id": 1, "type": "file", "inventory": "invs/hosts"}
```

### Environment — `POST /api/project/{project_id}/environment`

```json
{
  "name": "string",
  "project_id": 1,
  "json": "{}",
  "env": null,
  "password": null
}
```

- `json` — extra variables (JSON object as string)
- `env` — environment variables (JSON object with scalar values, or null)
- `password` — vault password (optional)

### Template — `POST /api/project/{project_id}/templates`

App types: `ansible` (default), `terraform`, `tofu`, `terragrunt`, `bash`, `powershell`, `python`, `pulumi`.
Task types (field `type`): `""` (task), `"build"`, `"deploy"`.

**Minimal Ansible**:
```json
{
  "name": "string",
  "project_id": 1,
  "app": "ansible",
  "playbook": "site.yml",
  "repository_id": 1,
  "inventory_id": 1,
  "environment_ids": [1]
}
```

**Minimal Bash**:
```json
{
  "name": "string",
  "project_id": 1,
  "app": "bash",
  "playbook": "script.sh",
  "repository_id": 1,
  "environment_ids": [1]
}
```

Optional fields: `description`, `arguments` (JSON string), `type`, `view_id`, `autorun`, `git_branch`, `build_template_id`, `allow_override_args_in_task`, `allow_override_branch_in_task`, `allow_parallel_tasks`, `suppress_success_alerts`, `survey_vars`, `task_params`.

### View — `POST /api/project/{project_id}/views`

```json
{
  "title": "string",
  "project_id": 1,
  "position": 0
}
```

### Schedule — `POST /api/project/{project_id}/schedules`

**Cron**:
```json
{
  "name": "string", "project_id": 1, "template_id": 1,
  "cron_format": "0 9 * * *", "active": true, "type": ""
}
```

**One-time** (`run_at`):
```json
{
  "name": "string", "project_id": 1, "template_id": 1,
  "run_at": "2026-06-01T09:00:00Z", "active": true, "type": "run_at"
}
```

### Task (run) — `POST /api/project/{project_id}/tasks`

```json
{
  "template_id": 1,
  "project_id": 1
}
```

Optional: `playbook`, `environment`, `arguments`, `git_branch`, `inventory_id`, `params` (debug, dry_run, diff, limit, tags, skip_tags for Ansible; plan, destroy, auto_approve for Terraform).

---

## Entity dependency graph

```
User (admin, created by migration)
 └─ Project
     ├─ AccessKey (none / login_password / ssh / string)
     ├─ Repository → AccessKey
     ├─ Inventory → AccessKey (optional)
     ├─ Environment
     ├─ View
     └─ Template → Repository, Inventory, Environment[], View
         ├─ Schedule → Template
         └─ Task → Template
```
