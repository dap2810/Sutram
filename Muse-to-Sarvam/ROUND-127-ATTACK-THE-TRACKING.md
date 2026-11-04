# Muse Round 127 — Attack the tracking, and find the fourth defect

- **Base:** main at v300 (`ca90b1ec`, same version string as `d2c96eaf`; the
  three new commits since R126 are only the R127/R201/R126 briefs, no
  `src/` changes — so current main is still the **buggy** v300, the fix is
  **not** applied yet, and this round attacks the buggy tracking as assigned).
- **Independence:** I did **not** read Claude's R125 hand-back or programs. I
  tested from the brief's WS1 cases plus my own derivation (from the brief's
  description of the table: per-function, name-keyed, set only from a bare
  variable, never cleared, blind to control flow). I therefore report **all**
  defects I found and identify which are new relative to R126, rather than
  guessing which three Claude found. By counting: I found 8 defect instances
  (3 segfaults + 5 silent over-reads); Claude found 3 total (2 segfaults +
  1 over-read); therefore **at least 5 of mine are new** beyond Claude's
  three, even if Claude found 2 segfaults + 1 over-read among my 8. The
  clearest new one — the fourth and beyond — is the **global** door
  (inter-function, not in the brief's WS1 list, which is all intra-function).
- **Test and analysis only.** No tracking fix was built, no code was changed.

## WS1 — Break `kosh_vars`: what fires, what crashes, what silently over-reads

The table is per-function, keyed by name, set only from a bare variable,
never cleared, blind to control flow. Results on v300 (all probes in this
round's deliverables, `r127_ws1_*.sm`):

### NOT defects (clean refusals or correct behaviour — the table is not broken here)

| Case | Result | Why it is not a defect |
|---|---|---|
| Redeclaration `vitti a = k; vitti a = m` (and reverse) | Compile error `E_DUPLICATE_NAME` ("punah ghoshana 'a'"; hint: use `a = ...` to give a new value) | Redeclaration is forbidden, so the "never cleared" table cannot be stale via redeclaration — you must use assignment, which is the reassignment case below |
| Two variables, same name, different scopes (outer raw + inner kosh, and reverse, via `yadi` block) | Compile error `E_DUPLICATE_NAME` (inner declaration refused) | Sutram has no block scoping for names (one namespace per function, duplicates refused), so the table **cannot** confuse scopes — scopes do not exist for names |
| Kosh passed as a `prakriya` parameter, indexed inside (`foo(kosh k) { k[100] }`) | Refuses (`mala ank seema atikram`, exit 1) | Parameter type is in its declaration, not in `kosh_vars`, so it bounds-checks directly — correct |
| `vitti` as a `prakriya` parameter type (`foo(vitti x)`) | Compile error (vyakaran dosh, `vitti` not a valid parameter type) | `vitti` parameters do not exist (confirmed: `vitti` is not a valid parameter type; `dasham` is), so the vitti-parameter door does not exist — you must use a kosh parameter (above, which bounds-checks) |
| Assignment mala → kosh via assignment (`a = m; a = k; a[100]`) | Refuses (bounds check, exit 1) | Assignment **to** a kosh **does** mark (table is updated on kosh assignment), so this direction is correct |
| Ternary in-bounds, both branches (`a = c ? k : p`; `c = 1` → `a[0] = 11`; `c = 0` → `a[0] = 77`) | Both correct, exit 0 | Ternary assignments are **not** marked (not a bare variable), so they use raw code — which works for in-bounds reads on both kosh and raw buffers (by accident for kosh, if elements are at offset 0). In-bounds is fine; out-of-bounds is not (below) |

### DEFECTS — segfaults (3 instances)

| # | Case | Result | New? |
|---|---|---|---|
| S1 | Reassignment kosh → raw, straight-line (`a = k; a = p; a[0]`) — R126's finding, re-verified on current main | **Segfault, exit 139** (instead of `77`) | **OLD** (R126; likely one of Claude's two segfaults) |
| S2 | Reassignment kosh → mala, via assignment (`a = k; a = m; a[100]`) | **Segfault, exit 139** | **NEW** — stale kosh marking on a mala buffer crashes (table never cleared on non-kosh assignment; assignment to kosh marks, assignment to non-kosh does **not** clear) |
| S3 | Loop reassignment (`a = k`; loop (2 iterations) `{ a = p }`; `a[0]` after loop) | **Segfault, exit 139** | **NEW trigger** (same root cause as S1 — may-analysis, never cleared — but proves the defect affects loops, not just straight-line code; the fix must handle loops, not just straight-line reassignment) |

S2 is the key new segfault: it proves the table is **set on kosh assignment
but never cleared on non-kosh assignment** (mala → kosh marks and refuses
correctly; kosh → mala does **not** clear and crashes). The asymmetry is the
defect, not just the reassignment itself.

### DEFECTS — silent over-reads (5 doors, all print `0`, exit 0, no refusal, no crash)

All five are koshes obtained **without** a bare variable, so `kosh_vars`
never marks them, so out-of-bounds reads use raw code (no bounds check) and
print `0` (garbage from zero-filled region memory beyond the elements, within
the mapped 64 MB region — so no crash, just a wrong number that looks right).
All five are **new** relative to R126 (which found no over-reads, only the
S1 segfault).

| # | Door | Program (short) | Result |
|---|---|---|---|
| O1 | Call result | `vitti a = make_kosh(); a[100]` (make_kosh returns a kosh) | `0`, exit 0 |
| O2 | Mala cell | `m[0] = k; vitti a = m[0]; a[100]` (mala holding a kosh) | `0`, exit 0 |
| O3 | Kosh cell | `outer[0] = inner; vitti a = outer[0]; a[100]` (kosh holding a kosh) | `0`, exit 0 |
| O4 | **Global, inter-function (THE FOURTH)** | Global `vitti holder = 0`; `set_holder()` assigns `holder = k` (kosh); `mukhya` reads `holder[100]` | `0`, exit 0 |
| O5 | Ternary | `vitti a = c ? k : p` (`c = 1`, kosh); `a[100]` | `0`, exit 0 |

**O4 (global) is the fourth defect, highlighted because it is the most
distinct:** it is **inter-function** (not in the brief's WS1 list, which is
all intra-function), and it is **global per se, not just inter-function** —
a control probe (global assigned a kosh **in the same function**,
`mukhya`, then read `holder[100]` in `mukhya`) **also** prints `0`
(`r127_ws1_global_samefn.sm`). So globals are **never** marked, in **any**
function's table, whether assigned in the same function or a different one.
The per-function table cannot track globals at all. O3 (kosh cell) is a
second clearly new door (distinct from the mala cell: a kosh, not a mala, as
the container).

Counting again, for the brief's "find the fourth": R126 found 1 (S1). This
round finds 7 more (S2, S3, O1–O5). Total 8. Claude found 3 (2 segfaults +
1 over-read). Even if Claude found S1 + one of (S2, S3) + one of (O1–O5),
there are **5 more** he did not find. The fourth — and the fifth, sixth,
seventh, and eighth — are here.

## WS2 — The silent over-read, smallest program, exactly what it prints

`r127_ws2_smallest.sm` (9 lines):

```sutram
prakriya make_kosh() {
    kosh k[4]
    kosh_kship(k, 11)
    nivartanam k
}
mukhya() {
    vitti a = make_kosh()
    likha(a[100])
}
```

**It prints exactly `0` (no trailing newline) and exits 0.** The kosh holds
`11` at `[0]` and has length 4 (capacity 4); index `100` is past its length,
but because `a` was assigned from a call result (not a bare variable),
`kosh_vars` never marked it, so no bounds check fires, and the raw load reads
`0` from zero-filled region memory beyond the elements — a wrong number that
looks right, with no error and no crash. (Mala-cell and kosh-cell versions
are equally small at 10 lines with a newline `likha`; the call-result version
without it is 9 lines, so it is the smallest.)

## WS3 — The 4.2M cliff, verified once more (and the brief's "never measured" is wrong)

**Correction first:** the brief says "That number has been quoted from a
report and never independently measured." **That is wrong (stale).** Round
124 independently measured it on v298 (commit `69a03fc7`, probe
`maxcap_alias2.sm`: original `99`, alias `41` stale, exit 0). This round
re-verifies it on v300 (current main), so it has now been measured **twice,
on two versions, with the same result**.

Program (`r127_ws3_cliff.sm`; naming chosen to match the brief's question —
here `a` is the **alias** (`vitti a = k`) and `k` is the **original** kosh,
the reverse of R124's naming, so the values below are the same break with
swapped names): `kosh k[4]`; push `41` (1 element); `vitti a = k` (alias);
push 4,194,305 more via `k` (total 4,194,306 elements, past the 4,194,304 →
4,194,305 relocation point, where capacity doubling 4,194,304 → 8,388,608
exceeds MAXCAP 8,388,603 and relocates); then post-relocation write `k[0] =
99` (via the original); then read both.

**Result on v300 (0.1 s, exit 0): `a[0] = 41` (stale, broken — should be `99`),
`k[0] = 99` (correct).** The alias breaks at about 4,194,304 elements: after
relocation, the original is updated but the alias keeps the old pointer, so
the alias reads the old value (`41`) while the true value is `99`. The
brief asks "report what `a[0]` gives": **`a[0]` gives `41`** (the stale value,
not the current `99`) — proving the alias broke. (In R124's probe the names
were reversed (`a` = original, `k` = alias), so R124 reported `a[0] = 99` and
`k[0] = 41` — same values, opposite names, same break.)

## NOT RUN

Windows execution (cannot run Windows; v300's Windows memory work does not
affect these Linux tracking results — the compiler is the same v300 as R126
for these behaviours, verified by re-running R126's reassignment probe on
current main with the same segfault), browser, implementation (none
authorized — attack and analysis, not fixing the tracking), native-speaker
review, full suite (no tree changes; the v300 suite numbers stand, not re-run
here).
