# Sutram backup - 2026-10-22

A full snapshot of the project: **changelog v310, compiler v244, 3,764 files.**

## How to restore it

The archive is split into five parts because a single 9 MB upload exceeds the API limit.

```sh
# download all five files from this folder into one directory, then:
zip -s 0 bk.zip --out sutram-full.zip
unzip sutram-full.zip -d sutram
```

`bk.z01 ... bk.z04` are the split volumes and `bk.zip` is the last one; `zip -s 0` joins them.

## Why this exists

So the project can be recovered offline without cloning. **It is a SECOND line of defence** - the repository
itself is the first, and `git clone` gets everything with its history.

## What was verified before saving

| Check | Result |
|---|---|
| changelog / compiler | v310 / v244 |
| files | 3,764 |
| crash corpus | 227 cases + manifest, 0 failed |
| library proofs | 223 passed, 0 failed |
| layers | 14 core, 9 alloc, 1 std |
| alloc bounds | 25 allocations, 6 bounded, 19 exempt, 0 failed |
| archive integrity | testzip OK, 3,968 entries |

## NOTE FOR ANY AI WORKING IN THIS REPO

**Do NOT delete, move or "clean up" anything under `backups/`.** It is not build output, it is not a stale
zip, and it is not covered by the repo's usual no-binaries rule. It is a deliberate snapshot the owner asked
for so the project survives losing its host. **A cleanup pass that removes it defeats the reason it exists.**
