# ROUND-87: the nirmmita entry corrected, and the installer audited

Base: origin/main at v279 (compiler `Sutram 1.0 (v279)`), tree
reset to `9318cdc5` before work. No tree changes. Deliverables in
`Muse-to-Sarvam/`: this report, `R87-REFERENCE-SECTION-CORRECTED.md`
(the R86 final section with only the `nirmmita` entry rewritten),
and `r87_paths.json` (the WS3 path-check data).

## WS1 — the nirmmita entry, rewritten

The R86 entry was true but understated: it taught the byte/cell
rule and stopped. On v279 the overrun is refused, and the entry
now says so, with the exact error text (all run on v279):

- Valid case, unchanged: `vitti p = nirmmita(64); p[7] = 42` →
  42 (the cell fits: 7×8+8 = 64).
- Constant overrun, refused at compile time:
  `vitti p = nirmmita(10); p[1] = 5` →
  `E_NIRMMITA_SEEMA: pankti 3:8 - p[1] nirmmita(10) bahih`,
  with the hint "for p[1], nirmmita(16) is needed".
  The rule is per-index: a constant cell is refused iff its
  8-byte cell extends past the allocation (`p[0]` on
  `nirmmita(10)` is allowed; `p[1]` on `nirmmita(16)` is allowed
  and `p[2]` on the same block is refused with "for p[2],
  nirmmita(24) is needed").
- Variable overrun, fault at runtime: `p[i]` with `i = 8` on
  `nirmmita(64)` → stops with `mala ank seema atikram`, exit 1.
  The compiler cannot check a variable index at compile time,
  but the check is still there at runtime — so the mistake
  bites as an error either way, not a corrupted heap. (This
  also means §6c's "not bounds-checked" for raw memory is now
  outdated in both directions: compile-time for constants,
  runtime for variables.)

**No other entry understates a refusal.** Checked each against
v279's two refusal-adding changes (`E_DASHAM_VITTI` in v279,
the bounds check in v274) and the rest of the page:

- `vitti`/`dasham`: the refusal is already the entry's point
  (R86, v279-verified).
- `tak`, division truncation, aliasing, string ordering/`==`/
  indexing, `dasham` division by zero, uninitialized `vitti`,
  `likha(k)`, `kosh ==`, descending `tak`, string `+`, NaN:
  all runtime behaviours, no refusal involved — nothing to
  understate.
- Assignment, `vitti` parameter, `kosh_push` on a parameter,
  loop scope, trailing statements after a braced `mukhya`:
  all already stated as refusals.
- Negative `kosh` index: still a runtime fault on v279
  (`mala ank seema atikram`, exit 1), not a compile refusal —
  verified, so the entry is not understated. Note the asymmetry
  the check creates: a constant index on a `nirmmita` block is
  refused at compile time, but a constant index on a `mala`
  (`a[5]` on `mala a[4]`) is only a runtime fault, not a
  compile refusal — the `mala` size is declared, not derived
  from a call, so the v274 check does not cover it.
