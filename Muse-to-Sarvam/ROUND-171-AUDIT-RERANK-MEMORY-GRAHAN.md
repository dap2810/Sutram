# ROUND-171 — the fourteen Tier 1 findings, re-ranked; the two the audit did not settle; the grahan question

**Base:** main at v315, tip commit `adf4f8c6` · **Deliver into:** `Muse-to-Sarvam/`

**Read only. Nothing compiled or run.** The audit is ChatGPT's ROUND-233
(`ChatGPT-to-Sarvam/ROUND-233-AUDIT.md` + `ROUND-233-EVIDENCE.json` +
`ROUND-233-FIXES.md`; the fixes were read only to know what changed).
"R:" = `docs/LANGUAGE-REFERENCE.md`, "C:" = `src/sutram_compiler.asm`,
"A:" = `src/r65_arena.inc`. Every line number below was re-grepped on the
tree cited; every count re-derived. The tip differs from the audit's base
`a3f41178` only by 7 added brief files, so the audit's pinned v315 line
numbers match. Where a behaviour differs between main and the staged v324
(branch `r186-grahan-and-files`, commit `e1f29f14`), both are stated.

The parent verified the decisive claims independently before writing this
report. Two corrections to the working notes are recorded in place: the
reverse-direction section had the Tier 2 / Tier 3 boundary wrong (see
below), and the MEMORY-MODEL contradiction sits at v324 `:1` vs `:10`,
not at "line 8 vs line 10". The re-ranked totals are unaffected by either
correction.

---

## Task 1 — the fourteen Tier 1 findings, re-ranked

The test, from the brief: **could a student, following this document or
using this function as documented, get a wrong answer without being told?**

### Verdicts

| Finding | Verdict | One-line reason |
|---|---|---|
| R01 `likh8`/`pad8` as 8-bit | **STAYS Tier 1** | Unconditional 8-byte store/load, no guard; doc-led 1-byte use silently corrupts neighbouring data. |
| R02 `likh8c`/`pad8c` as character I/O | **STAYS Tier 1** | Wrong operation (memory access, not I/O) plus guard holes (no lower bound, no whole-extent check) with silent failures. |
| R04 `grahan` "reads a number" | **STAYS Tier 1** (on v315; settled on v324) | All four static consequences verified by reading; final-line loss fires through the book's own loop pattern. |
| R05 `aksharank` index ignored | **STAYS Tier 1** | Note flatly false; the tree's own example + golden (`aksharank("AZ",1)` = 90) prove the index is used. |
| R07 "varna"/"character" without a unit | **STAYS Tier 1** | `vartani_aayam("नमस्ते")` is 18, not 6; continuation bytes surface as "character codes". |
| R08 `vartani_tul` "compare" | **STAYS Tier 1** | Exactly 0 equal / 1 different, no ordering; `> 0` as "a after b" is true for either order. |
| R11 `nirmmita` zeroed | **STAYS Tier 1** | R:183 promises zeroed unconditionally; persistent `nirmmita` never zeroes, and released scratch bytes are re-handed un-zeroed once the persistent cursor climbs that far. |
| R14 `brihat_ank_tak_laghu` negative digit | **STAYS Tier 1** | Code defect against its own contract (R:137) and header: `d <= 9` only. A −1 cell returns −1 silently, exit 0. |
| R15 `brihat_ank_se` failure mutation | **DEMOTE to Tier 2** | R:136 wrongly promises clearing for descriptor failures, but status 0 correctly signals the failure, and the code header + R116 test pin the true split. |
| R17 `purna_prasaran` variance | **STAYS Tier 1** (narrowly) | Reference promises −1 only for an oversized answer; `[0,0,6000000000]` has fitting variance 8000000000000000000 but returns −1 via the per-deviation guard. |
| R24 `madhya` example | **DEMOTE to Tier 2** | Body returns `b`, not the median — but the sort is explicitly marked omitted (`# ... sort t ...`, R:1279) and the example's job is scratch lifetime. |
| R27 `ekanka_gan` negative domain | **DEMOTE to Tier 2** | R:258 omits the domain, but the behaviour is defined and pinned in `NUMERIC-CONTRACT.md:49`, the code header, and the stdlib page. |
| R29 `ganita_paripurna_*` saturation | **DEMOTE to Tier 2** | R:114 overgeneralises, but every overflow case does saturate, no specific saturated value is promised for invalid-domain inputs, and each header documents the 0 sentinel. |
| R33 inclusive `chakra`, no endpoint caveat | **STAYS Tier 1** | Inclusive endpoints taught with no MAX/MIN caveat; an ascending loop to MAX wraps the counter to MIN and never terminates. |

**Tally: 10 stay Tier 1, 4 demote to Tier 2, 0 found wrong on the
evidence.** With the one promotion from the reverse direction (R09,
below), the re-ranked totals are **Tier 1 = 11, Tier 2 = 11, Tier 3 = 25**
of the audit's 47.

### R01 — `likh8` / `pad8` documented as eight-bit — STAYS Tier 1

What the document says (R:167–168): "`likh8` | write 8-bit value",
"`pad8` | read 8-bit value". No signature, no width beyond "8-bit". The
wrong width claim appears nowhere else in the reference or the books;
the only other `pad8` mention in the reference (R:407,
`pad8(digits + 0 * 8)`) uses an 8-byte stride and is consistent with the
true behaviour.

What the code does (C:23697–23742): `likh8(addr, val)` emits
`mov [rdi], rsi` — opcode bytes `48 89 37` — an unconditional **8-byte
store**; `pad8(addr)` emits `mov rax, [rdi]` — `48 8B 07` — an
unconditional **8-byte load**. The write is guarded in no way: no bounds
check, no width check, no alignment check. The only other mention of
`BN_LIKH8` is the `r73_check_call` escape check, which refuses storing a
scratch address inside a `mandapa` — an escape check, not a width or
bounds guard. The tree's own test proves the qword width:
`tests/r54_check/raw_valid.sm:4` does `likh8(b, 258)` and the acceptance
harness asserts `pad8(b)` prints `258` — a value that does not fit in a
byte.

Concrete path: a student follows the doc and the `nirmmita` row (R:183:
`nirmmita(n)` gives `n` **bytes**), allocates `nirmmita(1)` to hold one
byte, and writes `likh8(p, 65)`. The store writes 8 bytes: byte 0 is 65
and bytes 1–7 are the high bytes of the value. The 7 extra bytes
overwrite whatever was allocated next in the arena — another variable, a
string, kosh metadata. **Silent corruption**: no error, no crash, and
downstream values come out wrong. The reverse trap is the same shape: a
student who believes `likh8` writes one byte and uses it to poke a
single byte inside an 8-byte cell overwrites the whole cell. `pad8` on a
1-byte buffer returns the byte plus 7 neighbouring bytes as one number —
a **silent wrong value**. Crash only at a mapping boundary (the 8-byte
access touches an unmapped page); inside the arena the usual outcome is
silent clobbering, which is worse than a crash because nothing reports
it. The doc's own safety framing is defeated by the lie: R:183 says
"writing past `n` bytes is your mistake", but the student believes they
are writing exactly 1 byte.

### R02 — `likh8c` / `pad8c` documented as character I/O — STAYS Tier 1

What the document says (R:169–170): "`likh8c` | print a character",
"`pad8c` | read a character". No signature, no argument list, no mention
of a bound. The wrong "character" claim appears nowhere else:
`docs/rounds/R54-BUILTIN-BOUNDS.md:23-24` describes the real behaviour
correctly, and `docs/rounds/R71-MEMORY-BOUNDARY.md:16-17` shows correct
usage. The student-facing table is the only place that says character I/O.

