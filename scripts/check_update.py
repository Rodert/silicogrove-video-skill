#!/usr/bin/env python3
"""Check the installed skill for upstream changes at most once per day."""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

CHECK_INTERVAL_SECONDS = 24 * 60 * 60


def cache_path():
    if os.name == "nt":
        root = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    else:
        root = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    return root / "silicogrove-video" / "update-check.json"


def private_mode(path, mode):
    if os.name != "nt":
        os.chmod(path, mode)


def read_last_checked(path):
    try:
        with open(path, encoding="utf-8") as handle:
            value = json.load(handle).get("last_checked")
        return float(value)
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        return None


def write_last_checked(path, timestamp):
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        private_mode(path.parent, 0o700)
        with open(temporary, "w", encoding="utf-8") as handle:
            private_mode(temporary, 0o600)
            json.dump({"last_checked": timestamp}, handle)
            handle.write("\n")
        os.replace(temporary, path)
        private_mode(path, 0o600)
        return True
    except OSError:
        return False
    finally:
        try:
            if temporary.exists():
                temporary.unlink()
        except OSError:
            pass


def git_output(skill_dir, *args):
    return subprocess.run(
        ["git", "-C", str(skill_dir), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    )


def head(skill_dir):
    result = subprocess.run(
        ["git", "-C", str(skill_dir), "rev-parse", "HEAD"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def check(skill_dir):
    now = time.time()
    marker = cache_path()
    last_checked = read_last_checked(marker)
    if last_checked is not None and now - last_checked < CHECK_INTERVAL_SECONDS:
        return "skipped"

    before = head(skill_dir)
    if not before:
        write_last_checked(marker, now)
        return "unavailable"

    result = git_output(skill_dir, "pull", "--ff-only", "origin", "main")
    write_last_checked(marker, now)
    if result.returncode == 0:
        return "updated" if head(skill_dir) != before else "checked"

    status = git_output(skill_dir, "status", "--porcelain")
    return "blocked" if status.returncode == 0 and status.stdout else "failed"


def main():
    if len(sys.argv) != 2:
        print("Usage: check_update.py SKILL_DIR", file=sys.stderr)
        return 2
    result = check(Path(sys.argv[1]).expanduser().resolve())
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
