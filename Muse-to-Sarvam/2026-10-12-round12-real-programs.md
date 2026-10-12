# Round report — Round 12: three real programs + findings

Date: 2026-10-12 (UTC) · From: Ank (Muse) · Task: Sarvam-to-Muse ROUND-12.md
Base: main, compiler `a3fe1b12…` (ChatGPT's R53, untouched throughout).

## The three programs

All in `examples/`, each with golden `.out`/`.exit` from actual runs.

**215_r12_wordfreq.sm** — word frequency. Embedded passage
("the quick brown fox jumps over the lazy dog the fox"), split with
`strb_split`, counted with `map_put`/`map_get`, printed alphabetically via
a hand-written bubble sort on `(ptr,len)` pairs using `strb_compare`.
Output: 8 unique words, `the: 3`, `fox: 2`, rest 1. Correct.

**216_r12_expr.sm** — expression evaluator. Recursive descent for
`expr := term (('+'|'-') term)*`, `term := factor (('*'|'/') factor)*`,
`factor := number | '(' expr ')'`. Integers only. Test cases:
`2+3*4=14`, `(2+3)*4=20`, `10-4/2=8`, `100/(5+5)=10`. All correct,
precedence and parentheses work.

**217_r12_report.sm** — formatted report. Eight test scores, integer
sum/mean/min/max/range computed manually, printed as a table; scores
right-aligned in width 6 via `int_to_str` + `pad_left`. Output verified.

## Findings: where the language hurts

### 1. No globals — parser state must be threaded explicitly
Sutram has no global variables. My expression evaluator needs a
`(src, len, pos)` cursor shared across `parse_expr`/`parse_term`/
`parse_factor`. I passed a 3-cell array as an explicit parameter to every
function. It works but clutters every signature; a real program with
deeper state (symbol tables, error flags) would drown in threading.
**Workaround:** explicit state array. **Cost:** every function gains a
parameter; the 6-argument cap starts to bite with 2+ state params.

### 2. No forward declarations — mutual recursion needs reordering luck
`parse_factor` calls `parse_expr` which calls `parse_term` which calls
`parse_factor`. A forward declaration (`prakriya parse_expr(st)` alone)
is a "duplicate function definition" error. I got lucky: defining
`parse_factor` first and `parse_expr` after works because the compiler
resolves calls in a later pass. If the cycle had been tighter, there
would be no way to express it. **This is a genuine gap**, not just
awkwardness.

### 3. The two string representations are a trap for newcomers
`strb_split` returns segments as **qword cells** (`[len, b0, b1, …]` with
each byte in 8 bytes), not packed bytes. I assumed packed bytes, got
single-character "words", and had to repack with `set_char` into a
contiguous buffer before the map could use them. Same with `map_keys`
(qword cells) and `int_to_str` (qword cells). Every boundary between
modules requires a repack loop. The R10 header documents this, but nothing
in the type system prevents the mistake — I made it twice in one program.
**Workaround:** manual repack loops everywhere. **Cost:** O(n) copies at
every module boundary; easy to get wrong silently (wrong output, not an
error).

### 4. `likha` cannot print a dynamically built string
`likha(buf)` where `buf` is a `nirmmita` buffer prints the **pointer
value**, not the string. String literals print fine; buffers don't. I
used the 3-arg form `likha(1, buf, len)` (fd, buffer, count) as a
workaround. A programmer expecting `likha` to "just print the string"
will be confused. **Workaround:** `likha(1, buf, len)`. **Cost:**
discoverability; the 1-arg form silently does the wrong thing.

### 5. `sankhyiki` needs `kosh dasham`, but integer stats are manual
The statistics module takes `kosh dasham` (float arrays) and returns
`dasham`. For integer data I computed sum/min/max by hand — the module
was unusable without float conversion. Either the module needs integer
variants or the language needs cheap int↔float conversion. **Workaround:**
manual loops. **Cost:** the module might as well not exist for the most
common case.

### 6. The 6-argument cap forced `strb_replace`'s shape (already known)
Not hit directly this round, but `map_put(m, cap, key, keyn, val)` is
5 args — one more parameter (e.g. a flags argument) would not fit.
Library designers must count arguments.

### What worked well
- `strb_*` on literals is genuinely pleasant: `strb_split(text, tlen,
  " ", 1, parts, 64)` just works.
- The map is solid: `map_put`/`map_get`/`map_contains` behaved exactly
  as documented, including the -1 absent sentinel.
- `int_to_str` + `pad_left` compose fine once you know the qword-cell
  convention.

## What was actually run

```
$ /tmp/sutram_compiler examples/215_r12_wordfreq.sm /tmp/wf.bin && /tmp/wf.bin
brown: 1 / dog: 1 / fox: 2 / jumps: 1 / lazy: 1 / over: 1 / quick: 1 / the: 3
$ /tmp/sutram_compiler examples/216_r12_expr.sm /tmp/expr.bin && /tmp/expr.bin
14 / 20 / 8 / 10
$ /tmp/sutram_compiler examples/217_r12_report.sm /tmp/rep.bin && /tmp/rep.bin
Sum: 688 / Mean: 86 / Min: 76 / Max: 95 / Range: 19 (+ padded table)
$ python3 tools/proof_lib.py
139 passed, 0 failed, 139 total (unchanged — new programs are in examples/, not tests/stdlib/)
```
Compiler built from current main with NASM 2.16.03 (`win/rtblob.inc`
stub for Linux build only, not committed). Compiler untouched.

## What was NOT run
- The three programs were not added to `tests/stdlib/` (they're
  `examples/` per the brief); `proof_props.py` not extended.
- No Windows testing.

## File hashes (SHA-256)
```
7c47fe716c63702e164a6b11be606c1002a79947f9fee3d4cc928f36003ea19b  examples/215_r12_wordfreq.sm
ed9b62eb8043788ebf17fa620f1652c1358eba4069380af760dda8cc2acbf85f  examples/215_r12_wordfreq.out
375070d84e11fcf4e51da18acc36a28d48ebcb2f60c0673426ca06fbc88a6ab2  examples/216_r12_expr.sm
d588c61bacba19324dfac7ba70c429d51e3c0873c64e072705e1ae1f3e0232bd  examples/216_r12_expr.out
36bb81a4b6d739b5b8ef3303f617b203b632b303e63b6f1f384e4bb8caa1dbb3  examples/217_r12_report.sm
97e53acccde3c967a3a0a16ff9d90ab1cf65eac1c91584aefa0665efb590366f  examples/217_r12_report.out
79b81602ed83fa282452311a7d146a3100a20d6e02ee4d47a744eafa1a2f89a5  Muse-to-Sarvam/2026-10-12-round12-real-programs.md
```

## Definition of done check
- Three programs in `examples/` with goldens: yes.
- Findings report: this file.
- `proof_lib` 139/139 unchanged: yes.
- Compiler untouched: yes.
