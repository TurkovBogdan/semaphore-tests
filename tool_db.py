#!/usr/bin/env python3
"""Inspect the test SQLite database."""

import sqlite3
import sys
from pathlib import Path

DB = Path(__file__).resolve().parent / ".testdata" / "database.sqlite"


def connect():
    if not DB.exists():
        print(f"Database not found: {DB}")
        print("Run tests first or execute: ./scripts/build.sh")
        sys.exit(1)
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def fmt_table(rows: list[sqlite3.Row]) -> str:
    if not rows:
        return "(empty)"
    keys = rows[0].keys()
    widths = {k: len(k) for k in keys}
    str_rows = []
    for row in rows:
        vals = {k: str(row[k]) if row[k] is not None else "" for k in keys}
        for k, v in vals.items():
            widths[k] = max(widths[k], len(v))
        str_rows.append(vals)

    header = "  ".join(k.ljust(widths[k]) for k in keys)
    sep = "  ".join("-" * widths[k] for k in keys)
    lines = [header, sep]
    for vals in str_rows:
        lines.append("  ".join(vals[k].ljust(widths[k]) for k in keys))
    return "\n".join(lines)


def cmd_tables():
    conn = connect()
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
    for r in rows:
        print(r["name"])


def cmd_schema(table: str | None = None):
    conn = connect()
    if table:
        rows = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchall()
    else:
        rows = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
    for r in rows:
        if r["sql"]:
            print(r["sql"] + ";")
            print()


def cmd_dump(table: str):
    conn = connect()
    rows = conn.execute(f'SELECT * FROM "{table}"').fetchall()
    print(fmt_table(rows))


def cmd_count(table: str | None = None):
    conn = connect()
    if table:
        c = conn.execute(f'SELECT COUNT(*) as c FROM "{table}"').fetchone()["c"]
        print(c)
    else:
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
        for t in tables:
            name = t["name"]
            c = conn.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
            if c > 0:
                print(f"{name:<40} {c}")


def cmd_query(sql: str):
    conn = connect()
    rows = conn.execute(sql).fetchall()
    if rows:
        print(fmt_table(rows))


def cmd_users():
    conn = connect()
    rows = conn.execute("SELECT id, username, name, email, admin, created FROM user").fetchall()
    print(fmt_table(rows))


def cmd_projects():
    conn = connect()
    rows = conn.execute("SELECT id, name, created FROM project").fetchall()
    print(fmt_table(rows))


def cmd_keys(project_id: int):
    conn = connect()
    rows = conn.execute("SELECT id, name, type FROM access_key WHERE project_id=?", (project_id,)).fetchall()
    print(fmt_table(rows))


def cmd_repos(project_id: int):
    conn = connect()
    rows = conn.execute("SELECT id, name, git_url, git_branch FROM project__repository WHERE project_id=?", (project_id,)).fetchall()
    print(fmt_table(rows))


def cmd_templates(project_id: int):
    conn = connect()
    rows = conn.execute("SELECT id, name, app, playbook, type FROM project__template WHERE project_id=?", (project_id,)).fetchall()
    print(fmt_table(rows))


def cmd_tasks(project_id: int):
    conn = connect()
    rows = conn.execute('SELECT id, template_id, status, start, "end" FROM task WHERE project_id=?', (project_id,)).fetchall()
    print(fmt_table(rows))


USAGE = """\
Usage: uv run db.py <command> [args]

Commands:
  tables                List all tables
  schema [TABLE]        Show DDL (all or one table)
  dump TABLE            All rows in a table
  count [TABLE]         Row counts (non-empty tables, or one)
  query "SQL"           Arbitrary SQL
  users                 Show users
  projects              Show projects
  keys PROJECT_ID       Access keys for a project
  repos PROJECT_ID      Repositories for a project
  templates PROJECT_ID  Templates for a project
  tasks PROJECT_ID      Tasks for a project"""


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help", "help"):
        print(USAGE)
        return

    cmd = args[0]
    rest = args[1:]

    match cmd:
        case "tables":
            cmd_tables()
        case "schema":
            cmd_schema(rest[0] if rest else None)
        case "dump":
            if not rest:
                print("Usage: db.py dump TABLE"); sys.exit(1)
            cmd_dump(rest[0])
        case "count":
            cmd_count(rest[0] if rest else None)
        case "query":
            if not rest:
                print("Usage: db.py query \"SQL\""); sys.exit(1)
            cmd_query(rest[0])
        case "users":
            cmd_users()
        case "projects":
            cmd_projects()
        case "keys":
            if not rest:
                print("Usage: db.py keys PROJECT_ID"); sys.exit(1)
            cmd_keys(int(rest[0]))
        case "repos":
            if not rest:
                print("Usage: db.py repos PROJECT_ID"); sys.exit(1)
            cmd_repos(int(rest[0]))
        case "templates":
            if not rest:
                print("Usage: db.py templates PROJECT_ID"); sys.exit(1)
            cmd_templates(int(rest[0]))
        case "tasks":
            if not rest:
                print("Usage: db.py tasks PROJECT_ID"); sys.exit(1)
            cmd_tasks(int(rest[0]))
        case _:
            print(f"Unknown command: {cmd}")
            print(USAGE)
            sys.exit(1)


if __name__ == "__main__":
    main()
