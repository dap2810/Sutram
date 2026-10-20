#!/usr/bin/env python3
"""Independent, read-only, per-pack structural audit of Sutram .sandesh.

This complements tools/sandesh.py --check; it does not certify the grammar,
translation quality or native compiler behavior. Review findings do not force
changes to an unreviewed draft language pack.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import unicodedata

PACKS = {
    "sanskrit": (0x0900, 0x097F),
    "hindi": (0x0900, 0x097F),
    "marathi": (0x0900, 0x097F),
    "gujarati": (0x0A80, 0x0AFF),
    "bengali": (0x0980, 0x09FF),
    "punjabi": (0x0A00, 0x0A7F),
    "odia": (0x0B00, 0x0B7F),
    "tamil": (0x0B80, 0x0BFF),
    "telugu": (0x0C00, 0x0C7F),
    "kannada": (0x0C80, 0x0CFF),
    "malayalam": (0x0D00, 0x0D7F),
}
SUPPORTED = {"sanskrit", "hindi", "gujarati"}
SHARED_MARKS = {0x0964, 0x0965, 0x200C, 0x200D}
TAGS = re.compile(r"Sutram Error|\[E_[A-Z0-9_]+\]")
PLACEHOLDERS = re.compile(r"\{(?:kw:[A-Za-z_][A-Za-z0-9_]*|ver)\}")
LATIN = re.compile(r"[A-Za-z][A-Za-z0-9_]*")
# The existing generator defines recognized user-facing code words. Additional
# Latin strings are review candidates, not automatically bad translations.


def parse_pack(text: str):
    entries = {}
    problems = []
    for n, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, sep, raw = line.partition("\t")
        if not sep:
            problems.append({"line": n, "issue": "missing tab"})
            continue
        if key in entries:
            problems.append({"line": n, "key": key, "issue": "duplicate key"})
            continue
        try:
            value = json.loads(raw)
        except (ValueError, TypeError) as exc:
            problems.append({"line": n, "key": key, "issue": "invalid JSON: " + str(exc)})
            continue
        if not isinstance(value, str):
            problems.append({"line": n, "key": key, "issue": "value not a string"})
            continue
        entries[key] = value
    return entries, problems


def placeholders(s):
    return Counter(x.group() for x in PLACEHOLDERS.finditer(s))


def examine(packs: dict[str, str], code_words: set[str] | None = None):
    words = code_words or set()
    loaded = {name: parse_pack(text) for name, text in packs.items()}
    reference = loaded.get("sanskrit", ({}, []))[0]
    expected = set(reference)
    rows = {}
    for pack, (lo, hi) in PACKS.items():
        values, parse_errors = loaded.get(pack, ({}, [{"issue": "missing pack file"}]))
        failures = [{"issue": "parse", **x} for x in parse_errors]
        reviews = []
        missing = sorted(expected - set(values))
        extra = sorted(set(values) - expected)
        for key in missing:
            failures.append({"key": key, "issue": "missing key"})
        for key in extra:
            failures.append({"key": key, "issue": "unexpected key"})
        for key, text in values.items():
            if not text:
                failures.append({"key": key, "issue": "empty message"})
            if key not in reference:
                continue
            base = reference[key]
            if TAGS.findall(text) != TAGS.findall(base):
                failures.append({"key": key, "issue": "Sutram Error/[E_] identifiers changed"})
            for boundary in ("left", "right"):
                if boundary == "left" and base.startswith("'") and not text.startswith("'"):
                    failures.append({"key": key, "issue": "opening name quote removed"})
                if boundary == "right" and base.endswith("'") and not text.endswith("'"):
                    failures.append({"key": key, "issue": "closing name quote removed"})
            original, translated = placeholders(base), placeholders(text)
            for marker, expected_count in original.items():
                if translated[marker] < expected_count:
                    failures.append({"key": key, "issue": "placeholder missing",
                                     "placeholder": marker,
                                     "want": expected_count, "actual": translated[marker]})
            for marker, count in translated.items():
                if count > original[marker]:
                    reviews.append({"key": key, "issue": "additional placeholder",
                                    "placeholder": marker, "extra_count": count - original[marker]})
            if pack != "sanskrit" and text == base:
                reviews.append({"key": key, "issue": "identical to Sanskrit; review if meaningful"})
            cleaned = TAGS.sub("", PLACEHOLDERS.sub("", text))
            for ch in cleaned:
                cp = ord(ch)
                if cp < 128 or cp in SHARED_MARKS or lo <= cp <= hi:
                    continue
                if unicodedata.category(ch)[:1] in ("L", "M"):
                    failures.append({"key": key, "issue": "wrong-script Unicode letter/mark",
                                     "codepoint": f"U+{cp:04X}"})
                    break
            latin = set(LATIN.findall(cleaned))
            for word in sorted(latin - words):
                reviews.append({"key": key, "issue": "Latin token not in recognized-code whitelist",
                                "token": word})
        rows[pack] = {
            "tier": "SUPPORTED" if pack in SUPPORTED else "DRAFT",
            "entries": len(values), "hard_violations": len(failures),
            "review_candidates": len(reviews), "failures": failures, "reviews": reviews,
        }
    return {
        "status": "FAIL" if any(x["hard_violations"] for x in rows.values()) else "PASS",
        "scope": "11 .sandesh pack source files, lexical/structural checks only",
        "canonical_keys": len(reference), "packs": rows,
        "native_programs_executed": False,
    }


def run(root: Path):
    files = {}
    for pack in PACKS:
        path = root / "lang" / f"{pack}.sandesh"
        if path.is_symlink():
            raise ValueError("symlinked pack refused: " + str(path))
        files[pack] = path.read_text(encoding="utf8")
    # Reuse only generator's finite code-word allowlist, not its check_entry logic.
    from importlib.util import module_from_spec, spec_from_file_location
    p = root / "tools" / "sandesh.py"
    spec = spec_from_file_location("sutram_sandesh_allowlist", p)
    module = module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return examine(files, set(module.CODE_WORDS))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument("--report", type=Path)
    a = p.parse_args()
    try:
        report = run(a.repo)
    except (OSError, UnicodeError, ValueError) as exc:
        report = {"status": "FAIL", "reason": str(exc)}
    result = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    print(result, end="")
    if a.report:
        with a.report.open("x", encoding="utf8") as out:
            out.write(result)
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
