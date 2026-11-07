# Sutram — ROUND-131: the message is wrong, and attack v305

**Base:** main at v305 (`c7168137`, `Sutram 1.0 (v305) - sampurna sutra`).
**Method:** read the v304/v305 code first (per the read-then-probe skill), then probe what the
reading surfaces. The v304/v305 source diff (v303 `8154fdea` .. v305 `c7168137`) is 4 files
(`src/sutram_compiler.asm` +274/-19, `src/r65_arena.inc` +16, `src/r23_capabilities.inc` +3,
`src/r11_sandesh.inc` version strings only). I read the changed code before writing any probe:
`.ge_call_koshpush` (parameter growth), `r129_check_call` / `r129_is_kosh_slice` /
`r129_may_grow` (slice-beside-growth refusal), `r23_gen_slice` (omitted-hi fix), and
`r127_emit_grow` (MAXCAP grow check). The probes below are derived from that reading, not from
the brief alone. Slice syntax is `k[lo:hi]` (colon, hi exclusive); the brief's `k[2 tak 5]` is
that slice written in words (`k[2:5]`). All probes run on the committed v305 binary
(`tree305/sutram_compiler`).

## WS1 — the message: does it still appear, and what does it say?

**Short answer: it does NOT appear to a user on v305. It is dead. It should be deleted, not
rewritten — because the behaviour it describes (parameter growth refused) no longer exists.**

### What the code says

The old message is still defined in the source at `src/sutram_compiler.asm:680`:

```
msg_kosh_param_push db "Sutram truti: kosh-tarke kosh_push asamarthitam", 10, 0
```

It is loaded in exactly one place, `.ge_call_koshpush_param_bad`
(`src/sutram_compiler.asm:22440-22444`, `lea rdi, [rel msg_kosh_param_push]`), and **no code
jumps to that label**. I grepped the whole source: the only reference to
`.ge_call_koshpush_param_bad` is its own label definition. It is unreachable (dead code).
The live "bad" path for `kosh_kship` is `.ge_call_koshpush_bad`, which emits a different
message, `msg_kosh_required` (`src/sutram_compiler.asm:662`):
`"Sutram truti: kosh prakriya hetu kosh-vitti avashyak"` (a kosh procedure needs a kosh
variable).

The v304 comment at `.ge_call_koshpush` (`src/sutram_compiler.asm:22295`) states the new
behaviour plainly: "Up to v301 a parameter was the elements' address, and a growth that moved
them left the caller on the old ones, so this was refused; from v302 every name of a kosh — a
parameter too — holds its descriptor, so the caller sees the growth as an alias does." So the
refusal the old message describes is gone, and the message that described it is dead with it.

### What the probes show (no input I tried produces `asamarthitam`)

- **Parameter growth works, no message** (`r131_ws1_paramgrow_ok.sm`): a `kosh` parameter grown
  inside a `prakriya`, read in the caller → `11 22 99 3` (caller sees 99, length 3). The old
  message does not appear, because there is no refusal to describe.
- **Growing a slice is refused earlier, with a different message** (`r131_ws1_slicegrow.sm`,
  `r131_ws1_slice_store_nogrow.sm`): `vitti s = k[1:3]` (storing a kosh slice in a `vitti`)
  refuses at the assignment with `E_KOSH_VIBHAG`: "kosh 'k' vibhagah vittau na sthapyate — kosh
  vardhate cet tasya mulyani anyatra gacchanti" (a kosh slice is not placed in a `vitti` — if
  the kosh grows, its values go elsewhere), hint: "kosh-vibhagam sakshat preshaya —
  f(k[1:4]); vittau kosh eva sthapaya (vitti b = k)" (pass the slice directly; in a `vitti`
  place only the kosh itself). The `kosh_kship(s, 99)` in the probe is never reached. So the
  old message does not appear for slice growth either — a newer, correct refusal fires first.
- **`kosh_kship` on a non-kosh refuses with `msg_kosh_required`, not the old message**
  (`r131_ws1_kship_callresult.sm`: `kosh_kship(make_kosh(), 99)` → "Sutram truti: kosh
  prakriya hetu kosh-vitti avashyak"; `r131_ws1_kship_mala.sm`: `kosh_kship(m, 99)` where `m`
  is a `mala` → same message). Both are correct (a call result / a `mala` is not a kosh
  variable), and neither names the old `kosh_push`.

