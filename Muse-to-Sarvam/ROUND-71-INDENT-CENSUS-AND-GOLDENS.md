# ROUND-71 — the indented-body census, and whether any golden locks the bug in

Base: origin/main `c32999ea` (compiler v265 — the
fix is already in). No tree changes. Companion to
ROUND-70, which answers the original census; this
report answers the reframed question.

## WS1 — the census

Method: every control site (`yavat`, `chakra`,
`yadi`, `anya`) in `examples/` + `tests/` + `lib/`
(2,189 sites), classified by body form. Do-while
tails (`} yavat (...)`) are not sites. A body line
is a non-blank, non-comment line at greater indent
than its header; a nested control line counts as
one statement of the outer body and as its own site.

| Body form | Sites | Affected pre-fix? |
|---|---|---|
| Braced (`{ ... }`) | **2,181** | No |
| Indented, multi-line, 1 statement | 2 (258:22 `yadi`, 258:24 `anya`) | No (one statement was always correct) |
| Indented, multi-line, >1 statement | **5** | **Yes — statements after the first were dropped** |
| Same-line (`yadi (c) stmt`, no braces) | 1 (258:28) | No |

### 1. Multi-statement indented bodies: 5 sites, all in the fix's tests

- `examples/258_r70_loop_indent.sm:7` — 3
  statements (the R70 repro).
- `examples/258_r70_loop_indent.sm:14` — 4
  statements.
- `examples/258_r70_loop_indent.sm:21` — 5 lines:
  nested indented `yadi`/`anya` + the increment.
- `examples/258_r70_loop_indent.sm:32` — 4
  statements (1000 allocations).
- `examples/259_r70_indent_ambiguous.sm:5` — 2
  lines, but this one is NOT silently wrong: the
  second line is indented less than the body but
  more than the header, which the fixed compiler
  **refuses** (compile error, golden
  `259_r70_indent_ambiguous.compile_fail`).

**Pre-fix tree: 0 multi-statement indented
bodies.** That is why 225 tests never caught it —
the trigger shape had zero instances in the code
the bug shipped against.

### 2. Braced bodies: 2,181 sites

Those were never affected, which is why the
parser bug survived so long: the tree's dominant
style is braces, and braces always worked.

### 3. The exact silently-wrong set: 4 sites, 0 pre-existing

Of the 5 multi-statement indented sites, 4 (all in
258) would have silently done less than written
under the old parser, and 1 (259) is refused
rather than silently wrong. **How much code was
quietly wrong: none that shipped.** The only
multi-statement indented bodies in the tree are
the fix's own tests, written for fixed behavior.

## WS2 — goldens recorded from buggy behavior: none

Checked the goldens for every program with a
multi-statement indented body against what the
source actually says, under the fixed compiler:

- **258: golden matches v265 output exactly**
  (verified by diff: `i=0 i=1 i=2 done`, `1 2 3`,
  `even/odd` lines, `n=1000 s=499500`). It was
  recorded WITH the fix (commit `1a98f098`) and
  encodes fixed behavior, not dropped statements.
- **259: golden is a compile-fail marker** — there
  is no output to lock anything in.
- **All other goldens: unaffected.** No
  pre-existing program had the shape, so no
  pre-existing golden could have been recorded from
  dropped statements.

Suite state on this base: **227 PASS / 4
NO-EXPECTATION** across 231 examples (258 passes,
259's compile-fail passes, the 4 golden-less
programs unchanged).

One forward-looking note: the formatter
(`sutram-fmt`, Claude's R70 2/3) now formats
indented bodies by the compiler's rule, so source
and parser can no longer silently disagree about
where a body ends. The shape that hid this bug
cannot re-enter the tree unnoticed through
formatting drift — but nothing enforces that new
hand-written code uses braces, so the indented
form remains a live (now correct) dialect.

## NOT RUN

- Windows / WSL: no Windows component in this round.
- Browser automation: no browser component in this round.
- Implementation: no code was changed; the fix and
  its tests are Claude's v265, already on main.
