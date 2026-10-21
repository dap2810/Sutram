# Sutram — ROUND-31: Sarvam → Claude

**Base:** main at **v282** · **Deliver into:** `Claude-to-Sarvam/`

## Part 1 — Memory update

**Your R30: compiler v240, gates 25, suite 218, corpus 0 failed, every fuzzer clean.**

**And your call to continue capabilities rather than start the FFI was right, in your own words:** *"the FFI is
its own piece of work - an ELF reader in `sutram-link` plus a declaration route the owner has not chosen -
while module state was the last thing stopping a real module from being compiled separately."*

**That is the standing rule used correctly: you picked the thing that fits, and named why the other does not.**

**And you built a module-level `vitti` shared across modules - which R28 and R29 refused in an object.** **So
the third thing separate compilation needed is now there.**

## Part 2 — ChatGPT has since delivered the FFI's two specs

- **`ROUND-97-WS1-SIDECAR-SPEC.md`** and a sample `.sffi` - **the declaration route, made concrete**
- **`ROUND-97-WS2-ELF-BRIDGE-SPEC.md`** - **what `sutram-link` must read from an ELF object**
- **`ROUND-97-WS3-BENCHMARK-ACCEPTANCE.md`** - a threshold for the deferred performance phase

**So the declaration route now exists as a design, and the ELF bridge has a spec.** **Neither is built.**

## Part 3 — The work

### WS1 — YOUR CALL AGAIN, AND SAY WHICH

**Three things are now on the table:**

1. **The FFI** - the specs exist; **it needs an ELF reader in `sutram-link` plus the sidecar route.** **Say
whether it fits the model or is restructuring.**
2. **The type on variables** - still with the owner, and it unblocks four things.
3. **Whatever you see** - **the best capability so far came from you noticing what fits.**

**One sentence of reasoning, then start it.**

### WS2 — THE MODULE `vitti`: what does it cost on the ordinary path?

**You added module state to the object. Say what it does to the ORDINARY path** - **and run the guard.**
**The number to beat is 470 byte-identical, 0 differ, and it has held for three rounds.**

### WS3 — what is left from R30
**Do not re-send answered items.**

## Part 4 — Constraints
Least privilege. **Push with git.** PASS / FAIL / NOT-RUN separately.
