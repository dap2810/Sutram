#!/usr/bin/env python3
"""R72 reproducible release gate; offline, clean-checkout builds only.

No goldens are updated, no CI is invoked, and no source checkout is edited.
The selected compiler must be built twice from the same pinned commit.
Only a real successful run may produce a binary hash or native PASS.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tools" / "r72_release_manifest.json"

def git(*args: str, cwd: Path = ROOT) -> str:
    r = subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True,
                       timeout=45, check=False)
    if r.returncode:
        raise RuntimeError("git " + " ".join(args) + ": " + r.stderr[:2000])
    return r.stdout.strip()

def source_check(root: Path, manifest: dict) -> dict:
    pins = manifest["inputs"]
    assert manifest["entry"] == "src/r68_compiler_entry.asm"
    if not pins or "src/sutram_compiler.asm" not in pins:
        raise ValueError("empty release input manifest")
    observed = {}
    for rel, expected in sorted(pins.items()):
        if not re.fullmatch(r"[0-9a-f]{40}", expected):
            raise ValueError("invalid input SHA: " + rel)
        p = root / rel
        if p.is_symlink() or not p.is_file():
            raise ValueError("unsafe/missing source: " + rel)
        data = p.read_bytes()
        actual = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        if actual != expected:
            raise ValueError("source drift: " + rel + " expected=" + expected + " got=" + actual)
        observed[rel] = {"git_blob": actual, "sha256": hashlib.sha256(data).hexdigest(),
                         "bytes": len(data)}
        for match in re.finditer(rb"^\s*%(?:include|incbin)\s+([^\r\n;]+)", data, re.M):
            token = match.group(1).strip()
            if len(token) < 3 or token[:1] not in (b'"', b"'") or token[-1:] != token[:1]:
                raise ValueError("dynamic include needs review: " + rel)
            child = token[1:-1].decode("ascii")
            if child not in pins:
                raise ValueError("unlocked include: " + rel + " -> " + child)
    return observed

def run(cmd: list[str], root: Path, timeout: int, env: dict | None = None) -> dict:
    try:
        p = subprocess.run(cmd, cwd=root, stdin=subprocess.DEVNULL,
                           capture_output=True, timeout=timeout, check=False, env=env)
        if len(p.stdout) + len(p.stderr) > 1000000:
            return {"status": "FAIL", "reason": "output exceeds evidence bound",
                    "exit": p.returncode}
        out, err = p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")
        return {"status": "PASS" if p.returncode == 0 else "FAIL",
                "exit": p.returncode, "stdout": out, "stderr": err,
                "no_expectation": sum(int(n) for n in re.findall(
                    r"\bNO[- ]EXPECTATION(?:S)?\s*[:=]\s*(\d+)", out, re.I))}
    except subprocess.TimeoutExpired as e:
        return {"status": "FAIL", "reason": "TIMEOUT", "seconds": timeout}
    except OSError as e:
        return {"status": "FAIL", "reason": type(e).__name__ + ": " + str(e)}

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=("default", "mukti"), default="default")
    ap.add_argument("--source-only", action="store_true")
    ap.add_argument("--report", type=Path, required=True)
    ns = ap.parse_args()
    if os.path.lexists(ns.report):
        ap.error("report already exists: use a fresh file")
    if not ns.report.parent.is_dir() or ns.report.parent.is_symlink():
        ap.error("report directory missing or symlink")
    data = json.loads(MANIFEST.read_text("utf-8"))
    report = {
        "kind": "SUTRAM_R72_CLEAN_CHECKOUT_GATE", "requested_mode": ns.mode,
        "host": platform.platform(), "target": "linux-x86_64",
        "input_base": data["base_main_commit"], "source_ref": "",
        "input_observed": {}, "builds": [], "gates": {},
        "binary_sha256": None, "reproducibility": "NOT_RUN",
        "native_status": "NOT_RUN", "counts": {
            "PASS": 0, "FAIL": 0, "SKIP": 0, "NO_EXPECTATION": 0, "NOT_RUN": 0}
    }
    failure = False
    try:
        if git("status", "--porcelain"):
            raise ValueError("checkout not clean; commit or isolate first")
        head = git("rev-parse", "HEAD")
        git("merge-base", "--is-ancestor", data["base_main_commit"], head)
        report["source_ref"] = head
        report["input_observed"] = source_check(ROOT, data)
        if ns.source_only:
            report["reproducibility"] = "NOT_RUN"
        else:
            with tempfile.TemporaryDirectory(prefix="sutram-r72-clean-") as tmp:
                copies = [Path(tmp) / ("nirmana" + str(i)) for i in range(2)]
                binaries = []
                for clone in copies:
                    c = run(["git", "clone", "--quiet", "--local", "--no-hardlinks",
                             str(ROOT), str(clone)], ROOT, 90)
                    if c["status"] != "PASS":
                        raise RuntimeError("clean clone failed: " + str(c))
                    git("checkout", "--quiet", "--detach", head, cwd=clone)
                    if source_check(clone, data) != report["input_observed"]:
                        raise ValueError("clone input source mismatch")
                    build = run([sys.executable, "tools/r69_build.py", "--mode", ns.mode,
                                 "--target", "linux", "--output", "sutram_compiler",
                                 "--report", "r72-build.json"], clone, 180)
                    report["builds"].append(build)
                    if build["status"] != "PASS":
                        raise RuntimeError("reproducible build failed")
                    compiler = clone / "sutram_compiler"
                    payload = compiler.read_bytes()
                    if not payload.startswith(b"\x7fELF\x02\x01\x01"):
                        raise ValueError("not ELF64 compiler")
                    binaries.append(hashlib.sha256(payload).hexdigest())
                report["binary_sha256"] = binaries[0]
                if binaries[0] != binaries[1]:
                    raise ValueError("two clean compiler binaries differ")
                report["reproducibility"] = "PASS"
                env = {k: v for k, v in os.environ.items()
                       if not k.upper().startswith("SUTRAM_")}
                env["SUTRAM_COMPILER"] = str(copies[0] / "sutram_compiler")
                commands = {
                    "suite": [sys.executable, "tests/run_tests.py"],
                    "codegen": [sys.executable, "tools/codegen_gate.py"],
                    "packs": [sys.executable, "tools/test_lang_packs.py"],
                    "library": [sys.executable, "tools/proof_lib.py", "--compiler",
                                env["SUTRAM_COMPILER"]],
                    "properties": [sys.executable, "tools/proof_props.py", "--compiler",
                                   env["SUTRAM_COMPILER"]],
                    "layers": [sys.executable, "tools/check_layers.py"],
                    "module_graph": [sys.executable, "-m", "unittest", "discover",
                                     "-s", "tests/module_graph", "-p", "test_*.py", "-v"],
                    "negatives": [sys.executable, "tools/r70_negative_corpus.py",
                                  "--compiler", env["SUTRAM_COMPILER"],
                                  "--report", str(copies[0]/"r72-negatives.json")]
                }
                if ns.mode == "mukti":
                    legacy = copies[1] / "sutram-legacy"
                    base = run([sys.executable, "tools/r69_build.py", "--mode",
                                "default", "--target", "linux", "--output",
                                str(legacy)], copies[1], 180)
                    report["builds"].append(base)
                    if base["status"] != "PASS":
                        raise RuntimeError("control compiler build failed")
                    commands["kosh_mukti"] = [
                        sys.executable, "tools/r72_kosh_acceptance.py",
                        "--compiler", env["SUTRAM_COMPILER"], "--legacy", str(legacy),
                        "--report", str(copies[0]/"r72-kosh-native.json")]
                for name, cmd in commands.items():
                    res = run(cmd, copies[0], 240, env=env)
                    report["gates"][name] = res
                    if res["status"] != "PASS":
                        failure = True
                report["native_status"] = "FAIL" if failure else "PASS"
    except (OSError, ValueError, RuntimeError, KeyError, json.JSONDecodeError) as exc:
        report["fatal"] = str(exc)
        failure = True
    for r in report["gates"].values():
        report["counts"][r.get("status", "NOT_RUN")] += 1
        report["counts"]["NO_EXPECTATION"] += r.get("no_expectation", 0)
    if ns.source_only:
        report["counts"]["NOT_RUN"] = 8 if ns.mode == "default" else 9
    elif not report["gates"]:
        report["counts"]["NOT_RUN"] = 8 if ns.mode == "default" else 9
    if failure:
        report["counts"]["FAIL"] += 1 if not report["gates"] else 0
    with ns.report.open("x", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        f.write("\n")
    print(json.dumps({"native_status": report["native_status"],
                      "reproducibility": report["reproducibility"],
                      "binary_sha256": report["binary_sha256"],
                      "counts": report["counts"]}, indent=2))
    return 1 if failure else 0

if __name__ == "__main__":
    raise SystemExit(main())