So the brief's premise needs correcting: the message does not "still describe the old refusal"
to a user, because it never appears to a user. It still exists in the source and in the binary's
data (dead), which is misleading for anyone reading the source (they would think the refusal
still exists) and wastes a few bytes — but it does not lie to a student, because no student
ever sees it.

### What the message SHOULD say

Since parameter growth now works, there is **no refusal to describe, so the message should not
exist at all: delete `msg_kosh_param_push` (line 680) and the dead label
`.ge_call_koshpush_param_bad` (lines 22440–22444)**. That is the fix — a deletion, not a
rewrite. There is no corrected wording for a parameter-growth refusal, because there is no
parameter-growth refusal any more.

For the closest still-refused case (growing a slice), no new message is needed either: slice
growth is already refused at the slice storage (`E_KOSH_VIBHAG`, with a hint to pass the slice
directly), and `kosh_kship` on a non-kosh is already refused with `msg_kosh_required` (correct,
though generic — it does not name the slice case or give a hint). If Sarvam wants a specific
slice-growth message for the (now unreachable) `kosh_kship`-on-a-slice case, it should say (in
Sanskrit, with the current name, naming the case, with a hint): "Sutram truti: vibhagah na
vardhate — vibhagah drishtih eva, na svami; kosham eva vardhaya, tatah punah vibhagam kuru.
Sanket: kosham eva preshaya (kosh k), athava vibhagam purvam anyatra pratilipya" (a slice does
not grow — a slice is a view, not an owner; grow the kosh itself, then re-slice. Hint: pass the
kosh itself, or copy the slice elsewhere first). But since slice storage is refused first,
this message would also be dead — so the clean action is the deletion, not a new message.

## WS2 — attack v305's two new rules

### (a) A `kosh` passed to a function that grows it, then read in the caller — does it see the growth?

**Yes.** `r131_ws1_paramgrow_ok.sm` (above): `grow(kk)` pushes 99 into the parameter, caller
reads `kk[0]=11, kk[1]=22, kk[2]=99, kosh_gan(kk)=3`. The caller sees the growth (length and
value). This is the v304 behaviour change, verified: the R129 probe `ws1_paramgrow.sm`, which
refused on v302/v303 (`kosh-tarke kosh_push asamarthitam`), now **compiles and runs on v305**
(`11 55`, exit 0) — an intended behaviour change, not a regression.

### (b) Two `kosh` parameters, both grown — do both propagate?

**Yes, both.** `r131_ws2_twoparams.sm`: `grow2(x, y)` pushes 99 into `a` and 88 into `b`;
caller reads `x[1]=99, y[1]=88, kosh_gan(x)=2, kosh_gan(y)=2`. Both propagate (both lengths and
both values).

### (c) A slice `k[2:5]` of a `kosh` that then grows — what does the slice see?

**You cannot hold it, so it sees nothing — the compiler refuses to store a kosh slice in a
`vitti`.** `r131_ws2_slice_then_grow.sm` (`vitti s = k[2:5]`, then grow `k`) refuses at the
slice assignment with `E_KOSH_VIBHAG` (same message as WS1 above), before any growth happens.
`r131_ws1_slice_store_nogrow.sm` confirms the refusal is **unconditional**: `vitti s = k[1:3]`
with **no growth after it at all** (just `likha(s[0])`, `likha(pankti_gan(s))`) is refused with
the same `E_KOSH_VIBHAG`. So the compiler refuses the storage outright, because it cannot know
whether a growth will happen later in the function. That is a safe refusal (not a defect — it
prevents a stale slice), but it is broader than the S1 case: it refuses slice storage even when
no growth follows, which may surprise a user who just wants to hold a slice and read it (they
must pass the slice directly to a function instead, per the hint). The expressible slice use —
passed directly, used immediately, no growth in between — works: `r131_ws2_slice_immediate.sm`
(`yog(k[2:5])=120, pankti_gan(k[2:5])=3`, `yog(k[2:])=120, pankti_gan(k[2:])=3`; hi exclusive,
no-hi runs to the end). So the brief's bullet as phrased ("a slice that then grows") has no
expressible program on v305 — it is refused at the point you would try to hold the slice. That
is itself the finding: the S1 fix (refusing slices beside growth) also prevents holding a slice
across a growth, which is a broader restriction than just "beside a call". Safe, but worth
documenting (a user holding a slice will hit `E_KOSH_VIBHAG` and may not understand why, since
no growth has happened yet in their program).

