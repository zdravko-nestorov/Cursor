#!/usr/bin/env python3
"""Flag em-dashes and en-dashes in text the agent just wrote.

Enforces the no-em-dash part of rules/writing-style.mdc. A rule alone is a
suggestion the model can drift from. This hook checks the actual output.

Wired as a postToolUse hook, which is the only file-edit hook that can send
text back to the agent (afterFileEdit accepts no output fields).

It inspects the content the tool wrote, not the whole file, so pre-existing
dashes in someone else's repo do not trigger it.

Input:  postToolUse JSON payload on stdin.
Output: {"additional_context": "..."} when a dash is found, otherwise {}.
"""

import json
import os
import sys

EM = "\u2014"
EN = "\u2013"

# Keys that hold a path, not written content.
PATH_KEYS = {"path", "file_path", "target_file", "filePath", "notebook_path"}

# The file that defines the rule quotes both characters on purpose.
EXEMPT_BASENAMES = {"writing-style.mdc", "check-dashes.py"}


def emit(obj):
    print(json.dumps(obj))
    sys.exit(0)


def collect_strings(value, out, depth=0):
    """Gather every written string in the tool input, skipping path fields."""
    if depth > 6:
        return
    if isinstance(value, str):
        out.append(value)
    elif isinstance(value, list):
        for item in value:
            collect_strings(item, out, depth + 1)
    elif isinstance(value, dict):
        for key, item in value.items():
            if key in PATH_KEYS:
                continue
            collect_strings(item, out, depth + 1)


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        emit({})

    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        emit({})

    path = ""
    for key in PATH_KEYS:
        value = tool_input.get(key)
        if isinstance(value, str) and value:
            path = value
            break

    if os.path.basename(path) in EXEMPT_BASENAMES:
        emit({})

    written = []
    collect_strings(tool_input, written)

    offenders = [s for s in written if EM in s or EN in s]
    if not offenders:
        emit({})

    count = sum(s.count(EM) + s.count(EN) for s in offenders)
    sample = next(
        (line.strip() for s in offenders for line in s.split("\n") if EM in line or EN in line),
        "",
    )
    where = f" in {path}" if path else ""

    emit({
        "additional_context": (
            f"writing-style violation: the edit you just made{where} contains {count} "
            f"em-dash or en-dash character(s). The rule bans U+2014 and U+2013 in all "
            f"output. Replace each one now: use a spaced hyphen ' - ' for a pause, and an "
            f"unspaced hyphen for ranges such as 1-10. First offending line: {sample[:160]}"
        )
    })


if __name__ == "__main__":
    main()
