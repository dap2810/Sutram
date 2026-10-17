#!/usr/bin/env python3
"""Run a pinned, six-category Sutram rejection corpus; never build or install.

--validate-only checks corpus files, NOT compiler behavior. Native mode requires
an explicitly selected compiler, matching repository source pins and successful
positive controls. Unexpectedly accepted negative programs are never executed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import tempfile
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "tests/negative/r70/manifest.json"
CATEGORIES = frozenset({"bad_type", "bad_arity", "unknown_identifier",
                        "malformed_literal", "unterminated_string", "misplaced_keyword"})
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
MAX_INPUT = 65536
MAX_LOG = 262144


class CorpusError(ValueError):
    """A corpus/input identity or execution precondition did not hold."""


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def repository_file(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or "\\" in relative:
        raise CorpusError("repository paths must be relative POSIX paths")
    parts = PurePosixPath(relative)
    if parts.is_absolute() or not parts.parts or any(p in ("..", ".") for p in parts.parts):
        raise CorpusError(f"unsafe repository path: {relative!r}")
    root = root.resolve()
    path = root
    for part in parts.parts:
        path = path / part
        if path.is_symlink():
            raise CorpusError(f"symlink input not accepted: {relative}")
    if not path.is_file() or root not in path.resolve().parents:
        raise CorpusError(f"missing/outside repository file: {relative}")
    return path


def read_case(root: Path, case: dict[str, Any]) -> bytes:
    path = repository_file(root, case["source"])
    raw = path.read_bytes()
    if sha256(raw) != case["file_sha256"]:
        raise CorpusError(f"fixture drift: {case['id']}")
    if case["encoding"] == "hex":
        try:
            data = bytes.fromhex(raw.decode("ascii"))
        except (UnicodeError, ValueError) as exc:
            raise CorpusError(f"invalid hex fixture: {case['id']}") from exc
    else:
        try:
            raw.decode("utf-8", errors="strict")
        except UnicodeError as exc:
            raise CorpusError(f"invalid UTF-8 text fixture: {case['id']}") from exc
        data = raw
    if not data or len(data) > MAX_INPUT or sha256(data) != case["program_sha256"]:
        raise CorpusError(f"invalid program bytes/hash: {case['id']}")
    return data


def load_corpus(root: Path, manifest: str = MANIFEST) -> dict[str, Any]:
    try:
        doc = json.loads(repository_file(root, manifest).read_text("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise CorpusError("manifest is not UTF-8 JSON") from exc
    if not isinstance(doc, dict) or doc.get("schema") != 1:
        raise CorpusError("unsupported corpus schema")
    pins = doc.get("input_git_blobs")
    if not isinstance(pins, dict) or not pins:
        raise CorpusError("input source pins are required")
    for name, value in pins.items():
        if not isinstance(name, str) or not isinstance(value, str) or not HEX40.fullmatch(value):
            raise CorpusError("invalid source pin")
    cases = doc.get("cases")
    if not isinstance(cases, list) or len(cases) < len(CATEGORIES):
        raise CorpusError("all six negative categories must have cases")
    seen: set[str] = set()
    categories: set[str] = set()
    for case in cases:
        if not isinstance(case, dict):
            raise CorpusError("each case must be an object")
        required = ("id", "category", "source", "encoding", "file_sha256", "program_sha256",
                    "expected_exit", "diagnostic", "provenance", "native_status", "language")
        if any(key not in case for key in required):
            raise CorpusError("incomplete case")
        ident = case["id"]
        if not isinstance(ident, str) or not re.fullmatch(r"[a-z][a-z0-9_]{0,63}", ident) or ident in seen:
            raise CorpusError("invalid/duplicate case id")
        seen.add(ident)
        if case["category"] not in CATEGORIES or case["encoding"] not in ("utf8", "hex"):
            raise CorpusError("invalid category/encoding")
        categories.add(case["category"])
        if case["expected_exit"] != 1 or isinstance(case["expected_exit"], bool):
            raise CorpusError("rejection contract requires exit 1, not any nonzero exit")
        if case["language"] not in (None, "sanskrit"):
            raise CorpusError("unreviewed language option")
        if case["native_status"] != "pending_current_run":
            raise CorpusError("manifest must not encode an unobserved native pass")
        if not all(isinstance(case[k], str) and HEX64.fullmatch(case[k])
                   for k in ("file_sha256", "program_sha256")):
            raise CorpusError("invalid fixture digest")
        diag = case["diagnostic"]
        if not isinstance(diag, dict) or diag.get("stream") != "stdout":
            raise CorpusError("diagnostic stream must be explicit")
        if diag.get("match") == "exact":
            if not isinstance(diag.get("text"), str) or not diag["text"] or not diag["text"].endswith("\n"):
                raise CorpusError("exact diagnostic must be nonempty and LF-terminated")
        elif diag.get("match") == "ordered_fragments":
            fragments = diag.get("fragments")
            if not isinstance(fragments, list) or len(fragments) < 2 or any(not isinstance(x, str) or not x for x in fragments):
                raise CorpusError("diagnostic fragments must be nonempty and specific")
        else:
            raise CorpusError("unknown diagnostic matcher")
        read_case(root, case)
    if categories != CATEGORIES:
        raise CorpusError("incomplete category coverage")
    return doc


def verify_source_pins(root: Path, pins: dict[str, str]) -> None:
    for relative, expected in pins.items():
        actual = git_blob(repository_file(root, relative).read_bytes())
        if actual != expected:
            raise CorpusError(f"source drift: {relative}: expected {expected}, got {actual}")


def clean_environment() -> dict[str, str]:
    # Explicit --lang is the only pack selector for this corpus. Do not inherit
    # experimental/check-mode variables from another test session.
    return {k: v for k, v in os.environ.items() if not k.upper().startswith("SUTRAM_")}


def invoke(argv: list[str], root: Path, timeout: float) -> subprocess.CompletedProcess[bytes]:
    completed = subprocess.run(argv, cwd=root, env=clean_environment(), stdin=subprocess.DEVNULL,
                               capture_output=True, timeout=timeout, check=False)
    if len(completed.stdout) > MAX_LOG or len(completed.stderr) > MAX_LOG:
        raise CorpusError("compiler/process produced excessive output")
    return completed


def diagnostic_matches(diag: dict[str, Any], output: bytes, source: Path) -> bool:
    def expand(text: str) -> bytes:
        return text.replace("{source}", str(source)).encode("utf-8")
    if diag["match"] == "exact":
        return output == expand(diag["text"])
    offset = 0
    for fragment in diag["fragments"]:
        needle = expand(fragment)
        found = output.find(needle, offset)
        if found < 0:
            return False
        offset = found + len(needle)
    return True


def assess_rejection(case: dict[str, Any], completed: subprocess.CompletedProcess[bytes],
                     source: Path, output: Path) -> list[str]:
    problems = []
    if completed.returncode != case["expected_exit"]:
        problems.append(f"expected exit 1, observed {completed.returncode}; crash/acceptance is not rejection")
    if os.path.lexists(output):
        problems.append("rejected compilation left an output path (including dangling symlink)")
    if completed.stderr != b"":
        problems.append("unexpected stderr; diagnostic contract is stdout-only")
    if not diagnostic_matches(case["diagnostic"], completed.stdout, source):
        problems.append("diagnostic contract did not match")
    return problems


def positive_control(compiler: Path, root: Path, directory: Path,
                     timeout: float, language: str | None) -> dict[str, Any]:
    label = language or "default"
    source = directory / f"positive_{label}.sm"
    output = directory / f"positive_{label}.bin"
    source.write_bytes(b"mukhya() {\n    likha(42)\n}\n")
    command = [str(compiler)] + (["--lang", language] if language else []) + [str(source), str(output)]
    built = invoke(command, root, timeout)
    if built.returncode != 0 or not output.is_file() or output.is_symlink():
        raise CorpusError(f"positive control failed tak compile ({label})")
    mode = output.stat().st_mode
    data = output.read_bytes()
    if not stat.S_ISREG(mode) or len(data) < 120 or data[:4] != b"\x7fELF":
        raise CorpusError(f"positive control did not create a Linux ELF executable ({label})")
    # Deliberately no chmod: a compiler that failed tak set execution permissions
    # must not be silently repaired by the acceptance runner.
    ran = invoke([str(output)], root, timeout)
    if ran.returncode != 0 or ran.stdout != b"42\n" or ran.stderr:
        raise CorpusError(f"positive control execution failed ({label})")
    return {"language": label, "status": "PASS", "binary_sha256": sha256(data)}


def run_corpus(compiler: Path, root: Path, doc: dict[str, Any], timeout: float) -> dict[str, Any]:
    report: dict[str, Any] = {"mode": "native", "compiler": str(compiler),
                              "compiler_sha256": sha256(compiler.read_bytes()),
                              "source_git_blobs": doc["input_git_blobs"],
                              "binary_source_correspondence": "reported pins are not proof of binary build provenance",
                              "positive_controls": [], "cases": []}
    verify_source_pins(root, doc["input_git_blobs"])
    with tempfile.TemporaryDirectory(prefix="sutram-r70-") as name:
        work = Path(name)
        languages = [None] + sorted({c["language"] for c in doc["cases"] if c["language"]})
        for language in languages:
            report["positive_controls"].append(positive_control(compiler, root, work, timeout, language))
        for case in doc["cases"]:
            source = work / f"{case['id']}.sm"
            output = work / f"{case['id']}.bin"
            source.write_bytes(read_case(root, case))
            if os.path.lexists(output):
                raise CorpusError("fresh temporary output unexpectedly exists")
            args = [str(compiler)]
            if case["language"]:
                args += ["--lang", case["language"]]
            args += [str(source), str(output)]
            row = {"id": case["id"], "category": case["category"], "source": str(source),
                   "program_sha256": case["program_sha256"], "provenance": case["provenance"]}
            try:
                completed = invoke(args, root, timeout)
                errors = assess_rejection(case, completed, source, output)
                row.update(exit=completed.returncode, stdout=completed.stdout.decode("utf-8", "backslashreplace"),
                           stderr=completed.stderr.decode("utf-8", "backslashreplace"), problems=errors)
            except (OSError, subprocess.TimeoutExpired, CorpusError) as exc:
                errors = [str(exc)]
                row.update(exit=None, problems=errors)
            row["status"] = "FAIL" if errors else "PASS"
            report["cases"].append(row)
            # Never run a negative case's generated output, even on exit 0.
    report["passed"] = sum(r["status"] == "PASS" for r in report["cases"])
    report["failed"] = len(report["cases"]) - report["passed"]
    report["native_status"] = "PASS" if report["failed"] == 0 else "FAIL"
    return report


def write_report(path: Path, data: dict[str, Any]) -> None:
    # O_EXCL refuses overwriting existing files and dangling symlinks.
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--manifest", default=MANIFEST)
    parser.add_argument("--compiler", type=Path)
    parser.add_argument("--compiler-sha256")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--timeout", type=float, default=12)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)
    if not math.isfinite(args.timeout) or not 0 < args.timeout <= 60:
        parser.error("timeout must be finite and between 0 and 60 seconds")
    if args.report and os.path.lexists(args.report):
        parser.error("report already exists; use a fresh output path")
    root = args.root.resolve()
    try:
        doc = load_corpus(root, args.manifest)
        if args.validate_only:
            result = {"mode": "validate-only", "validated_cases": len(doc["cases"]),
                      "categories": sorted(CATEGORIES), "native_status": "NOT_RUN",
                      "production_source_pins": "NOT_CHECKED", "compiler_executed": False}
            code = 0
        else:
            if args.compiler is None:
                raise CorpusError("--compiler is required for native acceptance")
            if args.compiler.is_symlink() or not args.compiler.is_file():
                raise CorpusError("compiler must be an explicit regular file, not a symlink")
            compiler = args.compiler.resolve()
            if args.compiler_sha256 is not None:
                if not HEX64.fullmatch(args.compiler_sha256) or sha256(compiler.read_bytes()) != args.compiler_sha256:
                    raise CorpusError("compiler binary hash mismatch")
            result = run_corpus(compiler, root, doc, args.timeout)
            code = 1 if result["failed"] else 0
    except (CorpusError, OSError, subprocess.TimeoutExpired) as exc:
        result = {"native_status": "NOT_ACCEPTED", "error": str(exc)}
        code = 2
    if args.report:
        write_report(args.report, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