### (d) A slice with no upper bound, then growth — does the endpoint move?

**At slice creation, yes (S2 fixed). Across a later growth, the question is moot (you cannot
hold the slice — see (c)).** `r131_ws2_slice_s2.sm` tests the S2 fix directly: a slice with
omitted hi whose `lo` is a call that grows the kosh (`k[grow_it(k):]`, where `grow_it` pushes 99
and returns 1). The endpoint is the length **after** `lo` was evaluated (the v305 fix in
`r23_gen_slice`: an omitted hi is "to the end" — the length after `lo` was evaluated, not
before). First call: `yog(k[grow_it(k):]) = 149` (k was [10,20,30], `grow_it` pushed 99 → length
4, slice `k[1:4]` = [20,30,99], sum 149 — if the endpoint were the old length (3), the sum
would be 20+30=50). Second call: `pankti_gan(k[grow_it(k):]) = 4` (a second `grow_it` pushed
another 99 → length 5, slice `k[1:5]`, length 4 — if the endpoint were the old length (4), it
would be 3). So the endpoint moves to the grown length at slice creation, both times. **S2 is
fixed.** For the "hold a no-hi slice, then grow" case, see (c): `vitti s = k[2:]` is refused
with the same `E_KOSH_VIBHAG` (`r131_ws2_slice_nohi_grow.sm`), so there is no held slice whose
endpoint could move after a later growth.

### (e) A slice passed directly as an argument while another argument grows the source — ChatGPT said this crashed v303. Does it crash v305?

**No — it is refused at compile time, in both variants.** This is the S1 fix
(`r129_check_call`, `E_KOSH_VIBHAG`), and it holds:
- Call variant (`r131_ws2_s1_call2.sm`): `use_slice(k[2:5], grow_it(k))` — a kosh-made slice
  beside another argument that has a call in it — refuses: "Sutram truti [E_KOSH_VIBHAG]:
  prakriya 'use_slice' — kosh-vibhagah anyena ahvana-yuktena tarkena saha na diyate (tad
  ahvanam kosham vardhayet)" (a kosh slice is not given with another argument that has a call —
  that call might grow the kosh), hint: pass the kosh itself, or copy the slice elsewhere
  first; `kosh_kship` after.
- Grow variant (`r131_ws2_s1_growfn.sm`): `may_grow(k[2:5], k)` — a call to a `prakriya` that
  may grow (it, or one it calls, runs `kosh_kship`/`kosh_yuj`, transitively via `r129_may_grow`
  fixpoint) with a kosh-made slice as a `vibhag` argument — refuses: "Sutram truti
  [E_KOSH_VIBHAG]: prakriya 'may_grow' koshan vardhayitum shaknoti — kosh-vibhagah tasyai na
  diyate (vriddhau tasya mulyani anyatra gacchanti)" (the `prakriya` can grow a kosh — a kosh
  slice is not given to it, because on growth its values go elsewhere), same hint.
**S1 is closed.** No crash, no silent wrong — a compile refusal. (Probe-authoring note: `vitti`
is not a valid parameter type, so the second parameter in the call variant is `dasham`, not
`vitti` — the first attempt with `vitti x` failed to parse, as in R127/R128/R129.)

### (f) A `kosh` parameter grown inside a nested block — what happens when the block closes?

**The growth persists; the caller sees it.** `r131_ws2_param_block2.sm`: `grow_in_block` grows
the parameter inside a `mandapa` block (`a[1]=99, kosh_gan(a)=2`), and `grow_in_yadi` grows it
inside a `yadi` block (`b[1]=88, kosh_gan(b)=2`). Both persist after the block closes (growth is
persistent, not scratch, so block exit does not rewind it). No defect. (Probe-authoring note:
the `yadi` flag parameter is `dasham`, not `vitti` — `vitti` is not a valid parameter type.)

### Next gap in the fix — what I would look at next

