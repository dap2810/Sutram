# Sutram — ROUND-105: ATTACK THE ARENA. It held.

**Base:** `origin/main` at `7be8273c` (compiler v290).
**Attack target:** `claude/r108-arena-review` at `0e71e54`
(the branch, built before ROUND-108-CORRECTION, not merged).
**Deliver into:** `Muse-to-Sarvam/`. **No tree changes by this
round, and no compiler implementation** — the probes delivered
are attack programs, not compiler code.

## Where the project is (premise notes)

v290 on main: the outlives rule (a `kosh` cannot be kept in a
`prakriya`), the `mala` refusal (`E_MALA_GANIT`, 319), and
`parimana()` moving (318: 0 → 48 → 72 → 184 → 288 → 176 — a
block gives back its `nirmmita` but keeps a block `kosh`'s
header + capacity for the program's life). Suite 287, guard 697
programs (1 DIFFER, 316; 2 new, 318/319), gates 59 PASS / 1
FAIL (installer) / 1 NOT-RUN — cited from the brief and
Claude's R108 hand-back, not re-measured. **Examples are 291
on this base, not 289:** v290 added 318 and 319, so the brief's
"289 FILES" is the v289 count, stale a sixth time. Passes 287
is correct (291 − 4 without expectation, the same four:
215/216/217/219). The installer gate still fails, and the
brief's audit explains why: `Sutram-Setup.exe` is v290 with a
matching SHA-256, but `bin/sutram.exe` and `win/sutram.exe`
inside it are still v243 — the outer package was rebuilt, the
payload was not.

## WS1 — break Claude's build: I attacked it eight ways, and it held

The branch's design (its README): a `kosh` made in a `mandapa`
is a slot of the block's arena (scratch side), counted by
`parimita`, released at block exit; growth takes a new slot and
copies (this IS relocation, as ChatGPT R177 says); the aliasing
hole is closed by *refusing* a second name for a block `kosh`,
not by a stable descriptor; the call-through hole is closed by
refusing a block `kosh` as an argument to any `prakriya`
parameter that may keep it (returns, stores, passes on to a
keeping parameter; unknown callees count as keeping) — a
greatest-fixpoint analysis over the whole program. Its own
318 golden reproduces exactly on the branch compiler built
here (before 0 → 1000 numbers, capacity 1024: 16896 bytes →
after 0 → outside kosh 48).

**The four specified questions, answered with programs:**

**(a) A `kosh` grown inside the arena, with an alias taken
before growth — does the alias see the new data?**
It cannot be constructed: every second-name shape is refused
at compile time, so no alias exists at the moment of growth.
`vitti a = k` → `E_KOSH_MANDAPA` ("dvitiyam nama na
labhate"); `kosh a[1]; a = k` → the same refusal (the
message's "vitti a = k" is generic — the refusal covers
kosh-typed second names too); `bahar = k` (outer variable) →
`E_KOSH_MANDAPA` ("bahya-vittau na sthapyate"). The question
is therefore answered by refusal, not by coherence: the design
buys safety by refusing aliases, not by making them follow
growth. That is a deliberate tradeoff, stated below — not a
wrong output.

**(b) A `kosh` that outlives its block — is it refused, and at
what point?** At compile time, on the branch, for every shape
tried: the visible alias (`bahar = k`), the call-mediated
alias (`bahar = rakh(k)`, where `rakh` returns its argument
— "tam prakriyam na gacchati ya tam rakshati"), the container
store (`out[0] = k`), the `kosh_push` value (`kosh_push
(outer, k)`), the rachana field (`p.x = k`), the kosh element
(`outer[0] = k`), and the function return (`nivartanam k`
from inside a `mandapa` — "nivartanam na shakyate"). All
`E_KOSH_MANDAPA`, all before anything runs. (The global-store
shape does not exist: a top-level `kosh` declaration is a
syntax error.) A reader chain is *allowed* and works:
`padh2(k, i)` returning `padh(k, i)` prints 22 — the
fixpoint correctly computes readers as non-keeping, so the
analysis is precise, not naively conservative, for chains.

**(c) An arena exhausted mid-block — what happens?** A clean
error, both ways. Budgeted (`mandapa parimita 1000`, pushing
100,000 numbers): `E_PARIMITA`, exit 1, naming the block's
line. Unbudgeted (pushing into one `kosh` in a block, no
budget): `Sutram Error: kshetra purnam - mandapa-smritih
samapta`, exit 1 — not a crash, not garbage. The bound was
pinned exactly: 33,554,432 pushes (cap 2^25) complete;
33,554,433 (the first push requiring growth to cap 2^26)
refuses. The unbudgeted bound is the 1 GiB scratch side,
measured in cumulative slots (live + waste) — so the
"unbudgeted arena has no bound" hole from R103 is closed on
the branch: the bound is the scratch side, and exhausting it
is a clean error.

**(d) `parimana()` while the arena is in use — does it report
something meaningful?** Yes. It counts every arena slot, live
and wasted, 16-byte aligned: a `kosh` grown 1 → 2 → 4 reports
48 → 112 → 192 (live at cap 4 is 72; the 192 is all three
slots), and the branch's 1000-push case reports exactly
16896 — the sum of all eleven slots (caps 1…1024), verified
to the byte. At block exit it drops to 0 (the arena is
freed). So `parimana()` tracks the arena faithfully,
including its waste.

**The program that breaks it, I did not find.** That is the
honest result of this round, and it is a result: the branch
closes the holes it claims to close, and its failure mode on
exhaustion is a clean error, not a crash. What the attack
does establish is the design's price, which the specification
round (WS2) should carry explicitly:

1. **Refusal, not coherence.** Any program that needs a
   second name for a block `kosh` — even a safe, in-block,
   read-only alias that never outlives the block — is
   refused. Safety is bought by narrowing what can be
   written, and that narrowing should be named as a limit,
   not discovered by users one refusal at a time.
2. **Waste counts against the budget.** A `parimita` budget
   of N bytes holds roughly N/2 bytes of live `kosh` data
   after growth (192 reported for 72 live at cap 4). Anyone
   budgeting for live data gets a surprise refusal.
3. **The exhaustion error names nothing.** `kshetra purnam`
   gives no line and no count, unlike `E_PARIMITA` (which
   names the block's line). The program stops cleanly but
   does not say where.
4. **The benefit is real** (Claude's kb1, cited): 100,000
   blocks, each a 100-number `kosh`: 0 KB, 0.02 s on the
   branch, against v289's 400 MB, 0.46–0.59 s. The arena
   earns its keep where blocks are short and many.

## WS2 — attack ChatGPT's specification: PENDING, the report has not landed

Checked `ChatGPT-to-Sarvam/` (latest: ROUND-177,
ALIAS-AND-LIFETIME-FIXES) and `Sarvam-to-ChatGPT/ROUND-178.md`
(the assignment, present: ChatGPT is to specify the arena
properly this round — does growth move the data, and if so
by stable descriptor, indirection, or refusing growth; does
the arena itself move; what bounds it; the cost per
allocation, per growth, per read; three limits minimum; the
Sanskrit for anything new). **No R178 report is in the tree
yet, so there is no specification to attack, and none is
attacked here.** When it lands, the attack starts from what
WS1 established: does the specification cover the refusal
tradeoff (limit 1 above), the waste-counting budget (limit
2), and the diagnostic gap (limit 3) — the cases R177 and
the branch leave open — and does it answer R178's own
questions (growth moves or not, arena moves or not, bound,
cost) without quietly bending the owner's constraints (no
garbage collector, no runtime dependency, Sanskrit words
only, a model a student can hold in their head). This
workstream stays open until that report appears; it is not
closed by attacking R177 instead (R177 is the critique, not
the new specification).

## WS3 — the census, ninth run, and the outlives rule's breakage: none

Same method, denominators **291 examples / 306 lib / 597**
(+2 examples: 318, 319; lib unchanged).

- **Q1 (allocate inside a loop): 6, unchanged** (Q1a 3 =
  258/303/304, Q1b 0, Q1c 3 = 217/237/268). 317 pushes in a
  loop but allocates outside it (a grower, not an allocator);
  318/319 do not loop.
- **Q2 (grow a kosh >1000×): 0 definite, 1 potential,
  unchanged** (286 `varg_yog(n)`, caller-controlled).
- **Q3 (allocate without a mandapa): 58 textual examples /
  57 runtime-true + 26 lib, unchanged.** 318 has a `mandapa`
  (excluded by the method); 319's allocations are `mala`,
  which the method does not count as `kosh`/`nirmmita`
  allocation. 314 is the compile-refusing example, so
  runtime-true is 57. The known blind spot stands: the
  textual method does not see `+`-allocation (307's
  loop-concat; extended Q1 would be 7).

**Has v290's outlives rule broken any example that used to
work? No.** Every example on v290 was compiled and checked
against the new `.compile_fail` markers (an explicit
expected-fail set, new on v290): **61 compile-fails = 61
markers, zero fails without a marker, zero markers whose
example compiles.** The delta from v289 is exactly +316
(form change, not a break: 316 was an error example on v289
too, stopping at runtime; on v290 it refuses at compile
time, golden updated) and +319 (new deliberate refusal).
286 and 299, which make a `kosh` in a block and use it
inside, are byte-identical (Claude's guard, cited).

**Correction to R104, stated plainly:** R104 reported "61
compile-fails, 58 expected" on v289. The list itself had 62
entries; the headline was off by one. The true v289 numbers
were **62 fails = 59 expected + 3 flag artifacts**
(37/38/39, `--lang`), confirmed now by the v290 marker set:
61 = 59 + 316 + 319. The v289 conclusion (zero passing
programs refused) is unaffected — only the headline count
was wrong, and it is corrected here.

## What this round did NOT do (NOT RUN)

Windows (PE aliasing, installer rebuild, wizard), browser,
implementation (no compiler changes — the probes are attack
programs, not compiler code), native-speaker review. The
full suite was not re-run: no `src/`/`lib/`/`examples/`/
`tests/` file changed in this round, and the brief's +
Claude's suite/guard/gate numbers (287, 697 with 1 DIFFER +
2 new, 59 PASS / 1 FAIL / 1 NOT-RUN) are cited, not
re-measured — corroborated for passes by the compile audit
(61 fails = 61 markers) and the golden count (291 − 4 =
287). The arena branch's own suite (Claude: 288/0) was not
re-run; the branch's 318 golden and all WS1 probes were run
on a branch compiler built here. RSS beyond the WS1 probes
was not measured.

## Deliverables

- `Muse-to-Sarvam/ROUND-105-ARENA-ATTACK-IT-HELD.md` (this
  report)
- `Muse-to-Sarvam/r105_census.json` (WS1 attack table with
  programs and outputs, WS2 pending status, WS3 ninth-run
  census + outlives audit, the R104 correction)
- `Muse-to-Sarvam/atk_*.sm` (the fifteen WS1 attack probes:
  refused, visible, call, container, global, return, push,
  field, kelem, chain, parimana_small, budget, unbudgeted,
  bound, koshassign)

Work staged in `~/workspace/r105/` (probes in `ws1/probes/`,
worktrees in `tree/` (v290) and `arena/` (branch) — the
branch worktree's test binary was an untracked build
artifact, removed with the worktrees after delivery).
