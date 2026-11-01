# R96-00 (answers R96 and R97) — The loop hang is real: a `chakra` compared a decimal end as its raw bits, and on v282 it does not stop (R97's "off-by-one" is the first five lines of an endless loop). Refused from v283.

- **Commit on `main`:** this round's commit (on `c6c572b`, which carries R97). It contains compiler v283, one compile-time refusal, the R95 version check extended, docs, three goldens and evidence.
- **Compiler: `Sutram 1.0 (v283) - sampurna sutra`** (was v282). Linux x86-64 cloud, 2 cores, 7 GB.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `NO-EXPECTATION=4 PASS=270`, FAIL=0** (new: 300, 301, 302). Library proofs **229/229**. Property proofs **86/86**.
- **Gates (`sh tools/gates.sh`, Xvfb display, Linux): 58 PASS / 1 FAIL / 1 NOT-RUN.** The FAIL is `installer version`: the installer ships v243 and the compiler is v283. The NOT-RUN is Windows execution.
- **The guard, origin/main (v282) → v283: Linux ELF, Linux PE and the Windows compiler under Wine — 680 programs, 548 byte-identical, 129 refused identically, 0 DIFFER, 3 new.** No program in the tree has a decimal `chakra`.

## WS1 — why it hung: the disassembly says candidate 2, with 3 and 1 in the other forms

`chakra i = 0 tak 3.0` on v282, the loop test (`evidence-r96/loop-forms.txt`):

```
inc    rbx                            ; the counter + 1, a whole-number add
mov    rax,rbx
push   rax
movabs rax,0x4008000000000000         ; the end, 3.0, as its IEEE-754 bits
pop    rdx
xchg   rax,rdx
cmp    rax,rdx                        ; a whole-number compare
jle    <body>
```

**`chakra` is whole-number code from top to bottom.** It does `inc`, then `cmp`, then `jle`. A decimal end is
evaluated to its bits once (candidate 3) and then compared as an integer (candidate 2). 3.0 is
`0x4008000000000000`, which is 4,613,937,818,241,073,152, so the loop counts toward 4.6 × 10¹⁸. That is not
literally for ever, but at a billion iterations a second it is about 146 years.

A decimal **start** gives candidate 1: the counter starts from 0.5's bits and adds an integer 1.
`chakra i = 0.5 tak 2.5` printed `4602678819172646912`, `…913`, `…914`, …

**One note on your exact line.** `chakra dasham i = 0.0 tak 3.0` does not compile on v282 or v283. It fails with
`vyakaran dosh, pankti 2:12, shabd 'dasham'` and exit 1, because a type is not allowed in the `chakra` header.
It prints no program output, but it doesn't run, so there is nothing to hang. The hang is real in every form
that does compile.

## WS4 — the sweep: every counter/bound combination, v282 then v283

| form | v282 | v283 |
|---|---|---|
| `chakra i = 0.0 tak 3.0` | **0 1 2 3 4 5 … never stops** | refused, caret at `0.0` |
| `chakra i = 0 tak 3.0` (whole counter, decimal end) | **never stops** | refused, caret at `3.0` |
| `chakra i = 0 tak 2.5` | **never stops** | refused |
| `chakra i = 0 arabhya 2.0 paryantam` | **never stops** | refused |
| `chakra i = 0.5 tak 2.5` | **counts 4602678819172646912, …** | refused |
| `dasham i = 0.5` then `chakra i = 0 tak 2` (a `dasham` counter) | **prints 0.000000 three times** (whole-number bits read as a decimal) | refused |
| `dasham n = 3.0` then `chakra i = 0 tak n` | **never stops** (8.3 million lines in 3 s). My first look showed only `0 1 2 3` because I printed four lines - the same trap as R97's | refused |
| `chakra i = 0.0 tak 3` | 0 1 2 3. **Right by luck**: 0.0's bits are 0 | refused |
| `chakra i = 3.0 tak 0.0` | prints nothing. **Wrong**: it should count 3 2 1 0 | refused |
| `chakra i = 0 tak 3`, `chakra i = 3 tak 0` | 0 1 2 3, 3 2 1 0 | **unchanged** |

**So you were right to suspect more than one, and it was more than one.** On v282, five forms never stopped,
one counted garbage, one printed garbage, one silently skipped the loop, and one was right by luck. Every form
with a decimal anywhere is now refused.

**`yavat` and `kuru … yavat` with decimals are fine.** They use the `dasham` comparisons. `x <= 3.0` stepping by
1.0 prints 0.000000 to 3.000000, and `kuru` adding 0.5 while `x < 2.0` ends at 2.000000. (Adding 0.1 ten times
ends at 1.1, not 1.0, because 0.1 is binary. That is §15's rule, so a decimal loop should compare with `<` or
`<=`.)

## WS2 — refuse or support: refuse, and I agree with your instinct

```
300_r96_chakra_decimal_bound.sm:4:22: Sutram Error [E_CHAKRA_DASHAM]: chakra purnankaih eva gananam karoti - dashama-sankhya na sambhavati
      chakra i = 0 tak 3.0 {
                       ^
Sanket: chakra i = 0 tak 3 likhyatam; dashamaya yavat upayujyatam
```

`r96_check_for_float` runs first in `.gs_for`. It refuses three cases: a `dasham` counter (`is_float_var`), a start
or end that is a `dasham` (`expr_is_float`, written or a variable), and the same in the `arabhya … paryantam`
form. It puts the caret under a written decimal. For a `dasham` variable it can only name the file, because the
AST has no position for a variable yet.

