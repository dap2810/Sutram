#!/usr/bin/env python3
"""Reverse-apply a single-file unified diff to reconstruct the pre-patch source."""
import sys

src_path, patch_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
src = open(src_path, encoding="utf-8").read().split("\n")
patch = open(patch_path, encoding="utf-8").read().split("\n")

# Collect hunks: (old_start, old_count, new_start, new_count, lines)
hunks = []
i = 0
while i < len(patch):
    line = patch[i]
    if line.startswith("@@"):
        head = line.split("@@")[1].strip()
        old = head.split(" ")[0]
        new = head.split(" ")[1]
        os_, oc = (int(x) if x else 1 for x in old.lstrip("-").split(","))
        ns, nc = (int(x) if x else 1 for x in new.lstrip("+").split(","))
        body = []
        i += 1
        while i < len(patch) and not patch[i].startswith("@@"):
            if patch[i][:1] in (" ", "+", "-") and patch[i] != "\\ No newline at end of file":
                body.append(patch[i])
            i += 1
        hunks.append((os_, oc, ns, nc, body))
    else:
        i += 1

# Reverse: apply from the bottom up so earlier offsets stay valid.
out = list(src)
for os_, oc, ns, nc, body in reversed(hunks):
    # In the forward diff, 'context' and '-' lines are the OLD content;
    # '+' lines are the NEW content. To reverse, replace the NEW block with
    # the OLD block at position ns.
    old_block = [l[1:] for l in body if l[:1] in (" ", "-")]
    new_block = [l[1:] for l in body if l[:1] in (" ", "+")]
    start = ns - 1
    seg = out[start:start + len(new_block)]
    if seg != new_block:
        print(f"WARNING: hunk at new line {ns} does not match expected content",
              file=sys.stderr)
    out[start:start + len(new_block)] = old_block

open(out_path, "w", encoding="utf-8").write("\n".join(out))
print(f"reverse-applied {len(hunks)} hunk(s) -> {out_path}")
