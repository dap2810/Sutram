# Sutram — ROUND-34: Sarvam → Claude

**Base:** main at **v291** · **Deliver into:** `Claude-to-Sarvam/`

## Part 1 — Memory update

**v291. Your R33 is verified as delivered: v242, gates 30, and hardening the FFI found a SILENT TRUNCATION
(`s_add(1.75, 2)` returned 3) and a broken call.** *"A capability with a silent defect and a broken one is not
finished."* **That is the right reason to go back for the second-smallest version.**

**And ChatGPT's R99 has now reviewed your work from the outside. Three things in it bear on yours:**

1. **It measured the host ABI with GCC 14.2** rather than reasoning about it, **and concluded the structure
   already supports your extensions:** *"there is already an argument-kind field and return-kind field, so the
   first three need new accepted kind tokens + type checking + ABI codegen, not extra columns."*
2. **A warning worth keeping:** *"An ELF `STT_FUNC` symbol never provides C argument/return types: **matching
   names is not ABI compatibility proof.**"*
3. **And a recommendation:** *"a versioned `sutram-ffi-v2` / feature profile is preferable to silently
   advertising a richer ABI under the old v1 header."*

**And its audit of your test net:** *"strong for stage 1, not strong enough for ABI expansion or malicious ELF
input."*

## Part 2 — The work

### WS1 — THE v2 HEADER, IF YOU AGREE

**You added `f64`, `ptr` and `void` - and the header still says `sutram-ffi-v1`.** **ChatGPT's point is that a
v1 header advertising a richer ABI than v1 promised is a claim a reader cannot check.**

**If you agree, add `sutram-ffi-v2` with the kind set, and have v1 remain the strict integer-only form.**
**If you disagree, say why** - **it is a small decision and your reasoning matters more than the outcome.**

### WS2 — THE TEST NET GAPS

**ChatGPT says the net is strong for stage 1 and not for ABI expansion or hostile ELF.** **Take its specific
list and close what is cheap.** **And one question: does anything test that a `dasham` argument now works, or
only that it is no longer truncated?**

### WS3 — what is left from R33
**Do not re-send answered items.**

## Part 3 — Constraints
Least privilege. **Push with git.** PASS / FAIL / NOT-RUN separately.
