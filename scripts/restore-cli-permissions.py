#!/usr/bin/env python3
"""Copy the tracked permission rules in cli-permissions.json into cli-config.json.

cli-config.json is not tracked, because it also holds account details
(email, userId, authId). Only the "permissions" key is versioned, in
cli-permissions.json. Run this after cloning this repo onto a new machine.

Usage:
    python3 scripts/restore-cli-permissions.py [--dry-run]
"""

import json
import shutil
import sys
from pathlib import Path

CURSOR_DIR = Path(__file__).resolve().parent.parent
SRC = CURSOR_DIR / "cli-permissions.json"
DST = CURSOR_DIR / "cli-config.json"


def main() -> int:
    dry_run = "--dry-run" in sys.argv[1:]

    if not SRC.exists():
        print(f"missing {SRC}", file=sys.stderr)
        return 1

    perms = json.loads(SRC.read_text())["permissions"]
    config = json.loads(DST.read_text()) if DST.exists() else {"version": 1}

    if config.get("permissions") == perms:
        print("cli-config.json already matches cli-permissions.json, nothing to do")
        return 0

    allow = len(perms.get("allow", []))
    deny = len(perms.get("deny", []))
    print(f"applying {allow} allow rules and {deny} deny rules to {DST}")

    if dry_run:
        print("dry run, no changes written")
        return 0

    if DST.exists():
        backup = DST.with_suffix(".json.bak")
        shutil.copy2(DST, backup)
        print(f"backed up previous config to {backup}")

    config["permissions"] = perms
    DST.write_text(json.dumps(config, indent=2) + "\n")
    print("done. Restart the Cursor CLI to pick up the new rules.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
