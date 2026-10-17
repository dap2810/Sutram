#!/usr/bin/env python3
"""Push the Sutram tree to GitHub in bounded batches, tracking progress on disk.

Usage: python3 tools/push_to_github.py <batch_index> <batch_size>

Progress is appended to /scratch/work/.gh-pushed so a later batch skips files
already uploaded and a timeout never loses track.
"""
import asyncio, os, sys, json
from sarvam_tools import GITHUB_CREATE_OR_UPDATE_FILE_CONTENTS, ToolError

OWNER, REPO = "dap2810", "Sutram"
ROOT = "/scratch/work"
STATE = os.path.join(ROOT, ".gh-pushed")

INCLUDE_DIRS = ["src", "lib", "lang", "examples", "tools", "ide", "windows", "docs", "compiler"]
EXTRA = ["ROADMAP.md", "LICENSE.txt", "INSTALL-WINDOWS.md", "PROJECT-OVERVIEW.md", "README.md"]
SKIP_PARTS = {"tests/expect", "benchmarks", "nasm", "__pycache__", ".backup", ".oldicons",
              "ret", "inbox", "downloads", ".git", "payload.manifest.sha256"}
SKIP_EXT = {".o", ".obj", ".zip", ".exe"}


def collect():
    out = []
    for d in INCLUDE_DIRS:
        base = os.path.join(ROOT, d)
        if not os.path.isdir(base):
            continue
        for root, dirs, files in os.walk(base):
            dirs[:] = [x for x in dirs if x != "__pycache__"]
            for f in files:
                rel = os.path.relpath(os.path.join(root, f), ROOT)
                if any(p in rel for p in SKIP_PARTS):
                    continue
                if os.path.splitext(f)[1] in SKIP_EXT:
                    continue
                out.append(rel)
    for f in EXTRA:
        if os.path.isfile(os.path.join(ROOT, f)):
            out.append(f)
    return sorted(set(out))


def load_done():
    if not os.path.exists(STATE):
        return set()
    return set(json.load(open(STATE)))


def save_done(done):
    json.dump(sorted(done), open(STATE, "w"))


async def main():
    idx = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    size = int(sys.argv[2]) if len(sys.argv) > 2 else 100

    all_files = collect()
    done = load_done()
    todo = [f for f in all_files if f not in done]
    batch = todo[idx * size:(idx + 1) * size]
    print(f"total={len(all_files)} already={len(done)} todo={len(todo)} batch={len(batch)}")

    sem = asyncio.Semaphore(8)
    lock = asyncio.Lock()
    ok = 0
    fail = []

    async def put(rel):
        nonlocal ok
        async with sem:
            try:
                content = open(os.path.join(ROOT, rel), encoding="utf-8").read()
            except (UnicodeDecodeError, OSError):
                return
            for attempt in range(2):
                try:
                    await GITHUB_CREATE_OR_UPDATE_FILE_CONTENTS(
                        owner=OWNER, repo=REPO, path=rel.replace(os.sep, "/"),
                        message=f"add {rel}", content=content)
                    async with lock:
                        ok += 1
                        done.add(rel)
                    return
                except ToolError as e:
                    if attempt == 1:
                        fail.append((rel, str(e)[:70]))

    for i in range(0, len(batch), 40):
        await asyncio.gather(*[put(p) for p in batch[i:i + 40]])
        save_done(done)
        print(f"  {min(i+40, len(batch))}/{len(batch)}  ok={ok} fail={len(fail)}")

    save_done(done)
    print(f"\nBATCH DONE: uploaded {ok}, failed {len(fail)}")
    for r, e in fail[:8]:
        print("  FAIL", r, e)


asyncio.run(main())