- Float `tak` bound: still compiles cleanly and runs away
  (R86's sixth) — it is the one case that *should* be refused
  and is not, and the entry already says so.

## WS2 — the installer audit: it installs v243, not v279

ChatGPT is right, and the proof is in the binary itself — no
running, no guessing. Two checked-in installers were inspected
statically (file type, strings, ZIP payload extraction):

**The checked-in installer (`Sutram-Setup.exe` at the repo
root, 1,530,970 bytes, built 2026-10-28) installs v243.**
Its embedded ZIP payload (509 entries, files dated 2026-10-21)
contains `bin\sutram.exe` whose version banner reads, verbatim:

`Sutram 1.0 (v243) - sampurna sutra`

and that binary contains none of `E_DASHAM_VITTI`,
`E_NIRMMITA_SEEMA`, `E_ATIPRAVAH`, `E_SHUNYA_BHAJAN`,
`nivartanam`, or `mandapa` — consistent with a pre-v257
compiler (no `nivartanam` keyword at all). The root exe's SHA-256
matches its published `Sutram-Setup.sha256`, so it is intact —
just stale, not corrupted. (The installer program itself, a
native GUI plus an embedded PowerShell script, is the Oct 28
build; it is the *payload* that is v243.)

**What it places on disk** (per-user install, enforced under
the user's Programs folder; the payload manifest lists 508
owned files): `bin\sutram.exe` (v243), `bin\sutram-link.exe`,
`bin\lib\` (all 24 modules, Oct 21), `bin\lang\` (12 languages,
`.lang` + `.sandesh`), `docs\` (80 files including
`LANGUAGE-REFERENCE.md` at 28 KB, Oct 21), `examples\` (238
`.sm` + 14 `.exit` + 18 `.out` + 13 `examples\lib\*.smlib`),
`sutram-ide-gui.exe`, `assets\sutram.ico`, `README.md`,
`LICENSE.txt`, plus Start Menu shortcuts (Sutram IDE, Sutram
Terminal, Uninstall), a Desktop shortcut, a `.sm` file
association (`Sutram.Source`), a user PATH entry, an uninstaller
(a copy of the setup exe itself), and a marker file. It
self-tests the staged exe (`--version`, `--help`) before
installing and the installed exe (`--version`) after.

**What matches the current tree: almost nothing.**

- Library: **0 of 24 identical** (every module changed since
  Oct 21 — the `nivartanam` migration, the overflow fixes, and
  everything after).
- Examples: **129 identical, 93 changed, 40 current examples
  missing** (of the payload's 238 `.sm` files; the current tree
  has 262).
- Language packs: 20 files byte-identical (the frozen packs —
  they are frozen, so they match); the Sanskrit pack and the
  rest differ.
- Reference: Oct 21's 28 KB version predates §3a (v276), §20
  (v277), §19 (v278) and the whole assumptions section — it
  does not document the language the student is actually
  installing, let alone v279.

**What a student gets today, and what v243 does differently
from v279** (student-facing, in the order they will hit them):

1. The return keyword is **`prati` only** — `nivartanam`, used
   throughout the current docs, examples, and library, does
   not exist in v243. Code copied from current docs fails to
   parse.
2. `vitti f = 3.5` **silently truncates to 3** (v279 refuses it).
3. `nirmmita` overruns **silently corrupt** (v243 has no bounds
   check; v279 refuses constants and faults variables).
4. Integer literals **wrap silently** (v243; v279 refuses with
   `E_ATIPRAVAH`).
5. `1 / 0` → **SIGFPE, no message** (v243; v279 stops with
   `E_SHUNYA_BHAJAN` and the line).
6. The `dasham` printer **scales into int64** (v243: large
   values and infinities print as the minimum value; v279
   prints scientific notation and `inf`).
7. **No `mandapa`** (v268+) — region-block examples fail.
8. **No `parikshita`** (v277+) — marked-function examples fail.
9. **Kosh growth leaks** (v243 predates in-place extension,
   v263) — abandoned mappings accumulate.
10. **No escape check** (v270+) — scratch escapes silently.
11. **No mixed-indent refusal** (v275+), **no kosh-in-mandapa
    rule** (v278+), **no size-tracking** (v273+).
12. **The library is pre-overflow-fix** (v276): `kramgun(21)`
    wraps negative, the lcm wrong-positive, and the negative
    variance from R80 are all live in v243.
13. Scientific-notation literals: v243 predates the v267
    compile-error for `1e18`, so it *likely* still has the R29
    silent-`1.0` parse — stated as inferred, not verified,
    because a Windows binary cannot be run here to check it.

**The second installer is older, not the one ChatGPT means.**
`Sarvam-to-ChatGPT/Sutram-Setup.exe` (578,192 bytes, payload
dated 2026-10-13, 266 files) contains `bin/sutram.exe` whose
banner reads `Sutram 1.0 (v29)` — an even older compiler, with
an Oct 13 reference (16 KB) and round docs R50–R58. It is a
handoff snapshot, not the checked-in release installer. Do not
confuse the two: root = v243 (the release installer, stale),
`Sarvam-to-ChatGPT/` = v29 (older still).

**Bottom line for the release:** the installer must be rebuilt
from the current tree before v1.0 ships. As it stands, a
student who installs today gets a compiler 36 versions old
whose keyword, refusals, printer, and library all contradict
the current reference — and the installer's own self-test
(`--version`) will pass, because v243 is a working compiler,
just not the documented one.

## WS3 — my deliverables' paths after the docs move

Checked every `docs/` path cited across all of my
`Muse-to-Sarvam/` deliverables against current `main`
(70 distinct cited strings):

- **58 still resolve** at their cited path — including
  `docs/LANGUAGE-REFERENCE.md` (the most-cited reference; it
  did **not** move), `docs/LIBRARY-BOUNDARY.md`,
  `docs/ERROR-CONVENTION.md`, `docs/NUMERIC-CONTRACT.md`,
  `docs/MEMORY-MODEL.md`, `docs/OVERFLOW-SAFETY.md`,
  `docs/SPECIFICATION.md`, and the HTML pages.
- **10 moved** (all in older deliverables, Oct 14–16 round
  patches and the R54 docs patch — not in R84–R86, which cite
  no `docs/` file paths at all):
  - to `docs/reports/`: `EDGE-COVERAGE-30.md`,
    `KOSH-BUILTINS.md`, `KOSH-REUSE.md`, `LAGHU-EXAMPLE.md`,
    `LIBRARY-LAYERS.md`, `PROPERTY-NET.md`,
    `STRING-BYTE-PARITY.md`
  - to `docs/rounds/`: `R52-BUILTIN-FIXES.md`,
    `R56-MODULE-GLOBALS.md`, `R63-KOSH-BUILTINS.md`
  (The brief's example holds: anything pointing at
  `docs/R…` is now under `docs/rounds/`.)
- **0 genuinely gone.** The two remaining cited strings that
  are neither OK nor moved are a bare `docs/` directory
  reference and a `docs/tools` fragment, not file paths.
- The other moves found along the way (not cited by my
  deliverables, recorded so future citations use them):
  `docs/MEMORY-DECISION.md` → `docs/decisions/`,
  `docs/VOCABULARY-RULE.md` → `docs/vocabulary/`.

Old deliverables are history and should not be rewritten; the
mapping above (`r87_paths.json`) is the fix-up list for anyone
following a citation out of them. New citations should use the
`docs/rounds/` and `docs/reports/` paths.

## NOT RUN

Windows, browser, implementation. The installer audit is
static only: neither `.exe` was run (both are Windows GUI
binaries; the payloads were extracted and read, never
executed), so the v243 behavioural deltas are established
from the banner, the string inventory, and the version history
— except item 13 above, which is marked inferred. The
`nirmmita` entry's cases were run on v279 (Linux ELF build).