What the code does (C:24576–24670):
`likh8c(addr, value, bound)` is a conditional qword memory write: `cmp
rdi, rdx` / `jae +3` (skip) / `mov [rdi], rsi` (`48 89 37`). `pad8c(addr,
bound)` is a conditional qword memory read: `cmp rdi, rdx` / `jae +8`
(skip to `xor eax, eax`) / `mov rax, [rdi]` (`48 8B 07`). The guard is
unsigned `addr < bound` only: **no lower bound, no whole-eight-byte
extent check**. A failed write is silently skipped — no error, no return
value to inspect. A failed read silently returns **0**,
indistinguishable from a genuine stored 0. Guard holes: `likh8c(buf - 8,
v, buf + 64)` writes 8 bytes into whatever precedes the buffer;
`likh8c(0, v, bound)` with `bound > 0` dereferences address 0 (crash);
`addr = bound - 1` passes the guard, then the 8-byte access touches 7
bytes past `bound`.

Concrete paths: (a) a student who believes `pad8c` reads a character
does `vitti c = pad8c(buf, bound)` expecting `65` for `'A'` and gets
the 8 bytes at `buf` as one qword — for `"ABCDEFGH"` that is
0x4847464544434241; `yadi (c == 65)` is false although the first
character *is* `'A'`. (b) A student who believes `likh8c` prints a
character gets no output at all — and has instead written an 8-byte
value into memory. (c) `pad8c(buf + 7, buf + 8)` passes the guard and
reads 7 bytes past the allocation. Two independent Tier-1 defects in one
row: the operation is wrong, and the real guard has holes with silent
failure modes.

### R04 — `grahan` documented as "reads a number" — STAYS Tier 1 (on v315; settled on v324)

What the document says (R:178): "`grahan` | read a number from input".
That is the whole contract in the reference. The books add only "read
input (-1 on EOF)" (English book :346) and a section "`grahan()` and end
of input" (:409-411: "When input ends, `grahan()` now returns `-1`, so
programs can exit cleanly", with a `yadi (a == -1)` loop-exit example).
Neither says anything about signs, skipped characters, wrapping, or what
happens to digits already read when input ends.

What the code does (C:1074–1139 — the implementation is emitted machine
code stored as byte tables): one byte at a time from fd 0; LF ends the
number (`mov rax, r8`); every byte outside `'0'`..`'9'` is **skipped**;
digits accumulate with `imul r8, r8, 10` / `add r8, rdx` and **no overflow
check**; a read returning 0 (EOF) **or negative (error)** jumps to `.eof`,
which does `mov rax, -1` — even if digits were already accumulated, they
are discarded. Each of the audit's four static consequences verifies by
reading: `-5` → 5, `1 2` → 12, blank LF → 0, final `5` without LF → −1.
The last case is the sharpest: the book's own loop-exit idiom misfires
on a perfectly good final number — a program reading numbers until EOF
silently loses its last value and reports "Input ended" instead.

What changed on v324 (read on the v324 tree): the `grahan`
implementation is rewritten as real instructions (`R186_GRAHAN_TAIL`),
and the comment states the new contract. A `-` or `+` **before the first
digit** sets the sign (the last one wins); at EOF, digits already read
are returned **with their sign**, and −1 only when there were none — and
in that case `nivesha_anta()` is set to 1, because a typed `-1` now
genuinely reads as -1 and can no longer be told from the end signal.
Skipping and unchecked wrapping remain — but the v324 reference (§4d)
now **documents them with exact examples**, so on v324 the residuals are
disclosed behaviour, not silent surprises. R04 is settled on the v324
branch, but that branch is staged, not merged; the ranking is of the
finding on the audited tree.

### R05 — `aksharank` documented as ignoring its index — STAYS Tier 1

What the document says (R:191): "`aksharank` | character code (note:
index currently ignored)". The neighbouring row R:190 says `akshar` is
"character code at an index" — the table contradicts itself.

What the code does (`.ge_call_charcd`, C:24439–24480): two arguments
evaluates both, then `movzx eax, byte [rdi+rdx]` — the indexed byte; one
argument is index 0. The tree's own suite contradicts the doc note
directly: `examples/65_char_code_index.sm` is `likha(aksharank("AZ",
1))` and its golden is `90` — `'Z'`, the byte at index 1. Under the doc's
claim the answer would be `65`. `lib/varna.smlib:5-6` already records it
in-tree: "`aksharank(s, i)` already honours i in the compiler".

Concrete path: a student following the doc calls `aksharank(s, 3)`
expecting the first character's code and silently gets the code of
`s[3]`. A comparison such as `yadi (aksharank(s, 2) == 65)` is false
although the student believes they tested the first character. The note
is flatly false, and the wrong-answer path is a one-line student program.

### R07 — "varna" / "character" used without a unit — STAYS Tier 1

What the document says (R:186–194): `vartani_aayam` "varna length",
`vartani_tul` "varna compare", `akshar` "character code at an index",
`anka_akshar` "a new one-character string from a code", `akshar_guru` /
`akshar_laghu` "uppercase / lowercase a character". No row says bytes,
code points, or scalars, and "varna" is never defined as a unit anywhere
in the reference.

What the code does (all five cited implementations are byte operations):
`vartani_aayam` (C:23791–23845) is an inline strlen — counts **bytes to
the NUL**; `akshar` / `aksharank` (C:24405–24480) take the **byte** at
the index; `anka_akshar` (C:24483–24512) allocates 2 bytes and stores
only the low eight bits of the code (a code of 0 gives an empty string; a
code above 255 is silently truncated); `akshar_guru` / `akshar_laghu`
(C:24514–24574) change ASCII case only; `vartani_pratilip`
(C:24739–24807) copies bytes through the NUL.

Concrete path: the language's own premise makes this reachable — it is a
Sanskrit language, its book examples contain Devanagari literals, and
"varna" in Sanskrit means a letter. A student writes the natural
program — count the varnas in a Devanagari string:
`likha(vartani_aayam("नमस्ते"))`. `"नमस्ते"` is 6 code points but 18
UTF-8 bytes; the function returns **18**. The same student indexing into
it gets continuation bytes presented as "character codes":
`aksharank("अ", 1)` is 164 (0xA4, the second byte of अ U+0905).
`anka_akshar(2309)` — the code point of अ — keeps only the low byte
0x05, a control character, not अ. Mitigation noted, and it does not
demote the finding: the byte unit **is** stated in the library headers
(`lib/varna.smlib:8-22`, `lib/khand.smlib` header) — but the reference
table, the first document a student reads, says nothing, and its word
"varna" actively suggests letters. The fix is a one-line unit note per
row; the wrong-answer path is real until then.

### R08 — `vartani_tul` returns 0 for equal, 1 for different; reference says only "compare" — STAYS Tier 1

What the document says (R:187): "`vartani_tul` | varna compare".
Nothing about the return value: not equality-only, not ordering, not the
values 0 and 1.

What the code does (`.ge_call_vartcmp`, C:23956–24048; the comment at
C:23957 states it: "vartani_tul(s1, s2) → 0 if equal, 1 if not"): a
byte-by-byte loop; on any differing byte — including a NUL against a
non-NUL, i.e. a length difference — it jumps to `mov eax, 1`; if the loop
runs to the terminator it does `xor eax, eax`. The return is **exactly 0
for equal, 1 for different**. There is no −1, no three-way ordering, no
magnitude: it is an equality test, not a comparison in the
negative/zero/positive sense. The tree's own golden demonstrates it:
`examples/256_r44_vartani_sanskrit_names.sm` prints `vartani_tul(b,
"sutra")` = 1 — `"sutra"` sorts *before* `"sutram"` yet returns 1, the
same value a string sorting *after* would return.

