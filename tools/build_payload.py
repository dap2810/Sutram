#!/usr/bin/env python3
"""Build the installer payload: a staging tree + integrity manifest + zip."""
import os, shutil, hashlib, zipfile, sys

WORK = "/scratch/work"
STAGE = "/tmp/payload"
OUT = "/tmp/payload.zip"

# Whole cleaned project tree, minus things an end user should not receive.
EXCLUDE_DIRS = {"nasm", ".git", "__pycache__", ".backup", "ret", "inbox", "downloads"}
EXCLUDE_FILES = {"HANDOFF-SARVAM-TO-CHATGPT.md", "INSTRUCTION-CHATGPT.md"}
EXCLUDE_EXT = {".zip", ".o", ".obj", ".exe", ".ico"}   # .ico re-added explicitly below

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

def main():
    if os.path.exists(STAGE):
        shutil.rmtree(STAGE)
    os.makedirs(STAGE)

    # 1. Copy the cleaned project tree.
    for root, dirs, files in os.walk(WORK):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        rel_root = os.path.relpath(root, WORK)
        if rel_root == ".":
            rel_root = ""
        for name in files:
            src = os.path.join(root, name)
            rel = os.path.join(rel_root, name) if rel_root else name
            if os.path.splitext(name)[1] in EXCLUDE_EXT:
                continue
            if name in EXCLUDE_FILES:
                continue
            dst = os.path.join(STAGE, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)

    # 2. The three files the installer hard-requires.
    os.makedirs(os.path.join(STAGE, "bin"), exist_ok=True)
    os.makedirs(os.path.join(STAGE, "win"), exist_ok=True)
    shutil.copy2(f"{WORK}/win/sutram.exe", f"{STAGE}/bin/sutram.exe")
    shutil.copy2(f"{WORK}/win/sutram.exe", f"{STAGE}/win/sutram.exe")
    shutil.copy2(f"{WORK}/windows/gui/sutram-ide-gui.exe", f"{STAGE}/sutram-ide-gui.exe")

    # 3. Icon and licence the install script expects.
    os.makedirs(os.path.join(STAGE, "icons"), exist_ok=True)
    shutil.copy2(f"{WORK}/icons/sutram.ico", f"{STAGE}/icons/sutram.ico")
    if os.path.exists(f"{WORK}/windows/LICENSE.txt"):
        shutil.copy2(f"{WORK}/windows/LICENSE.txt", f"{STAGE}/LICENSE.txt")

    # 4. Manifest — every file except the manifest itself.
    manifest_rel = "payload.manifest.sha256"
    rows = []
    for root, dirs, files in os.walk(STAGE):
        for name in sorted(files):
            full = os.path.join(root, name)
            rel = os.path.relpath(full, STAGE).replace("/", "\\")
            if rel == manifest_rel:
                continue
            rows.append(f"{sha256(full)} *{rel}")
    rows.sort(key=lambda r: r.split("*", 1)[1])
    with open(os.path.join(STAGE, manifest_rel), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(rows) + "\n")

    # 5. Zip it (deterministic order, forward slashes as the zip spec requires).
    if os.path.exists(OUT):
        os.remove(OUT)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        allfiles = []
        for root, dirs, files in os.walk(STAGE):
            for name in files:
                full = os.path.join(root, name)
                allfiles.append(os.path.relpath(full, STAGE))
        for rel in sorted(allfiles):
            z.write(os.path.join(STAGE, rel), rel.replace(os.sep, "/"))

    print(f"payload files : {len(rows) + 1}")
    print(f"payload.zip   : {os.path.getsize(OUT)} B")
    for probe in ["bin\\sutram.exe", "sutram-ide-gui.exe", "win\\sutram.exe"]:
        p = os.path.join(STAGE, probe.replace("\\", os.sep))
        print(f"  {probe:24} {'OK' if os.path.exists(p) else 'MISSING'}")

if __name__ == "__main__":
    main()
