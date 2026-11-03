# R113-00 — A `rachana` reference beside an operator is refused (`E_RACHANA_GANIT`); Muse's bad alias was `sankhya_bindu`, now an integer dot product; the reference says what would remove `Error` (v293).

> **Correction (R115):** the integer dot product below is **wrong for a `kosh dasham`** (it multiplies float bits;
> 2.5·2.5 + 1.5·1.5 gave 0) - I tested an untyped `kosh` and missed the typed one. `sankhya_bindu` / `sankhya_dot` are
> **withdrawn in v295** (`E_PRATYAHRITA`); see R115-00.

- **Commit on `main`:** `1f706cf` (written as `98623a1` before a rebase; on top of `2065ebe`; the v292 base was `938d994`).
- **Compiler: `Sutram 1.0 (v293) - sampurna sutra`** (was v292). Linux x86-64 cloud, 2 cores, 7 GB.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `suite: NO-EXPECTATION=4  PASS=297  (301 run)`, FAIL=0** (295 + goldens 328, 329).
- **Gates (`sh tools/gates.sh`, Xvfb display, Linux): 60 PASS / 1 FAIL / 1 NOT-RUN** (FAIL: `installer version`, `payload v243 inside Sutram-Setup.exe`; NOT-RUN: Windows execution).**
- **The guard, origin/main (v292) → v293, 707 programs** (`evidence-r113/guard.txt`):
  - **Linux ELF: 564 byte-identical, 141 refused identically, 0 DIFFER, 2 new** (examples 328, 329).
  - **Linux PE: 564 byte-identical, 141 refused identically, 0 DIFFER, 2 new.**
  - **The Windows compiler under Wine: 564 byte-identical, 141 refused identically, 0 DIFFER, 2 new; its 1128 outputs are byte-identical to the Linux compiler's PE outputs.****

## WS1 - the `rachana` refusal, and one premise to correct first

**A `rachana` is not a type a variable has.** The reference says it outright - *"variables carry no type"*:
`vitti p = nirmmita(24)` is an address in an ordinary `vitti`, and `p.x` finds `x` by name. So there was no
"`rachana` value" for the compiler to refuse. It has to know a record by **how the name is used**, and v293 does
this:

> **A `rachana` reference is a name whose field the `prakriya` reads or writes anywhere in its body (`p.x`), or the
> first parameter of a method (`prakriya Bindu.chal(swa, ...)`).** Such a bare name beside any operator is
> **`E_RACHANA_GANIT`**, as a bare `kosh` is `E_KOSH_GANIT` and a bare `mala` is `E_MALA_GANIT`.

```
Sutram Error [E_RACHANA_GANIT]: rachana-upari ganitam tulana va na sambhavati - rachana sankhya na
Sanket: p.x tasya avayavasya mulyam - tani tulyantam
```

| two records, both with x = 3 (`evidence-r113/probes-v292-v293.txt`) | v292 | v293 |
|---|---|---|
| `p == q` | **0** (two addresses) | refused |
| `p != q`, `p < q` | **1**, **1** (address order) | refused |
| `p + q` | **280068630773776** | refused |
| `p asti p` | 1 | refused |
| `swa == o` in a method that never reads `swa`'s field | 1 | refused (the receiver rule) |
| `p.x + q.x`, `p.x == 3`, `p.x < q.x` | 7 1 1 | **7 1 1, the same bytes** |

**Every program in the tree compiles to the same bytes** - I compiled all 705 with both compilers before the guard
(0 differ), and the guard agrees. Nothing in the tree compared, ordered or added records.

**Documented** (`LANGUAGE-REFERENCE.md` §5, after the operand table): **what `==` will mean on a `kosh`, a `mala` and a
`rachana` - the same object, as ChatGPT R182 recommends - and why all three refuse today**: identity needs a stable
identity for a `kosh` that grows (R178's descriptor), and a refusal is safe until then. Ordering and arithmetic
stay refused for good. **What the rule does not see:** a copy that never touches a field (`vitti q = p`, then
`q == r`) - the same limit a `kosh` or `mala` given a second name has (R182 says so too).

**Not changed, found while testing:** a comparison refusal (`==`, `<`) prints no `line:column`, an arithmetic one
does (`add.sm:8:13:`) - comparison nodes store a line number where the others store a source position. It is the
same for `E_MALA_GANIT` and `E_KOSH_GANIT` on v292; fixing it changes existing refusal goldens, so it is reported,
not done.

## WS2 - Muse's one bad alias is `sankhya_bindu`, and it is fixed

Muse R108: *"the name is right, the body cannot deliver a dot for any Sutram-constructible input"*. Confirmed in
the source: it read 16 bytes from each pointer as **four 32-bit floats** (`movups`, `mulps`, two `haddps`) and
returned their bits as an integer. Nothing in Sutram holds 32-bit floats.

**The fix, and why integer:** a `mala` or `kosh` cell is an 8-byte **integer** - I checked: a `dasham` stored into
one is converted exactly (`3.0` → `3`) or refused (`2.5` → `E_DASHAM_VITTI`), and there is no `dasham` array. So the
dot product a Sutram program can mean is the integer one:

> **`sankhya_bindu(a, b, n)`** = `a[0]·b[0] + … + a[n-1]·b[n-1]` over 8-byte cells - a `mala`, a `kosh`, a
> `nirmmita` buffer. It wraps like every Sutram integer (`a + 1` at the maximum wraps too). `n ≤ 0` gives 0. Like
> `smaran_pratilip`, `n` is not checked against the buffers.

Golden **329**: `1·4 + 2·5 + 3·6 = 32`, the first two `14`, none `0`, a `kosh` with itself `113`. It is a 7-instruction
loop, no call. **It now takes three arguments**: `sankhya_bindu(a, b)` (and the old `sankhya_dot(a, b)`) is refused
when compiled. That is the one behaviour change: a two-argument call used to compile and return meaningless bits,
and nothing in the tree made one.

**The rest of the family is the same kind of thing, and I did not change it:** `sankhya_yog(dst, a, b)` and
`sankhya_gunan(dst, a, b)` add and multiply **four 32-bit float lanes** in raw memory (`addps`, `mulps`). The
reference called them "integer add" and "integer multiply", which they never were; it now says what they do. They
need the same decision `sankhya_bindu` got - an integer form, or a removal - and that is yours.

## WS3 - the note on `Error`

`LANGUAGE-REFERENCE.md` §4b now says why one English word remains, and **what would remove it**: the owner's
exception for this one token in all eleven packs, and accepting that every program carrying a run-time message
changes in those bytes only. **R114 has now given exactly that**, and it follows this commit.

## Not done

- Identity semantics for `==` (documented as the meaning, not built), and a type on variables.
- The location on comparison refusals; `sankhya_yog` / `sankhya_gunan`.
- Native-speaker review of `E_RACHANA_GANIT`'s text: NOT RUN.
- Not touched: `backups/`, `Windows-to-Sarvam/`, every pack file, `MEMORY-DECISION.md`, `Muse-to-Sarvam/`.