Concrete path: a student who reads "varna compare" and writes the
idiomatic ordering test, `yadi (vartani_tul(a, b) > 0)`, gets a silent
wrong answer in both directions — `vartani_tul("apple", "banana") > 0`
is **true**, although "apple" sorts *before* "banana", and
`vartani_tul(a, b) < 0` is **never true**.

**Correction to the brief (not the audit):** the ROUND-171 brief
abbreviates this as "returns 0 for equal and 1 for greater". That is
wrong: 1 means *different*, not *greater*. The audit table has it right
("0 for equal and 1 for different byte strings"); the brief's "1 for
greater" should read "1 for different". A student following the brief's
wording who tested `== 1` for `a > b` would branch silently for `a < b`
too. (Confirmed by two readers and by the code comment.)

### R11 — `nirmmita` documented as giving zeroed bytes; persistent allocation does not zero — STAYS Tier 1

What the document says: R:183 — "`nirmmita(n)` gives `n` **bytes**,
zeroed". Unconditional: every `nirmmita` buffer is zeroed. R:1302–1303:
"Each `nirmmita` inside [a block] takes memory from the scratch side of
the program's 1 GiB field, zeroed, like any `nirmmita` buffer."
R:1304–1305: "A later block reuses the same memory, and sees zeros, never
the earlier block's data." `docs/MEMORY-MODEL.md:4` repeats the blanket
claim.

What the code does (read on main): one arena, two opposing
cursors — persistent `cur` grows up from the base, scratch `end` grows
down from the top (`sima`). Persistent `nirmmita`, `r65_emit_nirm`
(A:245–298): the fast path checks room, advances `cur` to
`align16(cur + size)`, and returns the old `cur`. **No clearing anywhere
in the function.** The header comment itself states the premise it relies
on (A:23): "Memory from the arena is never reused, so it arrives zeroed
like mmap memory" — true only for bytes never written before: fresh mmap
pages arrive zeroed from the OS, so a persistent allocation over
never-touched bytes is zeroed by accident of the OS, not by any code in
this path. Scratch `nirmmita`, `r73_gen_scratch_nirm` (A:423–445),
**does** zero (A:441: "zero it (memory is reused)"). Block exit,
`r73_gen_rewind` (A:403–414) and `r73_gen_ret_rewind` (A:533–552), both
restore `end` to the mark with a plain store. **No clearing.** Bytes a
block wrote stay written after the block ends.

The persistent-reuse path is real on main: a block writes scratch bytes
in `[end_after, mark)`; the block exits and `end` is restored to `mark`,
unzeroed; later persistent `nirmmita` calls advance `cur` upward, and
once `cur` climbs past `end_after` into `[end_after, mark)`, the next
persistent allocation is handed bytes the block wrote, with no zeroing —
and the program reads the block's stale values as if they were a fresh
zeroed buffer. Reachability, stated honestly: the gap to close is
`(end_after − cur_at_exit)` bytes of further persistent allocation, so
the path needs persistent usage plus scratch high-water to approach the
arena size — a large-program path, not a beginner-toy path. But the
document's guarantee is unconditional, the failure is a silent wrong
value with no signal, and the path is confirmed by the staged fix itself.
The audit's R:1303 citation is half-right — the block-to-block half holds,
because scratch `nirmmita` zeroes on allocation — but R:183's blanket
"zeroed" plus R:1303's "like any `nirmmita` buffer" (which asserts the
persistent direction too) is false.

What v324 changes (read on the v324 tree):
`r175_emit_zero_to_mark` is added to `src/r65_arena.inc` (`:428`,
`:437`) and called from both rewind sites (`:422` and `:574`): it zeroes
`[end, mark)` — everything taken on the scratch side since the mark —
before the cursor is restored. Its own comment states the main-tree
defect in so many words: "Before R175, memory a block had written went
back unzeroed, and an ordinary nirmmita taken later, once the persistent
side had climbed that far, read the block's data", and "The cursor moves
back only in `r73_gen_rewind` and `r73_gen_ret_rewind`, so zeroing in
these two covers every way out". Persistent `nirmmita` itself still does
not zero, but after v324 every byte it can reach that was previously
scratch-written has been zeroed at block exit, and never-touched bytes
arrive zeroed from the mmap — so v324 settles R11 on this reading.

Not to be conflated with R169 ("zero of 347 examples over 16 MiB"): that
was about blocks *returning* memory — whether a returned address stays
valid — a different question from whether `nirmmita` bytes are zeroed.

### R14 — `brihat_ank_tak_laghu` checks `d <= 9` only — STAYS Tier 1

What the document says (R:137): "`brihat_ank_tak_laghu` (`brihat`) | a
digit outside 0..9, `n < 0` / the value is past the range | stops |
`E_MULYA_AYOGYA` / `E_PHALA_SEEMA`." Every digit outside 0..9 must stop
the program. The function's own header (`lib/brihat.smlib:68–70`) says
the same, and the in-body comment at line 72: "every digit 0..9 and
n >= 0 (`E_MULYA_AYOGYA`); refused before r * 10 + d passes MAX".

What the code does (`lib/brihat.smlib:71–85`): the digit guard at line 79
is one-sided — `abhava(d <= 9, ...)` with no `d >= 0`. (The `n >= 0`
check at line 73 *is* present; only the digit lower bound is missing.)
Any cell value from the minimum `vitti` up to −1 passes `d <= 9`, and
also passes the line-80 overflow guard (which only constrains `r` near
MAX). Digits are least-significant first, so reading the code gives,
with no run: a single cell holding −1 returns −1; cells `[1, −1]` give
−9; cells `[−1, 1]` give 9; a single cell holding the minimum `vitti`
returns the minimum `vitti` — all exit 0. These shapes match the
candidate-branch evidence in `ROUND-233-FIXES.md` (before the fix,
`brihat_ank_tak_laghu(a, 1)` gave `'-1'` and `'-9223372036854775808'`,
`(a, 2)` gave `'-9'` and `'9'`; after, the R116 contracts went from 139
checks / 4 failed to 0 failed) — but the shapes above are derived from
reading the main-tree code, not from that report. Why it slipped: the
R116 test (`tests/r116/test_contracts.py:110–116`) tests digit 10 and
`n = −1`, but no negative digit. The function is also the verification
backstop: it is the converter every bigint test uses to print a result,
so a corrupted digit cell is printed as a plausible-looking number
instead of being refused. The candidate branch changes the guard to
`d >= 0 && d <= 9`, the one-line fix the finding calls for. This is the
clearest Tier 1 in the set: a code defect against its own documented
contract and its own header comment, producing a silent wrong value with
no signal.

Concrete path: a student builds a digit array by hand (or a computation
writes a bad cell) with a −1 in it and converts it back for verification
— `likha(brihat_ank_tak_laghu(a, 1))` prints −1, exit 0, where the
document promises a stop with `E_MULYA_AYOGYA`.

### R15 — `brihat_ank_se`'s failure mutation described wrongly — DEMOTE to Tier 2

What the document says (R:136): "`brihat_ank_se` (`aadhar`) | a bad
digit or base, or the number needs more than `n` digits | status 0, the
digits cleared | —". The "how" column applies to all three failure kinds
listed: on any of them the destination digits are cleared (to zero).

What the code does (`lib/aadhar.smlib:80–111`): the code distinguishes
two failure classes and the header comment states the split exactly.
Descriptor failures — bad base, negative count, `n < 1` — return 0 at
line 86 **before writing the destination at all**, so whatever was in
`x` stays. Bad-digit and insufficient-capacity failures *do* clear it
(lines 92, 105). The R116 test pins this:
`tests/r116/test_contracts.py:143–155` pre-fills `x` with 7s and expects
them **unchanged** on descriptor failure. So the reference contradicts
the code, the code's own header, and the test.

