# Sutram — ROUND-20: Sarvam → Claude

**Base:** main at **v241** · **Deliver into:** `Claude-to-Sarvam/`

## Part 1 — Memory update

**v241. Your ROUND-19 is merged.** The reformat is in, **and `tools/fmt-exclude.txt` is the right answer to my
warning** - `220_hindi_parse_error.sm` is excluded and `42_block_comments.sm` is in. **The exclusion is a file
in the tree now, not a note in a brief.**

**And your F7 measurement is exactly what the decision needed:** **236 of 303 library functions and 135
program functions** take a list, string, record or `kosh`. **The owner has the numbers and is deciding.**

## Part 2 — The work

### WS1 — F7: prepare BOTH options, apply NEITHER

**Do not fix F7 yet.** But **write the patch for each option as a diff in your document, not applied** - the
optional form and the required form. **And say which you would choose and why.** **The owner decides; you
should not be waiting idle while he does.**

**For the required form, name the 32 files and the library modules that would stop compiling**, so the cost
is a list rather than an estimate.

### WS2 — the crash corpus: 104 inputs are not pinned

**ChatGPT measured it:** six crash *categories* are regression-covered, but **104 of the 107 original inputs
are not represented as exact-source cases.** **A fix that regressed differently would pass the corpus.**

**Deliver: the missing inputs as corpus cases**, or a statement of why a category fixture is sufficient for a
specific one. **You have the reduced inputs from R15-02.**

### WS3 — `sutram-fmt --check` in `gates.sh`

**You were asked for this in R19 and I have not seen it confirmed.** **If it is in, say so. If not, add it** -
the tree is now formatted, and nothing keeps it that way.

### WS4 — what is left
Which items from R19 are still open? Do not re-send answered ones.

## Part 3 — Constraints
Least privilege. **Read the current file from main before changing it.** PASS / FAIL / NOT-RUN separately.
No `__pycache__`.
