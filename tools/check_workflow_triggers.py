#!/usr/bin/env python3
"""Fail closed if a Sutram workflow auto-runs. Requires only Python standard library.

Usage: python3 tools/check_workflow_triggers.py [workflow_directory]
This intentionally checks the YAML top-level on: event block, not job bodies.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

_ALLOWED = {"workflow_dispatch", "workflow_call"}
_ON = re.compile(r"^(?:on|'on'|\"on\")\s*:\s*(.*?)\s*$")
_EVENT = re.compile(r"^([ ]+)([A-Za-z_][\w-]*)\s*:\s*(?:#.*)?$")
_ITEM = re.compile(r"^([ ]+)-\s*([A-Za-z_][\w-]*)\s*(?:#.*)?$")


def trigger_events(text: str) -> list[str]:
    """Read the YAML top-level on: node; reject unknown syntax, do not guess."""
    lines = text.splitlines()
    matches = [(n, m.group(1)) for n, line in enumerate(lines)
               if (m := _ON.fullmatch(line))]
    if len(matches) != 1:
        raise ValueError("expected exactly one top-level 'on:' block")
    start, inline = matches[0]
    inline = inline.split(" #", 1)[0].strip()
    if inline:
        if inline.startswith("[") and inline.endswith("]"):
            items = [a.strip().strip("'\"") for a in inline[1:-1].split(",")]
        elif re.fullmatch(r"[A-Za-z_][\w-]*", inline):
            items = [inline]
        else:
            raise ValueError("unsupported inline event syntax; use explicit on: mapping")
        if not items or not all(re.fullmatch(r"[A-Za-z_][\w-]*", e) for e in items):
            raise ValueError("invalid inline workflow event")
        return items
    tokens: list[tuple[int, str]] = []
    for line in lines[start + 1:]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[0] not in " \t":
            break
        if line.startswith("\t"):
            raise ValueError("tab-indented on: block unsupported")
        if m := _EVENT.fullmatch(line):
            tokens.append((len(m.group(1)), m.group(2)))
        elif m := _ITEM.fullmatch(line):
            tokens.append((len(m.group(1)), m.group(2)))
        elif not tokens:
            raise ValueError("unrecognized event declaration in on: block")
    if not tokens:
        raise ValueError("no workflow triggers found")
    min_indent = min(indent for indent, _ in tokens)
    return [name for indent, name in tokens if indent == min_indent]


def check_folder(folder: Path) -> list[str]:
    if not folder.is_dir():
        return [f"workflow folder missing: {folder}"]
    paths = sorted(set(folder.glob("*.yml")) | set(folder.glob("*.yaml")))
    if not paths:
        return [f"no workflow files in: {folder}"]
    failures = []
    for path in paths:
        try:
            events = trigger_events(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValueError) as exc:
            failures.append(f"{path}: {exc}")
            continue
        disallowed = sorted(set(events) - _ALLOWED)
        if disallowed:
            failures.append(f"{path}: automatic/unsupported events: {', '.join(disallowed)}")
        else:
            print(f"CI_MANUAL_ONLY_OK {path} events={','.join(events)}")
    return failures


def main() -> int:
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / ".github" / "workflows"
    failures = check_folder(folder)
    for line in failures:
        print("CI_NOTIFICATION_POLICY_FAIL " + line, file=sys.stderr)
    if failures:
        return 1
    print("CI_NOTIFICATION_POLICY_ACCEPTED: no automatic workflow events")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