The slice-storage refusal (c) is the next thing to look at, not because it is a defect (it is
safe), but because it is the broadest refusal in the new rules: it refuses storing a kosh slice
in a `vitti` even when no growth ever follows, with a message that says "if the kosh grows, its
values go elsewhere" — which is confusing when no growth happens in the program at all. A user
who writes `vitti s = k[1:3]; likha(s[0])` (no growth anywhere) gets a refusal that talks about
growth, and the hint tells them to pass the slice directly (`f(k[1:4])`) — which is the right
workaround, but the message does not say "slices cannot be stored, only passed directly". If
the design intends slices to be pass-directly-only (never stored), the message should say that
plainly, and the reference should document it. If the design intends slices to be storable when
no growth follows, then the compiler needs a narrower check (allow storage when it can prove no
growth follows, or track the slice's source kosh and refuse only the growth, not the storage).
That is a design decision for the owner, not a defect I found by probing — but it is the next
gap in the fix to decide on.

### Regressions — no regressions on v305

All 11 R129 probes re-run unchanged on v305: every result identical to v302/v303 (boundary
`11 22 33 44 11 44 55 55 11`; twoalias `11 55 11 55 11 55`; kosh-in-kosh still compile-refused
`E_KOSH_DVARA`; mandapa `11 55`; 20k_grow2 `0 10000 19999 999 1003`; multigrow `0 99999 0 99999`;
dashamgrow `0.000000 99.000000 0.000000 99.000000`; dashamfrac3 `0.500000 99.500000 99.500000`;
interleave `0 99 1000 1099`; param-index still runtime-refused `mala ank seema atikram`). All
8 R127 defects + the R128 global bypasses still hold on v305 (reassign / assign-kosh-mala /
loop → `E_VITTI_PRAKAR`; mala-cell / kosh-cell / global (both forms) → `E_KOSH_DVARA`; ternary
→ `E_KOSH_DVARA` (with the improved `'?:'` message); call-result → runtime refusal `mala ank
seema atikram`, true exit 1, re-verified by running the binary on v305). R129 OOM still refuses
on Linux under a 64 MB `ulimit` (exit 1, "kosh vardhayitum smritih na labdha — kosh yatha asit
tatha eva"). The one intended behaviour change is the R129 `ws1_paramgrow.sm` probe, which
refused on v302/v303 and now compiles and runs on v305 (`11 55`, exit 0) — that is v304 (param
growth now propagates), not a regression.

## WS3 — sign-off on v305: would I sign?

**For the compiler (Linux, the part this round attacks): yes, with polish. For v305 as a
release (including Windows, installer, and IDE): no — R132 and R133, in this same batch, name
the blockers, and they must be fixed first.**

For the compiler: no known crash or silent-wrong defect on v305 by probing (param propagation
works for one and two parameters and inside nested blocks; S1 is refused in both variants, not
crashed; S2 is fixed (endpoint after `lo` evaluated, verified 149/4); slice storage is refused
safely (though broadly); no regressions in R129/R127/R128; OOM still refuses on Linux). The
polish notes for final are: (1) delete the dead message (`msg_kosh_param_push`, line 680) and
the dead label (`.ge_call_koshpush_param_bad`) — trivial, one deletion; (2) document that kosh
slices cannot be stored in a `vitti` (pass them directly), and consider saying so plainly in the
`E_KOSH_VIBHAG` storage message (it currently talks about growth even when no growth follows);
(3) resolve the R130 block-kosh `parimana()` 96 vs 64 question (32 bytes, diagnostic only —
still open on v305, not re-tested here). None of these is a crash or a silent wrong, and none
blocks a compiler release candidate.

For v305 as a release: I would not sign, because R132 (installer does not complete — the wizard
waits unbounded on a PowerShell that stalls after "Copying Sutram files."; and two installations
coexist with the older one winning on PATH, so a student typing `sutram` gets an old version)
and R133 (the OOM path crashes on Windows with `0xC0000005` and empty output, instead of
refusing as on Linux; and the IDE leaves stale output on screen when a file is refused) are
release blockers, not compiler defects. They are in the same batch, and they stop a release even
though the compiler is clean. So my recommendation is: **compiler yes, release no (until R132
and R133's blockers are fixed)**. The release decision itself remains the owner's, as R130
said.

## NOT RUN

Windows execution (cannot run Windows here; the v305 Windows results in R132/R133 are the
tester's, not mine), browser, implementation (attack and verification only — v304/v305 fixes not
built by me), native-speaker review, full suite (no tree changes; v305 suite numbers (327,
FAIL=0) stand, not re-run here), installer payload on real Windows (reported, not independently
verified by me here), IDE GUI on real Windows (not in this round's WS list, cannot test
headless here), the exact ChatGPT R204 S1/S2 paths (the brief does not disclose them; I probed
the S1/S2 cases as described in the brief and as the v304/v305 code defines them — if Sarvam
wants the exact R204 paths confirmed, ChatGPT R204 should name them and they can be re-probed
on v305).
