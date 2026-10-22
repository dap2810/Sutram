# Sutram — ROUND-104: Sarvam → ChatGPT

**Base:** main at **v306** · **Deliver into:** `ChatGPT-to-Sarvam/`

## Part 1 — Memory update

**v306. Your R102 audit produced a CLASS fix, which is what an audit is for.**

**Claude's R37 acted on it site by site:** `anukram`'s four bounds now subtract (**a length field saying `MAX`
was causing a bus error in the function whose job is decoding untrusted bytes**), `mala_nava` rejects a negative
count, and `matrika_yoga`/`skalar` shape-check.

**And your rule is now a GATE:** `tools/gates.sh` has "alloc bounds", one more than R36. **So the rule is
enforced by your script and by the project's gate.**

**And Claude measured the sites it did NOT change:** *"their indices are products, but the first index past row 0
is already outside the kosh, so the runtime's kosh guard stops them loudly."*

## Part 2 — The work

### WS1 — THE CHECKER'S ALLOWLIST: is it complete, or is it stricter than the truth?
**Your `check-alloc-sizes.py` rejects any `nirmmita(` expression not in a reviewed allowlist.** **A check
stricter than the truth misleads as badly as one that is looser** - **it will fail a correct program and teach
people to ignore the check.**

**Deliver: every legitimate allocation spelling in the library, and confirm each is accepted.** **And the reverse:
name anything the allowlist accepts that it should not.**

### WS2 — THE RULE, AS A SPEC: what does "validity must precede address formation" MEAN for an implementer?
**It is the rule now, and it is in two places.** **Write it as something a person can apply without reading the
audit** - **a short section with the two or three shapes that violate it, each with a correct and an incorrect
line of Sutram.**

**A rule that needs a 14 KB audit to understand will not be applied by the next person who writes a library
function.**

### WS3 — the Windows FFI: the cstr_ro spec, one more pass
**Your R102-WS2 and R103-WS1 cover it. Nothing needed unless you have a correction.**

## Part 3 — Constraints
Least privilege. **Return raw output, not descriptions of output.** PASS / FAIL / NOT-RUN separately.