Why Tier 2, not Tier 1: the failure itself is correctly signalled
(status 0, correctly documented in the same row). The student must read a
destination after a signalled failure, trusting only the row's secondary
cleanup promise. No caller in the tree depends on the clearing for
descriptor failures. Wrong failure description, not a silent wrong answer
on the primary path. Fix by splitting the row: descriptor failures leave
`x` untouched; bad-digit / insufficient-capacity failures clear it —
exactly as the code header already says.

### R17 — `purna_prasaran` variance contract too broad — STAYS Tier 1 (narrowly)

What the document says (R:116–119): "The library's number functions do
not wrap on ordinary inputs (v276): `kramgun`…, `laghuttam_samapavartya`
(lcm) and `purna_prasaran` (integer variance) return **−1** when the
answer is too large to fit; …". The only −1 condition the reference
states for `purna_prasaran` is "the answer is too large to fit". No row
for `purna_prasaran` exists in `docs/NUMERIC-CONTRACT.md` (grep: no hit),
so the reference passage is the only contract-level statement, and it
states one condition.

What the code does (`lib/sankhyiki.smlib:179–221`): the header (lines
179–181) is more honest than the reference: "integer population variance
(truncated toward zero; uses the truncated mean, so exact only when the
mean is integral); −1 when it does not fit in int64, **or when one
squared deviation alone does not** (R80)". The refusal sites: lines
199/203 (`x − m` itself would overflow → −1); line 208 —
`yadi (d > 3037000499) { nivartanam 0 - 1 }` — any single absolute
deviation above ⌊√(MAX)⌋ refuses, because `d*d` would not fit int64,
even though the variance (an average of squares) may fit easily; lines
210–215 (the running quotient/remainder would overflow → −1).

Arithmetic, verified by hand: `[0, 0, 6000000000]` has mean
`6000000000 / 3 = 2000000000` (integral, so truncation is irrelevant
here). Deviations: `−2000000000, −2000000000, +4000000000`. Squares:
`4·10¹⁸, 4·10¹⁸, 16·10¹⁸`; sum `24·10¹⁸`; variance `24·10¹⁸ / 3 =
8000000000000000000`, which fits
(`8000000000000000000 < 9223372036854775807`). But the third deviation,
`4000000000 > 3037000499`, trips line 208, so the function returns −1.
The audit's arithmetic is correct. (The single square itself,
`16·10¹⁸`, does not fit int64 — the per-deviation refusal is a genuine
implementation limitation of the split-square accumulation, not a free
choice; the defect is the reference's failure to say so.)

Concrete path: `likha(purna_prasaran(xs, 3))` on `[0, 0, 6000000000]`
prints −1; the reference tells the student −1 means "the answer is too
large to fit", so the student concludes the variance does not fit (or
takes a failure branch, or aborts) when the answer fits comfortably.
There is no alternative in the function to get the right answer for this
input. Mitigating fact, recorded honestly: the per-deviation condition
*is* stated in the library source header and in the generated stdlib
page — a student reading the function's own comment is told. It is not
stated anywhere in the reference or in the numeric-contract document,
and the reference is the document the verdict is judged against. Narrow
stay: the values are extreme (a deviation above ≈3.04·10⁹), but they are
ordinary-sized `vitti` values, and the input is a three-element array a
beginner could plausibly construct.

### R24 — `madhya` described as the middle of three — DEMOTE to Tier 2

What the document says: the example at R:1270–1282, under the heading
"Example" in the `mandapa` (block) section — `prakriya madhya(a, b, c)
# the middle of three numbers`, body assigns `[a, b, c]`, `# ... sort t
...` (R:1279), `nivartanam t[1]` (R:1280). The section's stated topic
(R:1249–1250) is what a block is for: "a `mandapa` holds the temporary
buffers of one piece of work", and the following subsection (R:1284–1287)
is "What it holds in v1.0 — Scalar scratch". The example's job in context
is to show a number read out of scratch, not to teach a median algorithm.
Note also that `madhya` as a *library* name means something else
entirely: `lib/sankhyiki.smlib:27` defines `madhya(kosh dasham xs)` as
the arithmetic mean — the reference example's `madhya(a, b, c)` is a
one-off illustration, not the library function.

What the code does: there is no code to check — this is example text, not
a library function. As written, the body assigns `[a, b, c]`, does not
sort, and returns `t[1]`, which is `b` — the second argument, not the
median. A student who copies the example verbatim and calls
`madhya(3, 1, 2)` gets `1` instead of the median `2`. But the gap is
flagged *in the example itself*: line 1279, `# ... sort t ...`, is an
explicit ellipsis marking omitted work — the reader is told, in the code,
that sorting is not shown. The header comment states the *intent* of the
finished function, and the body shows the scratch mechanics around a hole
where the sort would go. A misleading example, not a silent trap. Had the
`# ... sort t ...` line been absent, this would stay Tier 1. Fix the
header comment (e.g. "the middle of three numbers — sorting omitted") or
fill in the sort.

### R27 — `ekanka_gan` negative bit-count domain omitted — DEMOTE to Tier 2

What the document says (R:258, a row of the §4b/§4c rename table):
"`ekanka_gan` | `bit_gan` | `ganit` | the count of 1-digits (एकाङ्क)
in `n`'s binary form". No domain is stated in that row, and no other
mention of `ekanka_gan` in the reference states one (the only hit in the
reference is line 258). The books never mention the function (0 hits in
both books).

What the code does (`lib/ganit.smlib:208–217`): the loop runs only while
`x > 0`, so every negative input returns 0. The audit's reading of the
code is correct.

The domain is pinned elsewhere: `docs/NUMERIC-CONTRACT.md:49` —
"`ekanka_gan` (was `bit_gan`) | `vitti` | defined for `n >= 0`;
negative `n` → `0` (not two's-complement popcount)" — plus the property
pin (`prop_numeric28`), the function's own header ("negatives return 0",
`lib/ganit.smlib:208`), and the stdlib page
(`docs/sutram-stdlib.html:129`).

**Adjudication — Tier 2, not the working notes' Tier 3.** The working
notes demoted to Tier 3 on the ground that the domain is pinned in three
places. That is too far. The reference row is the student-facing
contract, and it states no domain; its words ("count of 1-digits in
`n`'s binary form") invite exactly the two's-complement reading that
`NUMERIC-CONTRACT.md` explicitly disclaims — and the disclaimer proves
the misreading is a live student expectation. A student following the
reference row calls `ekanka_gan(-5)` and gets 0 instead of 62, with no
pointer from the row to any of the three places that pin the domain. But
it is not Tier 1 either: the behaviour is defined and pinned (not an
undefined behaviour), the wrong-answer path requires the expert
two's-complement expectation (a beginner counting bits in a positive
number gets the right answer), and the stdlib page — the other place a
student looks a function up — states it. Tier 2: a wrong/incomplete
message in the reference row. Fix: add "defined for `n >= 0`; negatives
return 0" to R:258.

### R29 — `ganita_paripurna_*` grouped under endpoint saturation — DEMOTE to Tier 2

What the document says (R:114, the last row of the §3a arithmetic table):
"the library's checked arithmetic says whether the answer fits:
`ganita_janchit_yuj` / `_nyun` / `_gun` (`ok[0]` is 1 or 0);
`ganita_paripurna_*` stops at the largest or smallest `vitti` instead of
wrapping". Read plainly, the `paripurna_*` family saturates (returns
MAX/MIN) instead of wrapping. The policy paragraph R:123 adds:
"Mathematical library functions must follow their individual documented
contracts — exact result or declared failure, or explicit saturation
where specified".

