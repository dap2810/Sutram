# R31-01 — Incremental rebuilds: `tools/sutram_build.py --cache DIR`

## What it does

**Without `--cache`, nothing changes:** every module is compiled, as in R29. **With it,** each module's object is
looked up in `DIR` under a key, reused when it is there, and compiled and stored when it is not.

## The key: everything an object depends on, and nothing else

A module's `--separate` object is a function of exactly these, so they are hashed (SHA-256) in this order:

1. **the compiler's bytes** (a new compiler can emit different code);
2. **`SUTRAM_LANG`** (it changes which words are keywords);
3. **the module's path and bytes;**
4. **the path and bytes of every module it reaches through `yoj`**, sorted. In `--separate` they are parsed for
   their signatures (R29), so a change in one of them can change this object. **A module that is not reachable
   from it is not in its key**, which is what makes reuse possible.

The graph is recomputed on every build, so a module that appears, disappears or moves changes the paths in the
keys. An object is written to a temporary name and renamed into place, so **a half-written object is never
under its key.**

## Why a cached build is exactly a clean build

**The objects are reproducible:** the same inputs give the same bytes. So reusing an object is the same as
compiling it again, and **a cached build links to the same executable as a clean one, byte for byte.** That is
the claim the test checks, for every program, rather than assumes.

## The proof: `tests/r31/test_incremental.py`, now a gate (Linux)

| What | Result |
|---|---|
| **The same executable.** Every program that `yoj`s a module (plain `yoj`; it compiles the ordinary way), built without a cache, with a cold cache and with the warm cache | **254 of 254 byte-identical all three ways**; every warm build compiled nothing |
| **Shared across programs.** One cache for all 254 | 289 objects compiled, **363 reused**: a library module is compiled once for every program that uses it |
| **Only what changed.** In `tests/r29/proj`: edit `r29_vam` | **2 compiled** (it and the root), **2 reused** |
| edit the leaf `r29_mul` (everything reaches it) | **4 compiled** |
| each edited build vs a clean build | **byte-identical**; output `402 800 3.500000` |
| **The key.** A compiler one byte different; a different `SUTRAM_LANG` | **4 compiled** each time |

## Limits

- **No eviction:** old objects stay until the directory is deleted.
- **The cache trusts its own files:** a hand-edited object inside it is not detected. `sutram-link` still checks
  every object's format.
- **Linux only,** like `--separate`.
