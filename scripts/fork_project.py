#!/usr/bin/env python3
"""Fork an existing project into a new one with the same layout but fresh personas.

Usage:
  python scripts/fork_project.py [SOURCE_PID] [--name NAME] [--server URL]

The script:
  1. Reads the source project's metadata + active setup (store layout).
  2. Writes a new project dir under backend/.data/ with a fresh pid and setup id
     — same store layout, empty personas, no run history.
  3. Triggers persona generation via the dev server so the dashboard sees it
     immediately. PERSONA_DAILY_CAP env var still applies, so the new project
     will be capped (default 100/day).

Run this with the dev server up. The new project shows up at the top of the
project list once generation kicks off.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "backend" / ".data"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def read_json(path: Path) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def fork(source_pid: str, *, new_name: str | None, server_url: str) -> None:
    src = DATA_DIR / source_pid
    if not src.is_dir():
        sys.exit(f"source project not found: {src}")

    meta = read_json(src / "metadata.json")
    state = read_json(src / "state.json")
    active_sid = state.get("activeSetupId")
    if not active_sid:
        sys.exit("source project has no active setup")
    src_setup = read_json(src / "setups" / f"{active_sid}.json")
    store = src_setup.get("store")
    if store is None:
        sys.exit("active setup has no store layout to copy")

    new_pid = f"proj_{uuid.uuid4().hex[:8]}"
    new_sid = f"setup_{uuid.uuid4().hex[:4]}"
    dst = DATA_DIR / new_pid
    dst.mkdir(parents=True, exist_ok=False)

    now = now_iso()
    new_meta = {
        **meta,
        "project_id": new_pid,
        "name": new_name or f"{meta.get('name', 'Project')} (copy)",
        "created_at": now,
        "updated_at": now,
    }
    write_json(dst / "metadata.json", new_meta)

    new_setup = {
        "id": new_sid,
        "name": src_setup.get("name", "layout 1"),
        "status": "draft",
        "parentId": None,
        "store": store,
        "runId": None,
        "memo": "",
        "created_at": now,
        "updated_at": now,
    }
    write_json(dst / "setups" / f"{new_sid}.json", new_setup)
    write_json(dst / "state.json", {"activeSetupId": new_sid})
    write_json(dst / "personas.json", [])

    print(f"forked: {source_pid} → {new_pid} (setup {new_sid})")

    url = f"{server_url.rstrip('/')}/api/projects/{new_pid}/setups/{new_sid}/regenerate-persona"
    req = urllib.request.Request(url, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read())
        print(f"persona generation kicked off: gen_id={body.get('gen_id')}")
        print(f"watch progress in the dashboard at {server_url}.")
    except urllib.error.URLError as exc:
        print(
            f"warning: failed to trigger persona generation ({exc}).\n"
            f"  The project files were written successfully — start the dev server\n"
            f"  and use the dashboard's persona-regenerate action on setup {new_sid}."
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_pid", nargs="?", default="proj_67916afd")
    parser.add_argument("--name", default=None, help="name for the new project (default: '<src> (copy)')")
    parser.add_argument("--server", default="http://localhost:8000", help="dev server URL")
    args = parser.parse_args()
    fork(args.source_pid, new_name=args.name, server_url=args.server)


if __name__ == "__main__":
    main()