What the code does (all eight `paripurna_*` in `lib/ganita.smlib`):
four of the eight return 0 on invalid-domain input —
`ghat` on `e < 0` (:622), `bhaj` on `b == 0` (:652), `shesh` on `b == 0`
(:669), `kramgun` on `n < 0` (:715) — not MAX/MIN. And every one of
those 0-returns is documented in the function's own header comment as a
deliberate sentinel ("the saturating form has no ok channel, so 0 is the
documented sentinel"). `docs/NUMERIC-CONTRACT.md:28–31` records the same
split.

Why Tier 2, not Tier 1: R:114's claim is about overflow ("stops at the
largest or smallest `vitti` instead of wrapping"), and every genuine
overflow case in the family *does* saturate — the 0-returns are all
invalid-domain inputs, for which saturation has no defined endpoint
(there is no "largest quotient of division by zero", no "saturated value
of (−1)!"). The student cannot say which MAX/MIN value was promised and
denied, because none was promised for that input. What R:114 does is
overgeneralise a one-line summary; the per-function contracts — the place
R:123 itself says to look — state the 0 sentinel explicitly. The checked
family (`ganita_janchit_*`, same inputs → 0 with `ok[0] = 0`) gives the
student a safe form, and the reference points at it in the same row. The
one-line summary should say saturation applies to overflow, with
invalid-domain inputs returning the documented 0 sentinel.

### R33 — inclusive `chakra` presented without an endpoint caveat — STAYS Tier 1

What the document says (R:579–607, §6a, "Counted loops"): `chakra i = 0
tak 4` prints `0 1 2 3 4`; R:625: "The endpoints in this example are
**inclusive**". The section covers whole-number counters (R:604–607: a
`dasham` start/end/counter is refused with `E_CHAKRA_DASHAM`) and warns
about the pre-v283 decimal-bits non-termination — but says nothing about
the integer endpoints MAX/MIN. The books say the same, with no endpoint
caveat (English book :228 — "`tak` includes its last number, so `0 tak 4`
is the five places 0, 1, 2, 3, 4" — and ch. 6, including a "Descending
Loops" note). No MAX/MIN caveat appears in either book or anywhere in the
reference's loop section. What a student *could* infer, only by combining
distant passages: R:101–102 states a `vitti` runs from
−9223372036854775808 to 9223372036854775807 and that runtime `+`/`*`
past the range wrap "without any warning" — but that is about arithmetic
operators, not about the loop counter's increment-then-compare shape, and
nothing connects it to `chakra`.

What the code does (`.gs_for`, C:20255 onwards): direction is detected
only when both bounds are constants (C:20270–20287: start > end constants
→ `for_descend = 1`); otherwise the loop is ascending. The shape is
test-at-bottom with an initial jump to the test, then the body, then the
increment (`inc rax` for ascending, C:20382), then the signed comparison
and backward branch (ascending `jle body_start`, C:20467). An ascending
loop ending at MAX: after the body runs with `i = MAX`, the increment
wraps `MAX` to MIN (plain `inc`, no overflow check), the test
`MIN <= MAX` is true, so the loop re-enters and iterates the whole int64
range again — effectively it never terminates normally. The descending
mirror: a constant-bound loop descending to MIN wraps MIN to MAX on
decrement, `MAX >= MIN` stays true, same non-termination. So
`chakra i = 0 tak 9223372036854775807 { … }` is a real, reachable program
(a student counting "to the maximum" or boundary-testing an inclusive
loop) whose behaviour is non-termination, not the inclusive run to MAX
the section teaches. This is worse than a silent wrong value: the program
never finishes, with no diagnostic.

The missing caveat sits in the primary teaching section and in both books,
the endpoint is stated as inclusive with no bound, the wrap is inferable
only by combining the general wrapping-arithmetic passage with the
unpublished increment-then-compare codegen shape, and the failure mode is
non-termination on a program the documentation invites. Off-by-one at the
endpoint is the most common beginner loop bug; a one-sentence caveat ("a
loop ending at the largest `vitti` does not terminate — the counter wraps
past it; end at MAX−1 or use `yavat`") fixes it.

Side observation, not verdict-driving: direction detection needs both
bounds constant, so a variable-bound descending loop (`chakra i = a tak b`
with `a > b` at run time) takes zero iterations rather than counting
down. That is a separate finding for another round.

---

### Reverse direction — Tier 2 / Tier 3 findings that are actually Tier 1

**Correction to the working notes, recorded here because it changes the
section's labels (not its totals).** The working notes had the Tier 2 /
Tier 3 boundary wrong. The audit's actual tiers, re-read from
`ROUND-233-AUDIT.md` (14 / 7 / 26), are: Tier 2 = R03, R16, R22, R30,
R31, D02, E01; Tier 3 = R06, R09, R10, R12, R13, R18, R19, R20, R21, R23,
R25, R26, R28, R32, R34, R35, A01, B36, C36, D01, D03, D04, D05, D06, E02,
E03. The notes listed R06, R10, R12, R18, R19 as Tier 2 (they are Tier 3)
and R03, R30, R31, D02, E01 as Tier 3 (they are Tier 2), described
several of them under the wrong content (R06 as "string `+` with a
number", R18 as "string literal `==`", R19 as "`vartani_sandhi`",
R03 as "`likha` argument count", R30 as "`grahan` EOF −1", R31 as
"`likha` newline", D02/E01 as documentation-only rows), and omitted R23
entirely. Every judgement below is re-derived from the audit's actual
rows, not from the notes' descriptions. The re-ranked totals
(11 / 11 / 25) are unchanged by this correction.

**One promotion: R09, `akshar_rakh`.** Every other Tier 2/3 finding stays
where the audit put it.

#### PROMOTE to Tier 1: R09 — `akshar_rakh` (audit Tier 3)

What the document says (R:672–676, a row of the §6d `mala` table):
"`akshar_rakh` (BN 14) | store one character at an index | stores a
**single byte** at the given **byte** offset inside a `mala` of character
codes (unchecked: the store takes a bare address — outside the buffer is
your mistake, §19). For a string, use `akshar_lekh`". The reference **does**
warn that the store is unchecked and that an out-of-bounds store is the
student's mistake — so the out-of-bounds case alone does *not* promote.
What no reference row states, anywhere, is the rest of the contract:
the **one-byte stride**, the **low-eight-bit truncation** of the value,
and the **low-byte return** (the code's own comment at C:24364–24402:
"1-byte stride; store ONLY value's low eight bits. Return 0..255.
Caller must provide writable storage and a valid byte offset").

Why it promotes: the neighbouring rows invite the wrong reading.
R:660 says `p[i]` "counts 8-byte cells", and the `mala` rows around R:672
all talk in cells and elements. A student treats the index as a cell
index — as the table teaches elsewhere — and writes
`akshar_rakh(buf, 1, 300)` expecting byte 8 (cell 1) to hold 300. What
actually happens, per the code (C:24364–24402): the store is
`mov byte [rcx+rdx], al` — a **one-byte** store at byte offset 1, keeping
only the low eight bits of 300 (44). The student has written the wrong
byte, *inside* the buffer, with no crash and no diagnostic: the buffer
now holds a silently wrong string, and `likha(buf)` prints it. The
failure is silent, inside bounds, and caused by a unit the reference
never states (stride + truncation), while the adjacent rows teach the
opposite unit (8-byte cells). The reference row's unchecked-store warning
does not cover it — the student is not outside the buffer. Tier 1.

#### Tier 2 findings that stay Tier 2 (7)

- **R03** (wrong file names): R:180–181 calls `dvaram` a descriptor
  helper and `paadh` open — the R169 D1 swap, already established. A
  student following the reference writes a program that compiles (arity
  passes) then fails at runtime — a loud failure, not a silent wrong
  answer. Stays Tier 2.
- **R16** (LCM stops on MIN / 0): the path exists —
  `laghuttam_samapavartya(MIN, n)` reaches the gcd guard — but the
  failure is a loud refusal (exit 1), not a silent wrong value, and the
  code's `E_GCD_BHADDA` guard is the thing that catches it. A loud stop
  is not Tier 1. Stays Tier 2.
- **R22** (example depends on an absent helper): following the book's
  example uses `sankhya_padh`, a name that does not exist, and the result
  is a loud compile failure, not a wrong answer. The book's example is
  broken, not a trap. Stays Tier 2.
- **R30** (failure token is not always the first bytes): R:8/R:232–235
  says every stopping message begins `Sutram truti`; positioned headers
  carry a filename/line/column prefix first. Diagnostics prose; no
  student wrong-answer path. Stays Tier 2.
- **R31** (error-mode distinction omitted): R:233 uses `E_PARSE` as the
  generic syntax example, while ordinary syntax failure also has an
  uncoded `vyakaran` diagnostic. Prose; no student wrong-answer path.
  Stays Tier 2.
- **D02** (gate count used as number of gates):
  `tools/doc_counts_gate.py:184–217` counts a passing gate as a gate that
  exists. Tooling; no student consequence. Stays Tier 2.
- **E01** (accept script literal): `tests/windows/accept_v316.cmd:39`
  requires literal v316 while the staged compiler is v324. Tooling; no
  student consequence. Stays Tier 2.

#### Tier 3 findings that stay Tier 3 (25 of 26)

- **R06** (length claim too narrow): R:171 restricts `pankti_gan` to
  constant-length arrays; the code handles dynamic arrays and slice
  lengths. A student following the doc avoids a working use — safe
  avoidance, no wrong answer. Stays Tier 3.
- **R10** (platform qualification missing): R:198–201 presents the socket
  builtins without a platform limit; on Windows they return visibly −38
  and refuse. No faked connection is ever produced, so there is no silent
  wrong answer. Borderline, recorded: if the −38 were ever consumed as a
  valid socket handle it would be Tier 1; as read, the −38 is returned,
  not hidden. Stays Tier 3.
- **R12** (Windows exception stale): R:1309 says a computed negative
  allocation inside a Windows block gives 0. The allocation is refused
  loudly either way; the wrong error description is a documentation
  mismatch, not a wrong answer. Stays Tier 3.
- **R13** (allocation accounting needs precise nouns): R:173/R:1425–1445
  attributes `parimana()` only to `nirmmita` and `kosh`. Measurement
  prose; no student program goes wrong from it. Stays Tier 3.
- **R18** (braces section obsolete): R:533/R:546–575 says a brace-free
  function is one statement and multi-statement `prakriya` requires
  braces; `parse_body` handles indented bodies. A student following it
  writes braces where not needed — safe. Stays Tier 3.
- **R19** (contradictory condition claim): R:490 says `yadi(s)` is true
  even for an empty string; the compiler refuses inferred-string
  conditions with `E_VARTANI_SATYA`. Following the doc gets a loud
  compile-time refusal, not a silent wrong answer. Stays Tier 3.
- **R20** (rationale stale, refusal real): R:478–485 says kosh identity
  awaits a stable descriptor; the compiler already builds second-name
  aliases and refuses them loudly. Prose about a refusal that is real.
  Stays Tier 3.
- **R21** (function-placement rule overstated): R:1158–1159 requires
  every `prakriya` before `mukhya`; the brace-free main path can contain
  collected function definitions. A student following it places functions
  earlier than needed — safe. Stays Tier 3.
- **R23** (placeholders are not programs): R:1127–1133 and three more
  passages contain literal `...` — schematic fragments, not complete
  compilable examples. A student copying `...` gets a loud compile
  failure. Stays Tier 3.
- **R25** (parameter restriction obsolete): R:399–401 says assignment to
  a parameter faults; the compiler emits the store. A student following
  it avoids assigning to a parameter — safe avoidance. Stays Tier 3.
- **R26** (library count stale): R:370–381 says the shipped library has
  60 functions in six modules; the tree has 310 in 24. A stale count;
  no wrong-answer path. Stays Tier 3.
- **R28** (base-prefix description too broad): R:264 says
  `roop_ank_upasarga` works in any base with a prefix; the function
  delegates to `roop_ank_dhvaj`, which adds prefixes only where they
  exist. A student calling it with a base that has no prefix gets digits
  without a prefix — a missing decoration, not a wrong number. Read the
  code (`lib/roop.smlib:239–242`); no silent wrong value. Stays Tier 3.
- **R32** (keyword label wrong): R:52 describes `guna` as
  "multiply/switch"; the parser treats it as switch/case, and
  multiplication is `*`. A student writing `guna` for multiplication gets
  a loud parse failure, not a silent wrong answer. Stays Tier 3.
- **R34** (installer defect presented as current after repair): R:825–827
  says installation self-elevates and writes machine-wide locations;
  the installer was repaired. Installer prose; no student program
  consequence. Stays Tier 3.
- **R35** (book-wide brace statistic contradicted): R:568–570 says every
  book example writes main without braces; the books contradict it.
  Prose statistic; no wrong-answer path. Stays Tier 3.
- **A01, B36, C36, D01, D03, D04, D05, D06, E02, E03** (audit tooling and
  verification gaps): `guard_pair.py` baseline and timeout handling,
  R116 contract count, gates baseline, suite accounting (331 attempts,
  four missing goldens), book-program checks, the 186-golden assertion,
  embedded package entries, GNU-time dependence. Verification gaps with
  no student consequence. Stay Tier 3.

### Audit accuracy — Tier 1 citations checked

All seven Tier 1 citations checked **MATCH** (verified against the tree
at `adf4f8c6`):

- **R08** — R:187, "varna compare". Matches: the row says only
  "compare", nothing about the return value.
- **R14** — R:137, "a digit outside 0..9 → stops". Matches: the row
  promises every digit outside 0..9 stops.
- **R11** — R:183 ("`nirmmita(n)` gives `n` bytes, zeroed") and
  R:1303 ("Each `nirmmita` inside [a block] takes memory from the
  scratch side …, zeroed, like any `nirmmita` buffer"). Both match:
  the rows say what the audit says they say.
- **R33** — R:579–607 (inclusive endpoints, no endpoint/MAX caveat).
  Matches: inclusive endpoints are taught, no MAX/MIN caveat appears.
- **R24** — R:1272–1281 ("the middle of three", sort as comment,
  returns `t[1]`). Matches: the example is as the audit describes.
- **R17** — R:116–119 ("−1 for oversized variance"). Matches: the
  reference states −1 only for an oversized answer.
- **R29** — R:114 (the `ganita_paripurna_*` family grouped under
  saturation). Matches: the row groups the family under "stops at the
  largest or smallest `vitti` instead of wrapping".

One mismatch is in the **brief**, not the audit (see Brief corrections):
the brief's abbreviation of R08 as "1 for greater" is wrong — 1 means
*different*. The audit's own wording is correct.

---

## Task 2 — the two the audit did not settle

The audit says "previously identified memory/loop boundaries" are open on
main, naming them only by reference. Read as it stands at v324
(`r186-grahan-and-files`, `e1f29f14`), the boundaries expand to four
items: (a) the loop-escaping kosh leak-by-design, (b) blocks not
returning memory to the OS, (c) the `kuru` hoist gap — a new finding of
this round, below — and (d) R162's FFI statement-call hole, re-verified
still open at v324.

### (1) Does a kosh that escapes a loop still leak? Yes, by design — and it is documented in the reference, not in the books

The hoist's escape check at v324 (`r172_scan`, C:11233–11428) is a
whitelist: only index-base uses and whitelisted `kosh_*` first-argument
uses hoist. Any bare-name argument, slice, second name, or unknown node
sets escape — "fails toward leaking". Documented in the reference §19
(at v324 `docs/LANGUAGE-REFERENCE.md:1394–1409`): "Anything else is made
every pass and kept, as before" and "800,000 passes of `kosh temp[1]` —
16-20 KB resident on v317, 37,516 KB on v316". The same paragraph is in
`docs/MEMORY-MODEL.md`'s box (48 bytes/pass; 64 with a kosh in a block).
**Not in either book** — 0 hits for "made once", "800,000", or "leak" in
either book, and ch. 19's header still says v315. So the leak-by-design
is documented where a student reading the reference would find it, and
invisible where a student reading the book would look. A student who
writes a loop-escaping kosh gets a program whose memory grows every pass
— correct values, growing resident size — and the reference tells them
why, but the book does not.

### (2) Does a block still not return memory to the OS? Yes — and that fact IS documented at v324, but the R169 measurement is not

The reference §19 at v324 states it plainly (v324 `:1408–1409`):
"**A block still returns no memory to the operating system**" — new at
v324, 0 hits on main. And "Pages are reused, not returned" (`:1444`,
already on main at `:1314`). `docs/MEMORY-MODEL.md`'s box agrees. What is
**not** written down anywhere student-facing is the R169 measurement
itself: zero of 347 examples over 16 MiB — 0 hits for "347" or "16 MiB"
in the reference, MEMORY-MODEL, or either book. The books state neither
the OS sentence nor the measurement. So: the fact is documented (at v324,
in the reference and MEMORY-MODEL); the evidence for it is not.

### (3) Is there a loop shape where the hoist is wrong? Yes — a fifth loop shape exists: `kuru … yavat` (do-while)

**There are exactly three loop shapes in the compiler**, not four. The
parser dispatch (C:15953–15962) and the AST enum (C:87–120) enumerate
three: `chakra` (AST_FOR), `yavat` (AST_WHILE), and `kuru … yavat`
(AST_DO_WHILE, do-while). R163/R164 checked `chakra`, `yavat`, and the
`yadi`/`mandapa` contexts — but the brief's "four" counts two
non-loops (`yadi` is a conditional, `mandapa` is a block).

**The hoist does not cover `kuru`.** `chakra` and `yavat` have hoist
entry calls (`:21344` `r172_for_enter`, `:21741` `r175_while_enter`);
`.gs_do_while` (`:21955`) has **no** entry call — only two hoist-entry
call sites exist in the whole v324 file, and `r175_walk` is called only
from the two entry functions (`:10988`, `:10995`) plus its own recursion
(`:11021/11026/11028`). A proven-local kosh/mala declared in a `kuru`
body is made every pass and kept — **absent, not wrong** (values correct,
memory grows). Concrete shape: a `chakra` outer loop containing
`kuru { kosh temp[1]; kosh_kship(temp, i) } yavat (0)` — 800,000
descriptors on v324. The scan itself sees into an inner `kuru` body
(`.two_8_16`), so only a kosh *declared* inside the `kuru` body
misses out. Exhaustiveness, checked shape by shape: the scan enumerates
every AST type and escapes on anything unknown — nested loops, prakriya
calls, recursion, slices, `krama`/`agrim`, mandapa, `yadi dosh` / asm
handlers — all fail safe. So the four the brief named are not exhaustive:
the fifth shape is `kuru … yavat`, and it is the one shape the hoist
misses.

Adjacent open boundary, re-verified at v324: R162's FFI statement-call
hole is still open — `r108_check_call` has exactly one call site
(`:22636`, expression form); `.gs_funcall` calls the foreign function
directly. A block kosh passed by its own name to a foreign function
taking a `ptr` parameter, as a bare statement, still sets no flag.

Corrections noted in the working notes, for the record (verified):
the guard corpus is 783 on main / 787 on v324 (v324 guard line: "787
programs - 582 byte-identical, 196 refused identically, 7 DIFFER, 2
new"); examples are 331/347 on main but 335/351 on v324;
`docs/MEMORY-MODEL.md`'s box contradicts itself — at v324, the status
line (`:1`) says a proven-local `kosh` or `mala` declared in a loop is
made once (v317–v319), while the `kosh` bullet (`:10`, v317-era) says a
declaration under a `yadi`, a `yavat` loop, or a `kosh` in a `mandapa`
inside the loop is "made every pass and kept, as before" — but v319
(R175) made exactly those once; one of the two lines is wrong, and the
box needs a rewrite, not a footnote. (The working notes cited this as
"line 8 vs line 10"; the correct lines are `:1` vs `:10`, and the
contradiction is at v324, not on main — main's box does not contain the
"made every pass" language at all.) The `r172_scan` header comment
(`:10962–10971`) says "a second declaration of the name" escapes —
stale against the R175 code (`.decl`, `:11346–11360`, which counts
multiple declarations, each getting its own slot, without escaping).
The English book's ch. 19 text says v315 (`:799`, "It describes the
compiler as it is today (v315)") while its footer says v324 (`:1006`).

---

## Task 3 — the grahan question

The owner wants one input function that handles both numbers and text,
like Python's `input()`. The question is answered as the reader of the
books, not as a language designer.

### (1) Is there a text-to-number conversion today? Yes, twice over — but neither is usable as `int(input())`, and neither is discoverable

`varna_tak_ank(buf, n, ok)` in `lib/vakyank.smlib:81–137` (identical on
main and v324): base-10; the input is a `mala` of character codes, **not
a string**; optional `-` only (no `+`, no whitespace); strict all-digits
(any non-digit fails); overflow refused via `ok[0] = 0`; empty input and
a lone `-` also fail. Siblings in the same module:
`varna_tak_ank_aadhar` (bases 2/8/10/16, no sign) and
`varna_tak_dashm` (decimal with exponent, no `+`/whitespace/`inf`).
`roop` is number→text only. `sankhya_padh` in
`examples/250_r26_dosh_handler.sm:15–26` takes a packed string and fails
loudly via `dosh`, but has no overflow check and is not `yoj`-able.

The converter is **undiscoverable**: `vakyank` is absent from the
reference §4b table (which says "60 functions across six modules" —
stale against the re-counted 24 modules / 310 functions) and from both
books (0 hits). The two `vakyank` mentions in the reference are a
failure-contract row for `varna_tak_dashm` (`:142`) and a rename-table
row (`:263`) — neither is an entry a student could use to find the
converter. A student who has read the book cannot find it.

### (2) If a beginner types `hello` into `grahan()`, they get 0 — silent on main, documented on v324

What `grahan()` actually does (main, C:1074–1139 — emitted byte tables):
one byte at a time from fd 0; LF ends the number; every byte outside
`'0'`..`'9'` is **skipped**; digits accumulate with `imul r8, r8, 10` /
`add r8, rdx`, **no overflow check**; EOF returns −1 even after digits
were read. So `hello` → 0: the letters are skipped, no sign, unchecked
wrap, EOF −1 even after digits. On main it is silent **and**
undocumented — one line in the reference (R:178) and nothing else. On
v324 it is documented but still silent: the reference §4d table says
"`hello` gives 0; `12 34` gives 1234" and "**the digits already read,
with their sign; -1 only when there were none (v324)**", and both books
say "type `hello` and it gives 0" (English book :420, Sanskrit :378) —
but the function still returns 0 with no error and no flag.
`vartani_grahan` (v324, BN 48) returns the string `"hello"` — a string
kind: `==`/`<`/`+` work on its text, arithmetic and conditions are
refused — and the reference's own advice for turning it into a number is
"use `grahan()` for that line instead", which is no conversion at all.

### (3) Which shape teaches better: one function + converter, or two functions that each do what their name says? Keep two functions

Teaching order, read from the books: input is first taught in ch. 14,
after untyped `prakriya` (ch. 7) and before any typed thing (ch. 18).
The Python shape needs `yoj vakyank` + `vartani_aayam` + a `nirmmita`
cell buffer + an `akshar` loop + an `ok[0]` check — about 8 lines using
three patterns no chapter teaches, and a 3-argument call whose answer is
in an argument. It fails more instructively **only if** the student checks
`ok`; unchecked, it gives the same silent 0. Two functions need two
lines and fail visibly: `vitti a = grahan()` for a number,
`vitti nama = vartani_grahan()` for a name — and the wrong one is caught
by the type system (a string where a number is expected is refused).
**Recommendation: keep two functions.** R189's option 4 ("make `grahan`
accept text and parse what it can") has no sensible number to return for
`hello` — 0, −1 (already taken by end-of-input), or a refusal are all
choices, and `grahan` has no failure channel today.

Breakage count if `grahan()` returned text (main tree): **22 `.sm` call
sites in 10 files** (9 in 6 example files, 13 in 4 test files; `lib/` 0),
**8 guard-corpus files** of 783, plus 7 embedded sites in 2 `.py` test
files — **29 total** (29 lines containing `grahan()` outside
`vartani_grahan()` across `examples/` and `tests/`). Breakage is partly
silent (a fresh `vitti a = grahan()` becomes string concatenation) and
partly refused (`E_VITTI_PRAKAR` on reassignment; EOF −1 checks lose
their signal). Verdict: a version bump, not a fix.

### The owner's unification work — what exists, and whether it settles the question

The owner's three commits `02e992d5`, `70faf4bd`, `adf4f8c6` (all titled
"fix and test the audit findings, and the grahan unification the owner
asked for") each contain **exactly one brief file** (ROUND-189 to Claude,
ROUND-234 to ChatGPT, ROUND-171 to Muse) — no implementation, no
decision. Nothing on main answers the unification question. What exists
on the staged branches: v323 built `vartani_grahan` (BN 48, reads a line)
+ `nivesha_anta` (BN 49); v324 made `grahan` read the sign and an
unfinished last number, added two file examples, and corrected
`dvaram`/`paadh`. That is the two-function shape, built and documented —
but it is staged, not merged, and the owner has recorded no decision on
R189's option 4 anywhere in the tree. The question is not settled on main.

---

## Brief corrections

1. **R08 abbreviation (wrong):** the brief says `vartani_tul` "returns 0
   for equal and 1 for greater". 1 means *different*, not *greater*
   (code comment C:23957; audit table correct). A student following the
   brief's wording would branch silently for `a < b` too.
2. **"Four loop shapes" (wrong count):** the brief says R163/R164 checked
   "direct, yadi, mandapa and yavat". `yadi` is a conditional and
   `mandapa` is a block, not loop shapes. The compiler has exactly three
   loop shapes — `chakra`, `yavat`, `kuru … yavat` — and the fifth shape
   the brief asks for is `kuru`, which the hoist does not cover.
3. **Guard corpus (stale number):** the brief's "783-program corpus" is
   main; v324 is 787 (582 identical, 196 refused, 7 DIFFER, 2 new —
   R186). Examples are 331/347 on main, 335/351 on v324.
4. **"A block still returns no memory to the OS" (new at v324):** the
   sentence is 0 hits on main; it appears at v324 in reference §19
   (`:1408–1409`). The brief's Task 2 framing ("R169 closed it") is
   about the measurement; the *statement* is new.
5. **MEMORY-MODEL box (self-contradiction):** at v324, the status line
   (`:1`) says a proven-local `kosh`/`mala` declared in a loop is made
   once (v317–v319), while the `kosh` bullet (`:10`, v317-era) says a
   declaration under a `yadi`, a `yavat` loop, or a `kosh` in a `mandapa`
   inside the loop is "made every pass and kept, as before" — but v319
   made exactly those once. One of the two lines is wrong; the box needs
   a rewrite, not a footnote.
6. **`r172_scan` header comment (stale):** `:10962–10971` says "a second
   declaration of the name" escapes; the R175 code (`.decl`,
   `:11346–11360`) counts multiple declarations without escaping.
7. **English book ch. 19 header (stale):** its ch. 19 text says v315
   (`:799`); the footer says v324 (`:1006`).
8. **R:1303's "like any `nirmmita` buffer" (half-wrong):** the
   block-to-block half holds (scratch `nirmmita` zeroes on allocation),
   but the blanket R:183 "zeroed" plus "like any" asserts the persistent
   direction too, which is false on main (R11).

## Could not determine

- The exact per-site split of refused vs silently-changed breakage for
  the 29 `grahan()` call sites if `grahan()` returned text (needs a
  compile check; the breakage count is from reading, the split is not).
- Whether any gate outside `r172`/`r184`–`r186` asserts hoist
  `parimana()` values that a future `kuru` entry call would disturb.
- The `kuru` demonstrator's runtime behaviour (written, not run — this
  round is read-only).
- Owner intent on R189 option 4 (no decision recorded anywhere in the
  tree).
- Whether the R27 Tier 2 demotion or the working notes' Tier 3 is the
  right call for a student who has read only the books (the books never
  mention `ekanka_gan`, so the reference row is the only exposure; the
  Tier 2 call stands on the reference row being the student-facing
  contract).

## Summary

Of the audit's fourteen Tier 1 findings, ten stay Tier 1 — R01, R02,
R04, R05, R07, R08, R11, R14, R17 (narrowly), and R33 — four demote to
Tier 2 (R15, R24, R29, and R27, the last by the parent's adjudication
over the working notes' Tier 3), and none is wrong on the evidence; the
reverse direction promotes exactly one Tier 3 finding, R09
(`akshar_rakh`), to Tier 1 on the one-byte stride and low-eight-bit
truncation no reference row states, leaving re-ranked totals of Tier 1 =
11, Tier 2 = 11, Tier 3 = 25 of 47, with all seven Tier 1 citations
verified as matching and one correction to the brief itself (R08's "1 for
greater" should read "1 for different"); on the two unsettled questions,
the loop-escaping kosh leak is by design and documented in the reference
but not the books, the block-returns-no-memory fact is stated at v324
while the R169 measurement (zero of 347 over 16 MiB) is written nowhere
student-facing, and a fifth loop shape exists — `kuru … yavat`, which the
hoist does not cover at all — alongside R162's FFI statement-call hole,
still open at v324; and on `grahan`, a text-to-number converter exists
(`varna_tak_ank`) but is undiscoverable, `hello` gives a silent 0 on
main and a documented-but-still-silent 0 on v324, and two functions teach
better than one — a change of `grahan()` to return text would break 29
call sites and needs a version bump, not a fix, while the owner's
unification commits contain briefs only and settle nothing.

---

*ROUND-171, read-only. Base: main at v315, tip `adf4f8c6`. Nothing compiled
or run. Counts re-derived on this tree; line numbers re-grepped on this
tree. The audit's tiers were re-read from `ROUND-233-AUDIT.md` (14 / 7 /
26) and the reverse-direction judgements re-derived from the audit's
actual rows.*