**Why refuse rather than support:**

- **Support is not cheap.** It means a second loop generator: a float counter, `addsd` by 1.0, a `ucomisd` test,
  and a direction for decimal bounds. It also means one more thing the PERF2 fast paths and the R65 peepholes
  must get right.
- **It would also teach the wrong habit.** A `chakra` is a count, and a decimal end usually means the programmer
  wants a step of 0.1, which `chakra` cannot express anyway.
- **The refusal fits the language's other decimal rules:** `vitti` takes no fraction, `%` takes no `dasham`, and
  now `chakra` takes no `dasham`. Its Sanket points to `yavat`.
- The error code and the Sanskrit are mine, for your review.

## WS3 — the goldens

- **300** `chakra i = 0 tak 3.0`, refused at 4:22.
- **301** a `dasham` counter, refused.
- **302** the supported way, `yavat (x <= 3.0)`, prints `0.000000 1.000000 2.000000 3.000000`, then
  `chakra i = 0 tak 3` prints `0 1 2 3`.
- Reference: a paragraph in the `chakra` section, **"A `chakra` counts in whole numbers (v283)"**, with the
  `yavat` form.

## R97 — the correction is itself wrong: on v282 it does not stop

R97 says `chakra i = 0 tak 3.0` prints `0 1 2 3 4` and stops, so it is an off-by-one. **Measured on v282, the
binaries of origin/main `c6c572b`, it does not stop** (`evidence-r96/v282-remeasured.txt`):

| run | result |
|---|---|
| ELF, 3-second timeout | killed (exit 124) after **6,625,058 lines**, the last one 6625057 |
| PE from the Linux compiler, under Wine, 10 s | killed after **16,511,651 lines** |
| PE from the Windows compiler (`sutram.exe` v282), under Wine, 10 s | killed after **17,077,101 lines** |
| `dasham n = 3.0; chakra i = 0 tak n`, ELF, 3 s | killed after 8,277,190 lines |

**`0 1 2 3 4` is exactly what its first five lines look like.** A `| head -5`, or a console that showed the
first screenful, gives that. The loop ends only when the counter passes 4,613,937,818,241,073,152. The
disassembly above shows why: there is nothing in that code that could stop at 4.

So R96 was right about the symptom; it was only the reproduction line, `chakra dasham i = …`, that was wrong,
because it doesn't compile. **v437 and the README sentence were right in substance: a loop whose end is a
decimal does not stop in any useful time.** I nearly made the same mistake myself: my first table read
`chakra i = 0 tak n` with a `dasham n` from four lines and called it right. A run with a timeout corrected it.
**The check that catches it is to count lines under a timeout, not to read the first few.**

R97's WS4 sweep (all four bound types plus `0.0 tak 3`, v282 then v283) is in the same file:

- **v282:** an integer literal end and a `vitti` variable end are correct. A `dasham` literal end and a `dasham`
  variable end never stop. `0.0 tak 3` is right by luck, because 0.0's bits are 0.
- **v283:** both `dasham` ends and the `0.0` start are refused; the integer forms are unchanged.

WS2's question, refuse or convert: **refuse**, for the reasons above. Converting once at entry would have to
choose between truncating and rounding `2.5`, and that is the silent-loss rule R92 just removed. The goldens
WS3 asks for are 300 to 302.

## R95 — what I did, and what I left for the next round (you said stop everything else)

- **WS1, one version everywhere: done.** The `installer version` gate now also reads the version string in the
  tree's `sutram_compiler`, `sutram.exe` and `win/sutram.exe`, and FAILS unless all three equal the source's.
  - Every binary already reports its version: `--version` prints it, and the string is inside each file.
  - The self-test now has 9 cases. The new one is a tree `sutram.exe` one version behind with a current
    installer.
- **`Sutram-Setup.sha256` is not stale:** it is the exact SHA-256 of the `Sutram-Setup.exe` beside it
  (`285470a4…`). What is stale is the package, which is v243, and the gate says so.
- **WS3, `sutram-fmt`:** it is a 3-line POSIX shell launcher, `exec python3 -B "$(dirname "$0")/tools/sutram_fmt.py" "$@"`,
  and it works. It is a launcher like the `sutram` command, not a broken binary. I left its name, because the
  docs call it as `./sutram-fmt`.
- **WS4, `backups/`: your measurement is wrong, and I didn't touch it.** `backups/` holds **6 tracked files, 9.2 MB**:
  `README.md` plus a 5-part split zip (`bk.z01`–`bk.z04`, `bk.zip`), dated 2026-10-22, at compiler v244. Its README
  explains how to rejoin and unzip it. A fresh clone gets all six. My standing rule is "backups/ is EXEMPT from
  cleanup", so I have not changed it. If it breaks a tarball extraction, I'd need to see the command that failed.
- **WS2, the root cleanup:** not done this round. It is the R88 kind of move (git mv and a link sweep), and it
  needs a round of its own. Your list conflicts with the R88 folder plan in one place: `docs/` versus
  `docs/rounds/` for the round work-products (`F7-…`, `F8-…`, `R34-…`). I'll do it next round unless you say
  otherwise.

## Not done

- **The R95 root cleanup**, above.
- **The installer rebuild:** it needs Windows.
- **Positions for a `dasham` variable** in `E_CHAKRA_DASHAM`, and for `& | ^ << >>` in `E_DASHAM_KRIYA`.
- **Not run:** real Windows.
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, the frozen packs, `MEMORY-DECISION.md`.
