# R83-00 — `vitti a = k` diverges when the `kosh` moves; safe today only because nothing is ever freed; option 1 breaks 3 fixtures, so I stopped and documented it

- **Commit on `main`:** `a41b5ba` (documentation and evidence only; no compiler change). Pushed with git, not `--force`.
- **Compiler: `Sutram 1.0 (v278) - sampurna sutra` — unchanged this round.** `sutram_compiler`, `sutram.exe` and
  `win/sutram.exe` are byte-identical to origin/main's. Linux x86-64 cloud, 2 cores, 7 GB.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `NO-EXPECTATION=4 PASS=255`, FAIL=0.** Library proofs **229/229**. Property proofs **86/86**.
- **Gates (`sh tools/gates.sh`, Xvfb display, Linux): 57 PASS / 0 FAIL / 1 NOT-RUN (Windows execution).**
- **The guard, origin/main → this tree: Linux ELF and Linux PE — 665 programs, 538 byte-identical, 127 refused
  identically, 0 DIFFER, 0 new.** **NOT RUN: the Windows compiler under Wine** — its `.exe` is byte-identical to
  origin/main's, so its outputs cannot differ.

## WS1 — they diverge, and whether they do depends on unrelated code and on the system

Your program, and three more (`evidence-r83/ws1-aliasing.txt`; each run on Linux, on PE under Wine, and in the
guard-page build):

| program | Linux | PE (Wine) | what it shows |
|---|---|---|---|
| `kosh k[2]; push 41; vitti a = k; push 42; push 43; k[0] = 7` → `a[0] k[0]… a[0] a==k` | `41 41 7 1` | **`41 41 41 0`** | **the same program prints differently on the two systems** |
| the same, with one `nirmmita(64)` before the pushes | `41 41 41 0 7` | `41 41 41 0 7` | split on Linux too; `a[0] = 99` never reaches `k` |
| `a` passed as a `kosh` | length **2** | | the real one is 3 |
| R42's `examples/255` with a growing push through `w` | `kosh_len(v)` **1**, `kosh_len(w)` **2** | | "an alias is the kosh" holds only without growth |

**Why:** a `kosh` grows **in place** when it is the arena's newest block (R65), and then the two names stay one
buffer. Otherwise — anything allocated in between, or always on PE and in the guard-page build, which have no
in-place growth — `kosh_push` copies the cells to a new buffer and only the name pushed through follows.

**Does it matter today? Wasteful and wrong, not unsafe.** **Nothing is ever freed:** the compiler emits no
`munmap` or `VirtualFree` anywhere; the `mandapa` rewind moves only the scratch cursor, and a `kosh` is never on
the scratch side (R82 kept it persistent). The old buffer stays mapped and owned, so a stale read or write lands
in valid memory. The guard-page build — every block its own mapping — runs all four without a fault. **The day
anything recycles `kosh` memory, this is a use-after-free.** That includes the next step for blocks (taking a
block `kosh`'s memory back) and the Step-0 recycling bins.

## WS2 — option 1 breaks 3 programs, so I stopped; option 3 is done; my judgement

**Option 1, built as a variant and measured, not shipped** (`evidence-r83/ws2-option1-count.txt`, the diff
beside it: 61 added lines). It refuses an assignment or declaration whose value is a bare `kosh` name, at the name:

```
a2.sm:4:15: Sutram Error [E_KOSH_PRATILIPI]: kosh 'k' anyasmin namni na rakshyate - ekah kosh, ekam nama
      vitti a = k
                ^
Sanket: vardhamanah kosh sthanam parivartayati, dvitiyam nama purane sthane tishthati - mulyani pratilipyantam (k[i], kosh_len)
```

*(kosh 'k' is not kept under another name — one kosh, one name; a growing kosh moves, the second name stays at
the old place; copy the values.)*

**The tree under it: 665 programs, 3 newly refused, no library module refused:**
- `examples/252_r38_alias_kosh_oob` — R38: "a kosh alias … must be bounds-checked like the original";
- `examples/255_r42_alias_kosh_push` — R42: "an alias of a kosh is the kosh" (false under growth, above);
- `examples/287_r82_kosh_after_mandapa` — mine, R82.

**All three exist to exercise this alias, and none is a program anyone wrote to do work.** But they are in the
tree and you said stop, so I stopped: the compiler is unchanged.

**What option 1 leaves.** Four other routes still give a second name for the buffer: a `prakriya` returning its
`kosh` parameter, a `kosh` passed to a plain parameter, a `kosh` pushed into another `kosh`, and `k + 0`. **None
of them gives a second *`kosh`*, though.** The existing type rule refuses each one where it would be passed as a
`kosh` (`kosh tark: tatv prakar bhinn` — checked for all of them). What remains is a plain number holding the
address, and indexing it is raw memory: unchecked, as all raw memory is, and refused in `parikshita`. **So option 1
plus the type rule closes every way to have two `kosh` names for one buffer.**

**Option 2 (deep copy):** no — it turns an assignment into a hidden O(n) copy, and the copy would *still* not
follow later pushes, so it trades one surprise for another.

**Option 3, done now:** reference §16 states the rule with the program that shows it (checked on Linux and PE):
*a second name for a `kosh` is not the same `kosh` once it grows; keep one name, copy values out.*

**My judgement:** ship option 1, and turn the three fixtures into refusal goldens — 252 and 255 encode a promise
the runtime cannot keep. Know what it does to R82: its gate's five refusal cases also copy with `bahar = k`, so
they would become compile-time refusals. With option 1 I found **no** route left by which a block's `kosh` reaches
a `kosh` parameter after the block. R82's run-time check would become defence in depth, which a gate can still
test with the check's own build switch. That is the better outcome: the mistake is caught when compiled. The raw-address routes are the handle work's job (R148): **a `kosh` should not be a value at all — usable
only as a `kosh` argument.** Do option 1 before anything recycles `kosh` memory, not after.

## WS3 — guard pages on v278: nothing faults that did not before

`tools/guard_page.py` (`evidence-r83/ws3-guard-page.txt`):

| | controls | suite | library proofs | properties | failed |
|---|---|---|---|---|---|
| v277 (`3b28a58`) | 5/5 | 253/0 | 229/229 | 86/86 | 0 |
| **v278** | **5/5** | **255/0** | **229/229** | **86/86** | **0** |

The two more suite programs are R82's examples 286 and 287. **And the new code, run under the guard-page compiler:**
the `R82 kosh-mandapa` gate 9/9, `R81 parikshita` 24/24, and R82's cost programs (20 million checked calls;
50,000-push growth with the 5-word header) exit 0. Every new header word and stack slot stays inside its block.

## What I did not do

- **Option 1 is not shipped** (your rule: it breaks 3 programs). The variant and its count are in the evidence.
- **The four raw-address routes are open** (a plain number holding a `kosh`'s address; indexing it is raw memory).
  Closing them needs the handle design, not a rule on assignment.
- **`examples/255`'s comment** ("an alias of a kosh is the kosh") is wrong under growth; I have not edited the
  fixture.
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, the frozen packs, `MEMORY-DECISION.md`. **Not run:** real
  Windows; the Windows-compiler guard path (identical binary).
