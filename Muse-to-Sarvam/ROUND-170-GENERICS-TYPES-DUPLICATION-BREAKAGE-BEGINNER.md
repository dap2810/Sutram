# ROUND-170 — generics: what the compiler knows, what the duplication is, what would break, and the beginner

**Base:** main at v315, tip commit `cb132a77` · **Deliver into:** `Muse-to-Sarvam/`

**Read only. Nothing compiled or run.** Every line number below was re-grepped
on this tree; every count re-derived from it. Paths are relative to the repo
root.

Note on the brief's delivery line: "Deliver into: `Muse-to-Saram/`" is a typo
for `Muse-to-Sarvam/`; not followed literally. The round is delivered into
`Muse-to-Sarvam/`, as every round before it.

---

## Task 1 — what does the compiler know about types today

### (1) Does a kosh carry an element type — runtime or compile time?

**No, at runtime. Yes, exactly one bit of it, at compile time.**

The descriptor has no type field. `src/r65_arena.inc:557-559` (the ROUND-127
comment): "A kosh value is a descriptor d that never moves: [d-16] length,
[d-8] capacity (R82's line, slot and generation before them when on), [d] the
elements, [d+8] the bytes of the region the elements are in." The growth code
reads and writes only those four fields (`r127_emit_grow`, `:577-630`). The
R82 header is three *more* qwords before them — line, liveness slot,
generation (`r82_emit_kosh_header`, `src/sutram_compiler.asm:10847-10852`) —
so the header is 32 bytes (4 qwords) without R82 and 56 bytes (7 qwords) with
R82 on; in neither case is any qword a type.

There are exactly two element types a kosh can have — integer/raw qword, or
IEEE-754 binary64 (`dasham`) — and the compiler records which one in:

1. **The AST_DECL type marker, `[node+32]`.** The parser sets it in `.ps_kosh`,
   `src/sutram_compiler.asm:15000-15057`: `rdx = 2` ("AST_DECL marker 2 =
   integer/raw kosh"), `rdx = 3` ("marker 3 = kosh dasham") when the
   declaration is written `kosh dasham name`. The scalar markers live in the
   same slot: 0 = integer `vitti`, 1 = `dasham` (`:15090`, `:15105`).
2. **Per-function name lists.** `mark_kosh_var` (`:27728`) puts the name in
   `kosh_vars` (`:1549`, cap 256); `mark_float_kosh_var` (`:27676`)
   additionally puts it in `float_kosh_vars` (`:1561`) when the marker is 3.
   `gen_decl` does both at `:19280-19290` (`.gs_decl_kosh`): "Marker 3 adds
   compiler-side binary64 element typing; runtime layout is identical." The
   lists are per generated function and reset per function (`:18068-18071`).

That one bit is *enforced* at every boundary where a value enters a kosh:
`kosh_kship` (push), `.ge_call_koshpush`, `:22427+` (converts the value to the
kosh's element type before storing); element store through `k[i] = v`,
`.gs_ai`, `:19710-19760` (same probe, 0 = not kosh, 1 = integer kosh,
2 = float kosh); a kosh passed to a typed parameter, `gen_typed_call_arg`,
`:27326-27364` (`PARAM_KOSH` refuses a float kosh and `PARAM_KOSH_DASHAM`
requires one, else `msg_kosh_param_type`).

There is no third element type: no string kosh, no pointer kosh, no nested
kosh. A kosh of pointers is just a raw (marker 2) kosh whose qwords happen
to be addresses — the compiler cannot tell it from a kosh of integers. And
the marker lives only in the AST node (transient) and in the per-function
name lists (compile-time only); nothing about it survives into the emitted
program except the *conversions* it caused.

### (2) Does the symbol table record a type per variable, and how many types?

**No. The symbol table records no type at all. Kind is derived on the fly
from separate per-kind name lists, and there are five kinds (+ one
meta-kind), plus two orthogonal bits (float, string) tracked elsewhere.**

The variable table is name + offset only: `VAR_TABLE_CAP equ 256 ; entries;
16 bytes each` (`:51`); `var_table resb VAR_TABLE_CAP * 16 ;
[name_ptr(8)][offset(8)]` (`:1535`). Registration (`:18568-18576`, and the
parameter loop at `:18584-18618`) writes exactly those two qwords. There is
no kind/type field in the table, and no kind field in any AST node for a
variable.

`r126_kind`, `:27884-27918`, returns a kind 1–5 for a name by probing the
per-kind name lists in fixed precedence (slice, float kosh, kosh, array,
local scalar), or 0 if the name is not bound yet. The kind names are the
strings at `:607-612`: 1 `vibhag`, 2 `kosh dasham`, 3 `kosh`, 4 `mala`,
5 `sankhya (smriti-sthanam va)` — "a number (or a memory address)".
`r126_value_kind` (`:27920-27975`) adds kind 6, `kadachit kosh` (`:612`),
"maybe a kosh": a value that is a kosh on some paths and not on others —
a property of an *expression*, never of a variable.

| kind | what it is | where the membership lives |
|---|---|---|
| 1 `vibhag` | a slice `a[lo:hi]` | `r23_slice_vars` (256 names), `src/r23_capabilities.inc:416-417`; mark `:421`, test `:438`. Slices are never declared. |
| 2 `kosh dasham` | kosh of binary64 | `float_kosh_vars` (`:1561`) **and** `kosh_vars`; mark `:27676`, test `:27696`. |
| 3 `kosh` | kosh of integer/raw qword | `kosh_vars` (`:1549`, cap 256); mark `:27728`, test `is_kosh_var` at `:29431`. Kosh parameters are additionally in `kosh_param_vars` (max 6, `:68`, `:1558`). |
| 4 `mala` | fixed-size array (`pankti`) | `array_vars` (`:1547`, 256 entries); mark `mark_array_var` at `:27576`, test `is_array_var` at `:27592`. |
| 5 `sankhya` | number or raw address | the default: any `var_table` local in none of the lists above (`r126_is_local`, `:27853`). This one kind conflates `vitti`, `dasham`, pointers, and rachana references. |

Enforcement: `r126_bind` (`:28829-28880`) — a name keeps one kind for its
whole prakriya; a second binding of a different kind is `E_VITTI_PRAKAR`
(`r126_fail_kind`, `:28272`).

The things the brief names, checked one by one:

- **`vitti` / `dasham` (scalar int vs float).** Not r126 kinds — both are kind
  5. The distinction is a *separate* name list: `float_vars` (`:1562`),
  `mark_float_var` at `:26813`, `is_float_var` at `:26833`, seeded from the
  AST_DECL marker 1 in `gen_decl` (`:19227-19231`) and from typed
  parameters (`:18584-18618`). Expressions are classified by
  `expr_is_float` (`:26890+`), and a prakriya's return float-ness is the
  only per-function type fact stored in a table (`func_defs` node, `[+40]`,
  set at `:12104` / `:27277`).
- **A text value.** Not an r126 kind either. String-ness is a flow-derived
  bit: `rfx2_bits` (`:1565-1568`, "1 = given a string, 2 = given anything
  else..., text iff exactly 1"), computed for the whole function by
  `rfx2_analyse`, read by `rfx_kind` (`:9516-9519`) and `is_str_var` /
  `is_mixed_var` (`:9293-9330`). There is also a per-slot byte, `str_flags`
  (`:1564`, "1 when the var_table slot holds a string"). A string literal
  is `AST_STR` (`:105`).
- **`pankti`.** `KW_PANKTI equ 28 ; mala = array (garland/row)` (`:183`).
  `pankti` is a keyword spelling of the same declaration as
  `vitti name[N]`: the array path `.ps_decl` (`:14920-14960`) builds an
  `AST_DECL` with the size expression in `[+24]` and sets *no* type marker
  — kind 4 comes only from `mark_array_var` in `.gs_decl_array`
  (`:19393`). There is no dasham-mala declaration form: `.ps_fdecl`
  (`:15063-15110`, the `dasham` declaration) has no `[N]` path, so a
  `dasham` array cannot be declared at all.
- **A `rachana`.** No kind, no per-variable binding. Rachana *types* live in
  their own table, `rachana_defs` (`:1668`: `RACHANA_CAP` 16 entries × 256
  bytes — `[name_ptr(8)][field_count(8)]`, then up to 15 fields of
  `[name_ptr, offset]` 16 bytes each; caps at `:59-60`), filled by
  `.ps_rachana` (`:15912-16015`). A variable holding a rachana value is kind
  5 (a raw address). Field access resolves the offset by *field name* looked
  up across all rachana definitions (`:14132-14189`); the comment at `:9338`
  states it plainly: "Variables carry no type, so a rachana reference is
  known by its use: a name whose field the function reads or writes (p.x)."
  Two rachanas sharing a field name at different offsets are refused
  (`E_AMBIGUOUS_FIELD`, `:343`).
- **Parameters.** The only place a per-parameter type is stored as a value:
  `func_param_types` (`:1636`, one byte per parameter slot), with the enum
  at `:69-73`: `PARAM_RAW equ 0` (untyped/integer scalar), `PARAM_DASHAM
  equ 1`, `PARAM_KOSH equ 2`, `PARAM_KOSH_DASHAM equ 3`, `PARAM_VIBHAG
  equ 4`. The parser sets them from the `dasham` / `kosh` / `kosh dasham` /
  `vibhag` prefixes (`:15266-15340`); `func_param_type` (`:26997-27090`)
  reads them back; `gen_all_functions` seeds the name lists from them
  (`:18584-18618`).

So "how many types": the r126 system has **5 kinds** (6 counting the
expression-only "maybe kosh"); the scalar int/float split is a second,
orthogonal bit; string-ness is a third, flow-derived bit; and a rachana is
a named record type with no per-variable binding at all. A variable's full
compile-time description is therefore a *combination* — e.g. "kind 3, float
elements" or "kind 5, float scalar" or "kind 5, string everywhere" —
assembled from four different tables at each use site, never stored as one
value.

### (3) How does the compiler currently tell sort_int from sort_text?

**It does not — because neither function exists, and because call resolution
is by name only, with arity as the only check on user functions.**

A whole-tree grep for `sort_int|sort_text` returns exactly one hit: the
ROUND-170 brief itself. There is no text sort and no dasham sort anywhere in
`lib/`, `examples/`, `src/`, or `docs/`.

The real sorts are per-algorithm, not per-type. `lib/shreni.smlib`
(header, `:1-5`: "Operates on `mala` integer arrays, in place") defines four
sorts, all taking untyped `(a, n)` and all comparing with signed integer
`>` / `<` on raw qwords: `budbud_shreni` (bubble, `:13`),
`shankh_shreni` (shell, `:120`), `nivesh_shreni` (insertion, `:148`),
`mil_shreni` (merge, `:223`, with helper `mil_shreni_punar` `:174`).
`suchi_shreni(l)` (`lib/suchi.smlib:214`) just delegates to `mil_shreni`.

Call resolution, read from the source:

1. **Lexer.** `lookup_builtin` (`:32959-33009`) linearly scans `bn_table`
   (`:901-975`, 24-byte rows: name pointer, token type, builtin id) with
   `strcmp` and returns the builtin id; the lexer (`:7174-7200`) then tags
   the word `TOK_BUILTIN`, otherwise `TOK_IDENT`. Pure name matching.
2. **Parser.** A call becomes `AST_FUNCALL [name_ptr][arg_count][arg1..arg6]`
   (`:17669`). No type is recorded on the node.
3. **Arity only.** `r7_check_arity` (`:13983-14080`, run after the whole
   program is parsed, called at `:7887`) compares each call's arg count
   against `r7_defs` (name, param count) by `strcmp` on the name; a mismatch
   is `E_ARITY` (`:345-348`). Duplicate definitions are refused
   (`parse_error_kind = 2`, `:1680`). There is no second definition of the
   same name to dispatch between, and no name mangling.
4. **Codegen.** `.ge_funcall` (`:21560+`) evaluates the arguments left to
   right through `gen_typed_call_arg`, pops them into `rdi, rsi, rdx, rcx,
   r8, r9`, and emits one direct `call rel32` to the name recorded in the
   patch list (`:21760+`). A call through a variable goes through
   `r23_call_is_indirect` / `r23_emit_indirect_call` instead — again by name,
   never by type.
5. **Builtins.** Arity is a fixed table, `r54_builtin_arity_table`
   (`:279-327`; e.g. `likha` 1–6 args, `kosh_push` 2, `kosh_len` 1), checked
   by `r54_builtin_arity_ok` at parse time (`:17762`).

The only argument-kind checks that exist:

- **`gen_typed_call_arg`** (`:27300-27401`): for a `PARAM_KOSH` /
  `PARAM_KOSH_DASHAM` parameter the argument must be a bare `AST_VAR` that
  `is_kosh_var`, with matching float-ness, or the compile fails; for
  `PARAM_VIBHAG` it must be a slice. For scalar parameters it calls
  `expr_is_float` on the source and `emit_scalar_type_conversion`
  (`:27412-27424`) — an int↔dasham *conversion*, not a dispatch. An untyped
  (`PARAM_RAW`) parameter accepts anything, converting dasham to int.
- **The r126 doors**: a kosh to an untyped parameter is refused
  (`r126_check_untyped_arg`, `:29343`); a kosh as a non-first builtin
  argument is refused (`r126_check_builtin`, `:29279`).
- **Foreign functions only**: `r33_kind3` (`src/r32_ffi.inc:566-567`) maps a
  declared foreign signature to 0 = i64, 1 = f64, 2 = ptr, and a mismatch is
  `E_FFI_KIND` (`:759-760`).

Type-directed dispatch that *does* exist — all of it per-builtin,
per-call-site, none of it applying to user prakriyas:

- **`likha`.** `.ge_call_likha` (`:22788+`) splits first by *arity* (1, 2, or
  3–6 values), then for one argument: an `AST_STR` literal prints inline
  (`:23000+`); otherwise `rfx_kind` == 1 (a string value) rewrites the call
  to `BN_SHABDA` (`:22995-23000`); otherwise `expr_is_float` selects the
  float printer (`:23075+`); otherwise the integer decimal printer
  (`:23107+`). One name, three behaviours, chosen per call site.
- **Arithmetic.** `binop_needs_float` (`:27425`): if either operand of
  `+ - * /` or a comparison `expr_is_float`, both operands are converted to
  f64 and the float opcode is emitted; otherwise the integer opcode.
- **String operators.** `rfx_check_str_binop` (`:9496+`) rewrites string
  `==`/`!=` to `vartani_tul` and string `+` to `BN_VYOJ`, and refuses a
  string beside a non-string.
- **Kosh builtins.** `.ge_call_koshpush` (`:22427+`) converts the pushed
  value to the kosh's element type. `kosh_pop` / `kosh_peek` /
  `kosh_dequeue` share one arm selected by builtin id at compile time
  (`:22300-22330`, comment: "this is compile-time selection, not a generated
  conditional branch").

Verdict, as the brief anticipates: **for user prakriyas there is no type
information to build generics on.** Resolution is name → arity → (for the
five `PARAM_*` kinds) a kosh/vibhag kind check or an int↔float conversion.
A single `sort` selected by argument kind could not be built on the
user-function path today; it would need either a new dispatch mechanism or
a new builtin arm.

### (4) Functions already generic in effect

**Yes — a whole family, all of them operating on raw 64-bit cells. But two
of the three names in the question are not library functions at all.**

Correction first: `kosh_gan` is the primary name of `kosh_len`:
`r111_koshlen db "kosh_gan"` (`:1066`), builtin id `BN_KOSHLEN equ 39`
(`:232`). `kosh_iksh` is the primary name of `kosh_peek`:
`r111_koshpeek db "kosh_iksh"` (`:1070`), `BN_KOSHPEEK equ 44` (`:237`).
`parimana` is builtin `BN_PARIMANA equ 47` (`:244`). None of the three is
among the 310 `prakriya` definitions. They are, however, the type-agnostic
core: `kosh_len` / `kosh_cap` / `kosh_empty` / `kosh_clear` read only
descriptor fields (`.ge_call_koshlen` `:22235`, `.ge_call_koshcap` `:22258`,
`.ge_call_koshclear` `:22158`, `.ge_call_koshempty` `:22192` — `[rax-16]`
length, `[rax-8]` capacity); `kosh_pop` / `kosh_peek` / `kosh_dequeue`
move one raw qword out of the elements (`.ge_call_koshpop`, `:22281-22360`);
`parimana` counts bytes (`.ge_call_parimana`, `:23892+`). The single
exception is `kosh_kship`, which converts the value to the element type.
`pankti_len` (`BN_PANKTILEN equ 36`, `:229`) likewise reads only the hidden
count header of a mala.

Generic in effect, in the 310 (**46 functions**): "generic in effect" means
the body only moves, copies, counts, or `==`-compares raw 64-bit cells —
never ordering-compares, arithmetises, or prints them. All take untyped
parameters, so the compiler imposes no element type at the call boundary
either (with the dasham caveat below).

- **`lib/mala.smlib` (7)** — raw qword arrays via `likh8`/`pad8` (header
  `:1-7`: "Each element is 8 bytes (one integer)"): `mala_sangrah` `:20`
  (store), `mala_grah` `:29` (load), `mala_purn` `:36` (fill with a value),
  `mala_pratilip` `:49` (copy n qwords), `mala_sangrah_surakshit` `:75`
  (bounds-checked store), `mala_grah_surakshit` `:87` (bounds-checked load),
  plus `mala_nava` `:8` (allocate n qwords).
- **`lib/shreni.smlib` (4)**: `vinimay` `:6` (swap two cells),
  `viparyay_mala` `:28` (reverse, via `vinimay`), `anwesh_sarak` `:77`
  (linear search, `==` only), `gan` `:87` (count occurrences, `==` only).
- **`lib/suchi.smlib` (26)** — lists, stacks, queues over qword cells
  (header `:1-11`: "Elements are QWORD CELLS (the mala/kosh convention),
  not byte strings"): lists `suchi_srij` `:46`, `suchi_vardh` `:67`,
  `suchi_khip` `:87`, `suchi_grah` `:100`, `suchi_sangrah` `:110`,
  `suchi_maap` `:122`, `suchi_nivesh` `:128`, `suchi_apanay` `:152`,
  `suchi_vinimay` `:173`, `suchi_viparyay` `:193`, `suchi_rikta` `:288`,
  `suchi_antah` `:300` (`==` only), `suchi_kramank` `:313` (`==` only);
  stacks `chay_khip` `:328`, `chay_apanay` `:334`, `chay_avalok` `:351`,
  `chay_rikta` `:365`; queues `avali_srij` `:384`, `avali_pravesh` `:407`,
  `avali_nishkas` `:441`, `avali_avalok` `:459`, `avali_tak_mala` `:478`,
  `avali_antah` `:494` (`==` only), `avali_rikta` `:511`,
  `avali_shunya` `:524`, `avali_maap` `:530`.
- **`lib/phal.smlib` (6)** — a Result is a 2-cell mala `[ok, value]`; the
  value cell is moved as a raw qword: `phal_siddhi` `:33`, `phal_dosh`
  `:41`, `phal_asti_siddhi` `:49`, `phal_mulya` `:56`, `phal_mulya_va`
  `:62`, `phal_se_siddhi` `:69`.
- **`lib/brihat.smlib` (2)**: `brihat_shunyank` `:13` (zero n qwords),
  `brihat_pratilip` `:88` (copy n qwords).
- **`lib/khand.smlib` (1)**: `khand_pratilip` `:81` (byte copy via
  `akshar`/`akshar_rakh`) — generic over bytes, the same shape at byte
  granularity.

That is 7 + 4 + 26 + 6 + 2 + 1 = **46** of the 310.

The dasham caveat — generic in the body, not at the call boundary: these
functions are generic over integers and pointers (addresses), **not** over
`dasham` values. An untyped (`PARAM_RAW`) parameter converts a dasham
argument to its integer part before the body sees it
(`gen_typed_call_arg`, `:27326-27349`, scalar path through
`emit_scalar_type_conversion`). The `suchi` header says it outright
(`lib/suchi.smlib:1-11`): "dasham elements are NOT supported — an untyped
parameter truncates a dasham argument to its integer part." A dasham bit
pattern already sitting in a `vitti` would survive `mala_*`'s raw `likh8` /
`pad8` moves untouched, but no caller can put one there through an untyped
parameter. And `==` on raw cells compares bit patterns, not float values
(`-0.0` vs `0.0` differ as bits; NaN never equals itself as a float) — so
`gan` / `anwesh_sarak` / `suchi_antah` are equality-generic, not
float-correct.

Near-misses: look generic, are not — all four sorts and the order
statistics (`laghu` `:39`, `adhik` `:53`, `yog` `:66`,
`asti_kramabaddha` `:98`, `dwi_anwesh` `:108`, plus the four sorts —
signed integer `<` / `>` / `+`; on dasham bit patterns the ordering is
wrong, on pointers or text addresses meaningless); the per-type duplicate
pairs (e.g. `sankhyiki.smlib`: `yoga` / `madhya` / `laghutama` /
`adhikatama` / `vyapti` / `prasaran` over `kosh dasham` (`:16-65`) beside
`purna_yoga` / `purna_madhya` / `purna_laghutama` / `purna_adhikatama` /
`purna_vyapti` / `purna_prasaran` over untyped arrays (`:131-182`) —
counting those is Task 2); `likha` on numbers vs text (dispatch on kind,
not genericity: one name, three behaviours, chosen per call site);
`brihat_tul` (`lib/brihat.smlib:101`, `>` / `<` on limbs: correct only
because big-int limbs are unsigned magnitudes in a fixed order);
`kalana.smlib` / `samanvaya.smlib` (explicitly typed `kosh dasham`
parameters, the opposite of generic); string functions (`khand.smlib`,
`varna.smlib` — generic over *bytes*, but they assume NUL-terminated
byte strings and byte-wise comparison).

**Task 1 verdict.** A kosh carries no element type at runtime, but the
compiler tracks exactly one element-type bit at compile time (int/raw vs
binary64). The symbol table records no type at all; kind is derived on the
fly from five per-kind name lists. Call resolution is name-only plus arity;
`sort_int`/`sort_text` do not exist. And genericity already exists in
practice — 46 of the 310 only move, copy, count, or `==`-compare raw
64-bit cells — but only over integers and pointers, so the generic core
the design can build on is a qword core, not a value core.

---

## Task 2 — the duplication, counted

### Recount — the library on this tip

Method: `grep -c '^prakriya '` per file in `lib/`; cross-checked with
`grep -c 'prakriya'` per file (every mention of the word is a definition
line — no mentions in comments, no other definition keyword). 302
definitions carry a `{` on the definition line; 8 are braceless one-liners
(`ank.smlib` 2, `sadhan.smlib` 4, `varna.smlib` 2). No name is defined twice
(`uniq -d` over all 310 names is empty).

| module | `prakriya` | module | `prakriya` |
|---|---:|---|---:|
| aadhar | 2 | patra | 3 |
| ank | 10 | phal | 14 |
| anukram | 5 | roop | 23 |
| brihat | 13 | sadhan | 7 |
| chandas | 6 | samanvaya | 11 |
| ganit | 18 | sangrah | 14 |
| ganita | 27 | sankhyiki | 16 |
| gudh | 2 | shreni | 14 |
| kalana | 6 | suchi | 34 |
| khand | 22 | vakyank | 6 |
| madhava | 5 | varna | 27 |
| mala | 8 | **total** | **310** |
| nighantu | 17 | | |

24 modules, 310 definitions. **The brief's 310 is confirmed on this tip.**

### Method — what counts as a duplicate

Every one of the 310 bodies was read (a text-similarity pass over
parameter-renamed bodies was used only as a lead list; every grouping below
was verified by reading both bodies, and name-similar pairs the similarity
pass did not flag were checked by family as well).

- **Duplicate (Tier A):** two or more separate implementations of the same
  algorithm with the same results on all inputs, differing only in (a)
  element type (`vitti` vs `dasham`, byte vs qword cell), (b)
  container/representation (raw `(pointer, n)` array vs `kosh` vs list
  descriptor vs raw pointer, byte string vs char-code cell array), (c) a
  value that could be a parameter (fixed base 10 vs base parameter, fill
  value 0 vs fill parameter, not-found value −1 vs default parameter,
  padding side, sign character), or (d) inessential structure (loop written
  inline vs delegated to a helper, guard placed before vs after a
  declaration). A group of size *n* collapses to 1, saving *n* − 1.
- **Wrapper/alias (Tier B):** a function whose body only delegates to one
  other library function (possibly fixing some arguments or unpacking a
  descriptor), adding no algorithm of its own. Each collapses to 0 — the
  generic replacement absorbs its role — saving 1, except the `maap` alias
  pair, which collapses 2 → 1 (saving 1; both alias the same builtin).
- **NOT a duplicate:** same loop shape but a different operation, a
  different comparison/predicate, a different overflow convention, a
  different failure convention (return −1 vs `ok` flag vs abort vs
  saturate), a different return convention (index vs boolean, value vs `ok`
  flag), a different element stride that changes what is read, or an
  inverse operation (encode vs decode, pack vs unpack). A shared skeleton
  is not a shared algorithm.
- **Trivial accessors (excluded, 0 saving):** one-line field reads,
  one-line emptiness predicates, and one-line builtin aliases. Different
  descriptors happen to have the same layout, but a generic cannot merge a
  read of field 1 of a list with a read of field 1 of a result cell — there
  is no shared algorithm there, only a shared line shape. (10 functions.)

### Tier A — separate implementations, same algorithm (40 groups, 86 functions, saving 46)

| # | group | members | n | what varies |
|---|---|---|---|---|
| G1 | sum | `shreni:yog` :66; `sankhyiki:purna_yoga` :131; `sankhyiki:yoga` :16; `mala:mala_yog` :62 | 4 | element type (`vitti` vs `dasham`) and container: raw `(a, n)`, raw `(xs, n)`, `kosh dasham`, raw pointer via `pad8`. `yog` and `purna_yoga` are line-identical after parameter renaming (verified: the bodies at `shreni:66-76` and `sankhyiki:131-141` differ only in the parameter name). |
| G2 | minimum | `shreni:laghu` :39; `sankhyiki:purna_laghutama` :148; `sankhyiki:laghutama` :34 | 3 | `vitti` raw array (×2) vs `dasham` `kosh`; guard placement only. |
| G3 | maximum | `shreni:adhik` :53; `sankhyiki:purna_adhikatama` :161; `sankhyiki:adhikatama` :47 | 3 | As G2, with `>`. |
| G4 | mean | `sankhyiki:madhya` :27; `sankhyiki:purna_madhya` :142 | 2 | `dasham` `kosh` (float division) vs `vitti` raw array (truncating integer division); both delegate to their own sum (G1). |
| G5 | range (max−min) | `sankhyiki:vyapti` :60; `sankhyiki:purna_vyapti` :174 | 2 | `dasham` `kosh` vs `vitti` raw array; both delegate to their own min/max (G2/G3). `purna_vyapti` adds an `n <= 0` guard. |
| G6 | dot product | `sankhyiki:bindu_gunan` :100; `samanvaya:adish_gunan` :136 | 2 | Nothing except the error-message text (function name). Same `kosh dasham`, same equal-length abort, same loop. |
| G7 | square root (Newton, `dasham`) | `madhava:madhava_vargmool` :13; `sankhyiki:sankhyiki_vargmool` :82 | 2 | One line: `madhava_vargmool` clamps the start guess to 1.0 when `v < 1.0`; otherwise identical (same `v <= 0` guard, 1000 iterations). Bit-identity of results is NOT established by reading — see Could-not-determine. |
| G8 | square | `ganit:varg` :7; `ganit:vargit` :15 | 2 | Nothing. Line-identical (verified: bodies differ only in the name and one comment line), same −1 overflow refusal, two names. |
| G9 | clamp | `ank:seemit` :78; `ganit:ganit_seemit` :237 | 2 | Nothing. Line-identical, two names. |
| G10 | absolute value (abort on MIN) | `ganit:nirapeksh_mulya` :34; `ganita:ganita_nirapeksh` :92 | 2 | Nothing except the error-message text (function name). Both abort on MIN, else `\|x\|`. |
| G11 | popcount | `ganit:ekanka_gan` :209; `chandas:guru_gan` :98 | 2 | Nothing. Same `yavat (x > 0)` bit-count loop; both return 0 for negatives. |
| G12 | fill | `mala:mala_purn` :36; `brihat:brihat_shunyank` :13 | 2 | Fill value is a parameter (`val`) vs fixed 0. Same loop, same stride, same return. |
| G13 | copy qwords | `mala:mala_pratilip` :49; `brihat:brihat_pratilip` :88 | 2 | Nothing. Line-identical `likh8`/`pad8` copy loop, two names. |
| G14 | reverse array | `shreni:viparyay_mala` :28; `suchi:suchi_viparyay` :193 | 2 | Container (raw array vs list descriptor), swap inline vs via `vinimay`, return 1 vs no return. Same two-pointer reversal. |
| G15 | bounds-checked read | `suchi:suchi_grah` :100; `mala:mala_grah_surakshit` :87 | 2 | Container (list descriptor vs raw pointer + `n`); both return 0 out of range, else the element. |
| G16 | bounds-checked write | `suchi:suchi_sangrah` :110; `mala:mala_sangrah_surakshit` :75 | 2 | Container as G15; both return 1 on success, 0 out of range. |
| G17 | contains (linear scan) | `suchi:suchi_antah` :300; `suchi:avali_antah` :494 | 2 | Container (list vs queue); queue indexes circularly `(head + k) % cap`, list linearly. Same scan, same 1/0 return. |
| G18 | clear | `suchi:suchi_rikta` :288; `suchi:avali_rikta` :511 | 2 | Queue version additionally resets the head index to 0. Same zero-the-cells loop. |
| G19 | create container | `suchi:suchi_srij` :46; `suchi:avali_srij` :384 | 2 | Queue descriptor has one extra field (head index, initialised to 0). Same allocation pattern and guards. |
| G20 | map get, not-found value | `nighantu:nighantu_grah` :159; `nighantu:nighantu_grah_mool` :312 | 2 | Not-found return is the constant −1 vs a `def` parameter. Bodies otherwise identical (same 32-byte key cap, same slot lookup). |
| G21 | map key enumeration | `nighantu:nighantu_kunjika` :383; `nighantu:nighantu_kunjika_ashtak` :417 | 2 | Output representation: length-prefixed char-code cell segments (via `khand_mukt`) vs length-prefixed byte segments (inline byte copy). Same slot traversal. |
| G22 | integer → decimal text | `roop:roop_ank` :32; `roop:roop_ank_aadhar` :73; `vakyank:ank_tak_varna` :15 | 3 | Base fixed at 10 vs base parameter; output representation byte string vs char-code cells; sign emitted (`ank_tak_varna`, and `roop_ank_aadhar` via its wrappers) vs not (`roop_ank`/`roop_ank_aadhar` emit digits of `\|val\|` only); MIN handled by delegation to `roop_ank_aadhar` vs a literal digit table — same emitted text in all cases read. |
| G23 | sign-prefixed integer → text | `roop:roop_chinhit` :609; `roop:roop_chihna_akshar` :646 | 2 | The prepended sign character is the literal `+` (43) vs a `signch` parameter. Bodies otherwise identical. |
| G24 | pad text | `roop:roop_purti_vam` :252; `roop:roop_purti_dakshin` :285; `roop:roop_purti_madhya` :319 | 3 | Placement only: pad left, pad right, pad split left/right (`left = npad / 2`). Same no-op branch when `width <= count`, same terminator. |
| G25–G40 | the 16 khand/varna byte-vs-cell string pairs | search `khand_anwesh` :105 / `varna_anwesh` :155; replace `:142` / `:189`; split `:206` / `:251`; join `:289` / `:338`; trim spaces `:327` / `:373`; upper `:365` / `:409`; lower `:388` / `:431`; starts-with `:413` / `:455`; ends-with `:429` / `:471`; 3-way compare `:445` / `:487`; reverse `:473` / `:510`; count occurrences `:504` / `:541`; count vowels `:527` / `varna:gan_swar` :63; count one char `:546` / `varna:gan_akshar` :78; find one char `:561` / `varna:anwesh_akshar` :90; all-digits `:576` / `varna:asti_sarv_ank` :101 | 2 each | Element access only: `akshar` (byte) vs `h[i]` (qword cell). Same guards, same scan, same conventions. (G36 advances `pos` bytes vs `pos * 8`; G37–G40 differ in length explicit vs derived via `vartani_aayam`; G40 inlines the 48–57 test where varna delegates per character.) |

Tier A arithmetic: 86 functions in 40 groups → 40 functions, saving **46**.

### Tier B — wrappers and aliases (38 functions, saving 37)

Each body only delegates (fixing arguments and/or unpacking a descriptor);
the generic replacement absorbs the role, so each collapses to 0 — except
the `maap` pair, which collapses 2 → 1.

- **8 `suchi_` adapters over `shreni_` array functions** (`lib/suchi.smlib`):
  `suchi_laghu` :226, `suchi_adhik` :237, `suchi_yog` :249,
  `suchi_gan` :256, `suchi_anwesh` :263, `suchi_asti_kramabaddha` :270,
  `suchi_dwi_anwesh` :278, `suchi_shreni` :214 (converts the −1 refusal
  into a 0/1 return). The first two add an `ok` flag (empty → `ok` 0);
  a generic min over a list must keep that flag.
- **`chay_khip`** (`lib/suchi.smlib:328`): stack push is list push.
- **`khand_antah`** (`:131`) / **`varna_antah`** (`:178`): `>= 0` → 1.
  **`khand_sam`** (`:592`): `khand_tul == 0` → 1.
- **`fnv1a_varna`** (`lib/gudh.smlib:30`): length derived via
  `vartani_aayam`.
- **`nighantu_antah`** (`:169`): `< 0` → 0.
- **14 `roop_` conveniences**: `roop_ank_aadhar_saral` :150 (adds the
  sign), `roop_ank_dhvaj` :174 (sign + `0b`/`0o`/`0x` prefix),
  `roop_dash` :212 (base 10), `roop_shodash` :217 (base 16),
  `roop_shodash_unnat` :222 (base 16, flags 2), `roop_asht` :227 (base 8),
  `roop_dwi` :232 (base 2), `roop_ank_upasarga` :239 (flags from `upper`),
  `roop_sthir` :597 (`always_sign` 0), `roop_sthir_chinhit` :603
  (`always_sign` 1), `roop_varg_bharatiya` :438 (step 2),
  `roop_varg_vishwa` :443 (step 3), `roop_varg` :450 (default Indian
  grouping), `roop_varg_ank` :456 (composition: render, then group).
- **7 `rakh_` set names over the `nighantu_` map**
  (`lib/sangrah.smlib`): `rakh_srij` :33, `rakh_yuj` :40,
  `rakh_antah` :45, `rakh_apanay` :50, `rakh_vardh` :171,
  `rakh_rikta` :179, `rakh_sam` :186 (two-way subset test).
- **`brihat_shesh`** (`lib/brihat.smlib:263`): allocates the scratch the
  helper takes as a parameter.
- **`khand_maap`** (`lib/khand.smlib:99`) + **`varna_maap`**
  (`lib/varna.smlib:19`): both the same one-line alias of builtin
  `vartani_aayam`; 2 → 1 (both could go, since the builtin exists — that
  would make the total 226, not 227).

Tier B arithmetic: 36 wrappers → 0 (saving 36) + the `maap` pair 2 → 1
(saving 1) = **37 saved**.

### Collapsed total

| bucket | functions | after collapse |
|---|---|---|
| Tier A duplicate implementations | 86 in 40 groups | 40 |
| Tier B wrappers / aliases | 38 | 1 (the surviving `maap` alias) |
| Everything else (singletons, incl. the 10 trivial accessors) | 186 | 186 |
| **Total** | **310** | **227** |

**310 − 46 (Tier A) − 37 (Tier B) = 227.** If the two `maap` aliases are
both deleted (the builtin `vartani_aayam` already exists), 226. Collapsing
only the separate implementations and keeping every wrapper as a named
convenience gives 310 − 46 = **264**. The "150" in the brief's "310 and not
150" would need 160 removals; the counted per-type duplication is 83 —
roughly half that. What the collapse does **not** do: it does not pick one
sort algorithm, one overflow convention, or one failure convention. Those
are further design decisions, not like-for-like collapses.

### NOT duplicates — functions that look duplicated but are not

- **Same operation, different overflow / failure convention (16 + others).**
  Checked vs saturating arithmetic, same op, same overflow detection,
  different outcome on overflow (`ok` = 0 + return 0 vs clamp to MAX/MIN)
  — 8 pairs in `lib/ganita.smlib`: `ganita_janchit_yuj` :363 /
  `ganita_paripurna_yuj` :495; `nyun` :389 / :514; `gun` :416 / :534;
  `bhaj` :453 / :647; `shesh` :474 / :665; `ghat` :565 / :615;
  `kramgun` :588 / :710; `nirapeksh` :680 / :695. (The `ghat`/`kramgun`
  pairs also differ in structure, but the deciding difference is the
  overflow outcome.) Plain/wrapping/saturating counterparts elsewhere:
  `ganit:ghat` :108 (saturating, `e <= 0` → 1) vs
  `ganita:ganita_paripurna_ghat` :615 (`e < 0` → 0) — the negative-exponent
  convention differs; `ganit:kramgun` :139 (−1 on overflow) vs the
  checked/saturating factorials; `sadhan:shesh` :93 (plain `a − (a/b)*b`,
  `b == 0` → 0) vs the checked/saturating remainders. Checked vs unchecked
  access: `mala:mala_sangrah` :20 / `mala_grah` :29 (no bounds check) vs
  `mala_sangrah_surakshit` :75 / `mala_grah_surakshit` :87 (return 0 out of
  range); `shreni:vinimay` :6 (unchecked, no return) vs
  `suchi:suchi_vinimay` :173 (bounds-checked, returns 1/0).
- **Differ ONLY in the comparison operator / constant — the most collapsible
  shape, but different functions.** Not counted (each computes a different
  predicate/value), but these are the cases where one parameterised function
  would most directly replace several: min vs max (`shreni:laghu` :39 /
  `adhik` :53; `sankhyiki:laghutama` :34 / `adhikatama` :47;
  `purna_laghutama` :148 / `purna_adhikatama` :161; `ganit:laghu2` :45 /
  `adhik2` :53); case direction (`khand_unnat` :365 / `avanat` :388, and
  the varna pair; `varna:unnat_sanket` :113 / `avanat_sanket` :120);
  one-character range predicates (`varna:asti_ank_akshar` :27,
  `asti_unnat_akshar` :34, `asti_avanat_akshar` :41,
  `asti_akshar_akshar` :48, `asti_avakash_akshar` :56);
  `ank:asti_yugm` :4 (`% 2 == 0`) vs `asti_visham` :8 (`% 2 != 0`); series
  terms (`madhava:madhava_sin` :50 vs `madhava_cos` :80 — the 15-line
  range-reduction preamble is verbatim identical, but the Taylor terms
  differ); set operations (`sangrah:rakh_ubhaya_bhed` :63,
  `rakh_sangam` :96, `rakh_sampat` :126, `rakh_bhed` :148 — same
  enumerate-and-test skeleton, different membership predicate);
  elementwise add vs scalar multiply (`samanvaya:matrika_yoga` :66 vs
  `skalar` :79); read-loop vs write-loop (`patra:patra_path_sarv` :29 vs
  `patra_likh_sarv` :57 — opposite syscalls).
- **Differ in element size / stride.** `khand:khand_pratilip` :81 (copies
  bytes) vs `khand_bandh` :39 (packs qword cells to bytes) — the stride is
  the semantic difference; its inverse `khand_mukt` :61 (bytes → cells)
  likewise distinct. `ganita:bk_na_adhik` :317 (30-bit-limb compare) vs
  `brihat:brihat_tul` :101 (decimal-digit compare).
- **Different algorithms that share a word.** The four sorts are four
  algorithms, not four copies (`shreni:budbud_shreni` :13 bubble,
  `shankh_shreni` :120 shell, `nivesh_shreni` :148 insertion,
  `mil_shreni` :223 + `mil_shreni_punar` :174 merge). There is no float or
  text sort anywhere. (`sangrah:rakh_tak_mala` :217 re-implements a bubble
  sort inline over `(pointer, length)` pairs compared with `khand_tul` —
  a different sort key/comparison, so it is not a duplicate of
  `budbud_shreni` either.) Linear vs binary search (`anwesh_sarak` :77 vs
  `dwi_anwesh` :108); count vs find (`gan` :87 vs `anwesh_sarak` :77;
  `suchi_antah` :300 boolean vs `suchi_kramank` :313 index;
  `khand_anwesh` :105 vs `khand_gan` :504); stack pop vs queue dequeue
  (`chay_apanay` :334 vs `avali_nishkas` :441); peek-last vs peek-first
  (`chay_avalok` :351 vs `avali_avalok` :459); encode vs decode (inverses:
  `anukram_khip_i64` :36 vs `anukram_grah_i64` :61, `:88` vs `:110`;
  `brihat_ank_se_laghu` :29 vs `brihat_ank_tak_laghu` :71;
  `aadhar:brihat_ank_tak` :20 vs `brihat_ank_se` :80); different operations
  sharing a name stem (`brihat_yuj` :117 add / `brihat_nyun` :134 subtract
  / `brihat_gun` :157 multiply / `brihat_bhajshesh` :200 divide /
  `brihat_shesh` :263 remainder; `ganit:dvigun` :186 ×2 / `trigun` :194 ×3
  / `vardh` :202 +1); different sqrt algorithms (`ganita:ganita_vargmool`
  :66 integer binary search vs the Newton float pair in G7); text → number
  with different accepted language (`vakyank:varna_tak_ank` :84 base 10
  with sign vs `varna_tak_ank_aadhar` :186 bases 2–36, no sign); integer →
  text, negative input (`vakyank:ank_tak_aadhar_varna` :142 returns 0 with
  empty output for negatives, lowercase-only, vs `roop:roop_ank_aadhar`
  :73); in-place shift vs out-copy (`vakyank:purti_vam` :241 vs
  `roop:roop_purti_vam` :252 — different aliasing); `khand_sam` :592
  (4-line wrapper over `khand_tul`) vs `varna:varna_sam` :127 (28-line
  standalone loop) — `khand_sam` is counted as a wrapper; `varna_sam` is
  not its duplicate; closest near-miss `ank:fib` :89 (returns `n` for
  `n < 2`, so `fib(-5)` is −5) vs `chandas:matra_meru` :63 (returns 0 for
  `n <= 0`) — identical for `n >= 2`, guard differs, not counted;
  unifying the negative convention would save 1 more (total 226);
  `nighantu:nighantu_srij` :107 (hash table) vs the G19 pair — not
  counted; rehash vs realloc copy (`nighantu_vardh` :279 vs
  `suchi_vardh` :67); values vs keys enumeration (`nighantu_mulya` :360
  vs `nighantu_kunjika` :383); trace vs plain sum (`samanvaya:karna_yog`
  :111 sums the diagonal vs G1's linear sums); the 8 `phal_janchit_*`
  (`:85, :100, :115, :130, :145, :161, :174, :187`) are all the same
  13–15-line wrapper pattern, but each wraps a *different* operation, so
  they do not collapse to one under type-generics — that would need
  parameterisation over the operation, which is not what this round's
  generics are. Intra-function repetition (not a function duplicate):
  the borrow-subtraction loop is written inline in both
  `brihat_shesh_sahaya` :276 and `brihat_bhajshesh` :200 instead of
  calling `brihat_nyun` :134.

**Task 2 verdict.** The brief's 310 is confirmed — 24 modules, 310
`prakriya` definitions, no duplicate names — but the duplication inside it
is 83 functions, not ~160: 46 separate implementations of the same
algorithm in 40 groups (headlined by the 16 khand/varna byte-vs-cell
string pairs, the sum/min/max/mean/range families across `vitti` raw
arrays, `dasham` koshes and raw pointers, and exact two-name copies such
as `varg`/`vargit` and `seemit`/`ganit_seemit`), plus 37 thin wrappers and
aliases that already delegate. Collapsing every group to one leaves 227
functions (226 if both `maap` aliases of the same builtin go); keeping the
wrappers as named conveniences leaves 264. The rest is not duplication a
type-generic can remove: four genuinely different sorts, eight
checked-vs-saturating arithmetic pairs that differ in overflow outcome,
eight `phal` wrappers over eight different operations, and a long tail of
same-shaped loops — min vs max, sin vs cos, union vs intersection, encode
vs decode — that compute different things and share only a skeleton.

---

## Task 3 — what would break

### (a) The guard — how it works, and the byte-change analysis

`tools/guard_pair.py` (78 lines) is the guard. Usage:
`python3 tools/guard_pair.py OLD_TREE OLD_COMPILER NEW_TREE NEW_COMPILER
OUT_DIR [--pe]`. It compiles every program in the corpus twice — once with
the old (tree, compiler) pair, once with the new pair — each time with the
tree as the working directory, so `yoj` resolves against that tree's `lib/`.
It compares the two outputs byte for byte plus the compiler exit code, and
prints one line per program: `IDENTICAL` (both compiled, same exit code,
same bytes); `REFUSED-SAME` (neither wrote an output, same exit code);
`DIFFER` (anything else — the line that matters); `NEW` (the program does
not exist in the old tree). The last line is the count, e.g. `783 programs:
587 byte-identical, 196 refused identically, 0 DIFFER, 0 new`. Exit code is
1 if any DIFFER. It writes only to `OUT_DIR`. It never runs the compiled
programs, never compares program output, and never compares compiler
stdout/stderr text — only output bytes and the compiler exit code.

There is **no caller in the tree**. `guard_pair.py` is not invoked by
`tools/gates.sh` (zero occurrences) and not by any workflow under
`.github/workflows/` (zero occurrences; one workflow mentions a `guard.txt`
log file, not the script). It is run manually, per change, by contributors,
in both formats (ELF, and PE via `--pe` / the Windows compiler under Wine).
The record of each run is the printed log line quoted in the contributor's
handback report. There is also **no stored baseline file** — no frozen hash
list, no golden byte file. The "baseline" is the previous tree plus its
compiler, checked out in a worktree and built or copied. The guard is a
pairwise comparison of two live trees, not a comparison against a recorded
hash.

Latest run on this line (v315 → v316, quoted in
`Claude-to-Sarvam/R163-00-...md` and repeated in R167 and in
`ChatGPT-to-Sarvam/ROUND-220-...md`): **ELF and PE, 783 programs:
587 byte-identical, 196 refused identically, 0 DIFFER**. The R163 report
adds that the 196 refusals were checked to carry the same message, 196 of
196 — that message check is manual; the script itself does not compare
refusal text (same exit code is enough for `REFUSED-SAME`).

Corpus recount on this tip — the five globs over the new tree:

| pattern | count |
|---|---|
| `examples/*.sm` | 331 |
| `examples/*/*.sm` | 13 |
| `tests/stdlib/*.sm` | 229 |
| `tests/r*/*.sm` | 148 |
| `tests/r*/*/*.sm` | 62 |
| **total** | **783** |

Recounted by running the same globs on this tip: **783, exact**. The
brief's "783 programs" reproduces. Two corrections to the usual phrasing:
the guard covers **344** examples, not 347 — the recursive example total
is 347, but the three files under `examples/r68/pairs/` sit one level
deeper than any guard pattern, so they are outside the guard (and outside
the suite too). And the guard is not "every program in the tree": a `find`
over `examples/` + `tests/` returns 1,018 `.sm` files; **235 are outside
the guard**, mostly the negative-mutant corpus under `tests/negative/`
and the `tests/guard_page/` controls. The brief's sentence "783 programs
compile to identical bytes" is wrong as written: **587 compile; 196 refuse
identically**. The guarantee is 587 byte-identical outputs plus 196
identical refusals.

Why a library change moves bytes — the mechanism, read from the source.
Four facts decide everything below:

1. **A `yoj` inlines the whole module file.** `expand_imports`
   (`src/sutram_compiler.asm`, around line 3599) reads the entire `.smlib`
   file verbatim into the expanded source buffer (`IMPORT_BUF_CAP` 131072),
   with de-duplication by module name only. There is no per-function
   selection: importing a module brings in every definition in it, called
   or not.
2. **Every collected function is emitted.** `gen_all_functions` (around line
   18429) loops over all collected `FUNCDEF` nodes and emits code for each.
   No "used"/reachable/dead-code check anywhere in that loop (the only
   `used` flags in the file are unrelated). Unused library functions are
   emitted into every importer's binary.
3. **Order: `mukhya` first, then all functions.** `gen_code` (around line
   18036) emits `mukhya`'s body, then calls `gen_all_functions` (line
   18210). Call sites are relative displacements resolved at compile time
   from `func_table`, which lives only in the compiler's memory.
4. **The output carries no symbol table.** `write_elf` (around line 32660)
   writes a 120-byte header pair (`e_shoff` 0, zero section headers) and
   then `code_buf` verbatim, with `p_filesz = code_sz`. There is no name
   table. **Function names are not in the output bytes at all** — except
   where a name occurs inside a string literal that the code emits. The
   library does contain such literals: the `abhava(...)` diagnostic strings
   name their function, e.g. in `lib/ganit.smlib`, `lib/brihat.smlib`,
   `lib/ganita.smlib`, `lib/samanvaya.smlib`, `lib/sankhyiki.smlib`
   (15 occurrences of the `Sutram truti ...: <name>:` form across those
   five files).

Consequences: renaming a function, by itself, changes **zero** output
bytes — unless the name appears in one of those diagnostic strings, or the
rename changes the order or the number of definitions in the file.
Deleting, adding, or reordering a definition in a module changes **every
importer's** output bytes: later functions move, so every later call
displacement changes (including calls from `mukhya`, which is emitted
first), and even a pure append at the end of the file changes `code_sz`
and therefore the header and the file length. There is no shape of
library-text change that leaves importers byte-identical. A compiler-only
change that leaves the emitted code for existing constructs untouched
changes zero programs. Precedent: R182 (unknown character now refused)
ran 0 of 783 DIFFER — a compiler change can be byte-free when no existing
program depends on the old behaviour. The R118 precedent shows how a
rename can be byte-free for *callers*: `r118_lib_alias` (around line
33307) textually rewrites a call to an old library name to the new name
at compile time, with only a warning. The warning goes to compiler
stderr, which neither the guard (bytes + exit code only) nor the suite
(compiler output discarded for programs that compile) compares. But the
rewrite only saves the call sites; if the old definition is also deleted
from the module, importers still change bytes for the reason above.
Guard blind spots that matter here: a change that only rewords a refusal
message is invisible (same exit code → `REFUSED-SAME`); a change that
turns a compiling program into a refusal is a DIFFER, and a change that
turns a refused program into a compiling one is also a DIFFER — any
program that newly uses generic syntax necessarily DIFFERs, by
construction.

Byte-change analysis per implementation shape. Importer counts below are
guard programs whose source has a `yoj <module>` line (recounted on this
tip; comment-only mentions excluded — one file, `examples/329_r113_sankhya_bindu.sm`,
mentions `yoj sankhyiki` only in a comment and is not an importer):

| module | guard importers | module | guard importers |
|---|---|---|---|
| ganit | 46 | sangrah | 13 |
| varna | 34 | samanvaya | 13 |
| ganita | 27 | chandas | 13 |
| shreni | 22 | roop | 12 |
| khand | 22 | madhava | 11 |
| ank | 22 | sadhan | 10 |
| sankhyiki | 21 | vakyank | 10 |
| suchi | 20 | kalana | 8 |
| nighantu | 16 | aadhar | 5 |
| brihat | 15 | anukram | 4 |
| mala | 15 | phal | 3 |
| | | patra | 2 |
| | | gudh | 1 |

Unions (distinct programs): shreni/suchi/sankhyiki = **62**;
shreni/suchi/sankhyiki/ganita/phal/khand/varna = **135**; all 24 lib
modules = **282**. Guard programs importing no lib module: **501**.

- **Shape A — compiler-only generics, library untouched.** New syntax, new
  symbol-table fields, new codegen that only runs for generic functions.
  Existing constructs emit identical code. **0 of 783 DIFFER.** This is the
  only shape that keeps the guard at 0 DIFFER, and it is achievable: the
  R182 precedent is exactly a compiler change with 0 DIFFER, and new
  symbol-table fields / name mangling have no output effect on their own,
  because names are not emitted and the function table is compile-time only.
- **Shape B — additive library: generic functions added, old ones kept
  byte-for-byte.** The old programs still compile, still print the same
  output — but every importer of a touched module **DIFFERs anyway**,
  because the whole module (now longer) is emitted into their binaries.
  Count = that module's importers (e.g. shreni 22, suchi 20, sankhyiki
  21). Appending at the end of the file avoids displacement changes in
  earlier code but not the length/header change, so the guard still
  reports DIFFER. The DIFFERs are byte-only; no output changes. Exception
  that avoids even this: put the new generic functions in a **new module**
  no existing program imports — then 0 existing programs change bytes,
  since no existing program's expanded source changes at all.
- **Shape C — collapse: duplicate definitions deleted, old names kept as
  compiler rewrites (R118-style).** Every importer of the touched module
  DIFFERs (deletion shifts all later functions; `mukhya`'s call
  displacements change too). For the seven most-duplicated modules
  (shreni/suchi/sankhyiki/ganita/phal/khand/varna) that is **135 guard
  programs**; for a whole-library collapse, **282**. Callers of the removed
  names keep compiling and keep their outputs (the rewrite), so the DIFFERs
  are byte-only — *provided* the generic body is semantically identical for
  each specialisation (checked vs exact vs result-wrapped are not
  identical, and kosh-dasham vs mala-vitti stats are not identical). If the
  collapse is careless about that, some of the 135 also change output.
- **Shape D — collapse without alias rewrites.** Same importer DIFFERs as
  Shape C, plus every program that *calls* a removed name moves from
  IDENTICAL to DIFFER because it stops compiling (compiled → refused).
  Across the guard corpus, 274 programs call at least one lib function and
  110 call at least one function from the duplicated families — those are
  the programs that would break outright rather than merely change bytes.
- **Shape E — monomorphisation (one copy per type, per call site).** Same
  importer DIFFERs as a collapse (old defs go), plus each program that
  instantiates a generic gains one emitted copy per type it uses — its bytes
  differ from any baseline by more than the importer's share. Programs that
  newly use generic syntax go from refused to compiling, which the guard
  reports as DIFFER by construction. There is no reading of the guard under
  which a new feature's first users are 0 DIFFER.
- **Shape F — erasure to 64-bit values.** This is the shape the brief
  implies, but the premise is partly already true: the library is already
  erased at the *element* level. `lib/shreni.smlib` operates on `mala`
  (64-bit cells) with no type knowledge — `budbud_shreni`, `laghu`,
  `adhik`, `yog`, `dwi_anwesh` compare and move 64-bit values and nothing
  else. There is no `sort_int` / `sort_text` anywhere in the tree. What
  erasure would actually change is the *container* level: a list's elements
  are already 64-bit cells, so a generic sort over a `suchi` list is a
  call-site change (unwrap the list to its cells) plus a compiler change,
  and needs no change to `shreni.smlib` at all. Under that reading:
  programs that switch to the generic change bytes (different call-site
  code); programs that do not switch change nothing; `suchi_shreni` itself
  is untouched unless the library is also rewritten, in which case Shape
  C's importer count (suchi: 20) applies.

**Bottom line for (a):** yes — under every shape except a pure
compiler-only change (A) and a new-module additive change (B's exception),
existing programs change bytes. The count is not "the programs that call
the duplicated functions" (110 in the guard corpus) but "the programs
that *import* a touched module" (135 for the seven duplicated modules,
282 for the whole library), because the whole module is emitted into
every importer. The guard would report those as DIFFER, all byte-only if
the collapse is faithful, plus outright breakage for callers if old
names are removed without rewrites.

### (b) The library's 229 proofs — what they are, and whether they assume a specific specialisation

The number **229 reproduces exactly**: `tests/stdlib/*.sm` contains 229
files, each with a `.out` and a `.exit` golden (229/229/229 recounted).
`tools/proof_lib.py` (160 lines) is the harness: for each file it
compiles and runs the program (working directory = repo root, so `yoj`
finds `lib/`) and compares stdout and exit code against the goldens.
Goldens are recorded from actual runs, never hand-written; `--record`
regenerates them. `tools/gates.sh` accepts the gate when the last line
contains "0 failed".

But 229 is only one of two proof sets. The second set is
`tools/proof_props.py` (86 `def prop_*` functions, recounted): property
proofs over deterministic inputs — fixed seed 20261009, 15 cases each.
Each property generates a `.sm` program in a temp file, compiles and
runs it, and checks an invariant (sortedness, round-trip, LIFO/FIFO,
checked-arithmetic refusal, …), printing PASS/FAIL with the
counterexample. There are no golden files for these; the property code
*is* the expectation. `tools/gates.sh` accepts them only on "86/86".
**Total proof corpus on this tip: 229 + 86 = 315.** The brief counts
only the first set. Stale line to note: `tools/guard_page.py`'s docstring
still says "library proofs 226/226" — the count moved to 229 since that
line was written.

They prove *values*, not bytes: a named library function on fixed
inputs prints the expected numbers and exits 0 (or refuses with the
expected diagnostic, for the contract cases). The proof files are
organised per specialisation, and the split is the point:

- `tests/stdlib/sort_*.sm` — **13 files, one per `shreni` function**:
  `sort_bubble_sort` calls `budbud_shreni`, `sort_shell_sort` calls
  `shankh_shreni`, `sort_insertion` calls `nivesh_shreni`, `sort_merge`
  calls `mil_shreni`, `sort_min_of` calls `laghu`, `sort_max_of` calls
  `adhik`, `sort_sum_of` calls `yog`, `sort_count_of` calls `gan`,
  `sort_find_linear` calls `anwesh_sarak`, `sort_binary_search` calls
  `dwi_anwesh`, `sort_is_sorted` calls `asti_kramabaddha`,
  `sort_reverse_arr` calls `viparyay_mala`, `sort_swap` calls `vinimay`.
  All operate on `mala`.
- `tests/stdlib/sankhyiki_*.sm` — **16 files**. The float and int
  versions are separate proofs with separate goldens:
  `sankhyiki_yoga` calls `yoga` on a `kosh dasham`; `sankhyiki_purna_yoga`
  calls `purna_yoga` on a `mala` and also covers the empty-input case
  (`purna_yoga(a, 0)`). Same split for madhya/prasaran/vyapti/laghutama/
  adhikatama vs their `purna_` twins.
- `ganita_checked.sm`, `ganita_sat.sm`, `result29.sm`,
  `result_chain.sm`, `safety24.sm`, `safety25.sm` and others test the
  checked (`ganita_janchit_*`), exact (`ganita_paripurna_*`) and
  result-wrapped (`phal_janchit_*`) arithmetic separately — three
  different refusal behaviours for the "same" operation.
- Property proofs: 5 properties `yoj shreni` (the four sort properties
  `prop_sort_ordered`, `prop_sort_permutation`, `prop_sort_idempotent`,
  `prop_sort_edges`, plus `prop_edge30_cont`); 12 `yoj suchi`;
  2 `yoj sankhyiki`; 14 `yoj ganita`; 2 `yoj phal`; 11 `yoj khand`;
  7 `yoj varna`.

**Yes, they assume a specific specialisation — per file, by name.** A
collapsed generic `sort` would satisfy the *value* assertions only if it
preserved each specialisation's semantics exactly, and the checked/exact/
result-wrapped triple cannot be one function without changing what
happens at the boundary (refuse vs wrap vs return-a-result). More
concretely: the proof *files themselves* would need rewriting wherever
they name a removed function, because a proof file is a program that
calls the function by name. Counts of stdlib proof files calling each
duplicated family:

| family | stdlib proof files calling it |
|---|---|
| shreni mala (sort/search/min/max/sum) | 14 |
| suchi list | 7 |
| sankhyiki (plain + purna) | 14 |
| ganita checked/exact + phal wrapped | 12 |
| khand/varna string ops | 16 |
| R116 scalar/contract fns (heterogeneous group) | 25 |

(The families overlap — `gaps19.sm` calls several — so the rows do not
add up. 227 of the 229 proof files call at least one lib function. The
two that do not are `tests/stdlib/kosh_reuse.sm` and
`tests/stdlib/width_repro.sm`.)

What "need rewriting" means here is precise and limited: the proof
files need their *call sites* edited to the new name; their goldens do
**not** need re-recording if the output is unchanged, because
`proof_lib.py` compares stdout and exit code only, not bytes. A
byte-only change to the library is invisible to the proofs. A faithful
collapse therefore costs proof-file edits (one line per call site, in
the files above) and zero golden changes. An unfaithful collapse — one
that changes a value, an exit code, or a diagnostic string — fails the
proofs until the goldens are re-recorded, and re-recording then destroys
exactly the evidence the proofs exist to provide.

The separate R116 contracts gate (`tests/r116/test_contracts.py`)
pins 11 function names and their exact diagnostic strings in its `MSG`
dict (`dvigun`, `trigun`, `vardh`, `nirapeksh_mulya`,
`mahattam_samapavartak`, `viparyay_ank`, `ganita_nirapeksh`,
`brahmagupta_kshetr`, `brihat_ank_tak_laghu`, `adish_gunan`,
`bindu_gunan`). Any rename of those eleven that reaches the diagnostic
string breaks this gate until its `MSG` dict is edited — which is a
re-baseline of a contract, not a test fix.

### (c) The goldens — how the suite works, what would need re-baselining

`tests/run_tests.py` (192 lines). `tests()` is exactly
`examples/*.sm` — top level only, **331 tests**. For each it compiles
the program (working directory = repo root, except `79_ayojan_cwd`
which compiles from elsewhere), runs it with fixed stdin where declared
(6 programs) and a language pack where declared (6 programs), and
compares stdout + exit code against `tests/expect/<name>.out` and
`.exit`. Two extensions: a `.err` file, when present, must match stderr
too (12 programs); a `.compile_fail` marker file means the expected
outcome is compilation failure, and then the golden `.out`/`.exit` hold
the compiler's stdout+stderr and exit code instead. No golden at all
means `NO-EXPECTATION`: the program runs, its output is printed but not
checked, and it is not counted as passing. `--record` regenerates all
goldens from actual runs. `tools/gates.sh` parses the last summary line
and fails the gate only on `FAIL=[1-9]` — `NO-EXPECTATION` is tolerated
there, though `run_tests.py` itself exits non-zero while any remain.

Recount on this tip: tests run **331**; goldens present (`.out` + `.exit`):
**327**; no golden: **4** — `215_r12_wordfreq`, `216_r12_expr`,
`217_r12_report`, `219_sanskrit_kosh_aliases`. (The brief's "327 tests
with expected outputs" is right as a count of goldens; the suite runs
331.) `.compile_fail` markers: **75**. `.err` files: **12**. Language
packs: 6 programs; fixed stdin: 6 programs; exit override: 1
(`29_nishkriya`, exit 42).

The suite compares output, not bytes — so a byte-only library change
fails **zero** goldens. What fails a golden is an output, exit-code, or
recorded-text change. Per category:

- **Plain run goldens (252 = 327 − 75).** Need re-baselining only if the
  program's stdout or exit code changes. Under a faithful collapse
  (Shape C) with old names aliased: **0**. Under a rename without aliases,
  every example that calls a removed name stops compiling, so its golden
  changes kind (stdout golden → compile-fail golden): at most the **23**
  examples that call a duplicated-family function (§3.4 below), and at most
  **44** that call any lib function. Under an unfaithful collapse
  (different comparison, overflow, or float-vs-int behaviour), the count is
  whichever of those programs' outputs move — not determinable from
  reading alone, but bounded by the same 23/44.
- **`.err` goldens (12).** All twelve name a lib function in the recorded
  stderr string: the eleven R116 examples (`330`–`337`, `339`, `341`,
  `342`) plus `207_sankhyiki_vector` (names `bindu_gunan`). If the
  generic keeps the same `abhava` string — same function name in the
  text — **0 change**. If the diagnostic is rewritten with the generic
  name, **all 12** need re-recording (mechanical, one `--record` run),
  and the R116 `MSG` dict needs the same edit. Note the asymmetry: the
  `.err` golden is the only place in the suite where a *name* is pinned
  to output text.
- **Compile-fail goldens (75).** Only **3** name a lib function as a
  whole word in the recorded compiler output: `283_r81_parikshita_refuses_library`
  (names `mala_yog`, in the refusal and the echoed source line),
  `329_r113_sankhya_bindu` (names `bindu_gunan`, in the hint),
  `70_module_collision` (names `varg`). Only **3** of the 75 programs call
  a lib function at all (`283`, plus `352_r127_muse_assign_kosh_mala` and
  `355_r127_muse_malacell`, both calling `mala_nava`). The other 72 are
  language errors — capacity, scope, arity, kind, indentation — that no
  library change touches. (An earlier substring search returned 29 hits;
  28 of those were substrings such as `gan` inside `ganita` or `yog`
  inside `prayogat` — the word-boundary count is 3.)
- **The 4 NO-EXPECTATION programs.** These are not re-baselining at all:
  they have no golden to re-baseline. Recording goldens for them would
  *add* coverage. Note `215_r12_wordfreq` calls `khand_bhed` (and imports
  `khand` + `nighantu`), so whatever golden it eventually gets depends on
  the `khand` collapse.

Re-baselining the suite is mechanically one command
(`tests/run_tests.py --record`); the cost is not the command but that
`--record` trusts the new run — a re-recorded golden stops being an
independent check of the change it records.

### (d) The 331 examples — which would change, and why

Usage counts on this tip (method: strip string literals and `#`
comments, match lib function names as whole words followed by `(`, and
exclude names the example itself defines; this misses Devanagari-named
calls and namespaced-alias calls, so call counts are lower bounds):

- **78** of 331 `yoj` some module; **53** import a lib module;
  **44** call at least one lib function.
- **23** call at least one function from the duplicated families in
  the per-family table below (shreni/suchi/sankhyiki/ganita-phal/
  khand-varna/R116-scalar): `10_mathlib`, `61_stdlib_math`,
  `62_stdlib_num`, `83_stdlib_sort`, `85_stdlib_shellsort`,
  `126_numeric_pipeline`, `202_brahmagupta_area`, `206_sankhyiki`,
  `207_sankhyiki_vector`, `215_r12_wordfreq`, `280_r80_runtime_wraps`,
  `330_r116_dvigun`, `331_r116_trigun`, `332_r116_vardh`,
  `333_r116_nirapeksh_mulya`, `334_r116_mahattam_samapavartak`,
  `335_r116_viparyay_ank`, `336_r116_ganita_nirapeksh`,
  `337_r116_brahmagupta_kshetr`, `339_r116_brihat_ank_tak_laghu`,
  `341_r116_adish_gunan`, `342_r116_bindu_gunan`,
  `343_r116_suchi_shreni`. (The five narrow families alone account for
  7 of the 23; the other 16 come from the heterogeneous R116-scalar
  group. `338_r116_brihat_ank_se` calls `brihat_ank_se`, which is in
  none of the table's families, so it is not in this count.)

Per-family example counts:

| family | examples calling it | which |
|---|---|---|
| shreni mala | 2 | `83_stdlib_sort` (`budbud_shreni`, `laghu`, `adhik`, `yog`), `85_stdlib_shellsort` (`shankh_shreni`) |
| suchi list | 1 | `343_r116_suchi_shreni` (`suchi_shreni`, plus `suchi_srij`/`suchi_khip`/`suchi_grah`) |
| sankhyiki plain + purna | 2 | `126_numeric_pipeline` (`madhya`, `prasaran`, `vichalan`), `206_sankhyiki` (`yoga`, `madhya`, `prasaran`, `vichalan`, `laghutama`, `adhikatama`, `vyapti`) |
| ganita checked/exact + phal | 1 | `280_r80_runtime_wraps` |
| khand/varna | 1 | `215_r12_wordfreq` (`khand_bhed`; also no golden — §3.3) |
| R116 scalar/contract (heterogeneous, not one collapse) | 17 | `10_mathlib`, `61_stdlib_math`, `62_stdlib_num`, `126_numeric_pipeline`, `202_brahmagupta_area`, `207_sankhyiki_vector`, `330`–`337`, `339`, `341`, `342` |

Change categories for the 331, under a collapse-with-rename and no
aliases (the worst honest shape):

- **Change bytes: 25** import one of shreni/suchi/sankhyiki/ganita/phal/
  khand/varna; **53** import any lib module. These change bytes even
  when they never call the collapsed function, because the whole module
  is emitted into their binary (§1.4). Under a whole-library collapse
  the byte-change set is the 53.
- **Change output: 0 expected** under a faithful collapse — the 23
  family-calling examples print the same numbers, because the generic
  computes the same values. Output changes only if the collapse is
  unfaithful (different comparison, overflow/refusal, or float-vs-int
  behaviour). The one output that is *known* to be load-bearing is
  `343_r116_suchi_shreni`: its second `suchi_shreni` call must return
  status 0 and print nothing (the R116 scratch-refusal case) — a
  generic sort that allocated differently would change that program's
  output, not just its bytes.
- **Stop compiling: up to 23** (the family callers) if their called name
  is removed without a compiler rewrite; **0** if old names are kept as
  R118-style rewrites.
- **Change stderr: up to 12** (the `.err` examples, §3.3), only if
  diagnostic strings are renamed.
- **No change at all: 278** import no lib module (under a library-only
  collapse); **331** under a compiler-only change (Shape A).

Under the additive shape (generics added, old kept): byte change = the
same 25/53 importers (binaries get longer), output change = 0, compile
failures = 0. Under the new-module variant of the additive shape: 0
examples change anything.

### Re-baseline list

What would have to be re-baselined, in the order the tree would feel it:

1. **The guard itself.** No file to edit — re-baselining means accepting
   a new DIFFER list as the expected result of the next comparison, and
   recording it the way R175/R176 did (differ-list + per-program output
   comparison on both sides). Expected size: **~135 DIFFER** for a
   collapse of the seven duplicated modules, **~282** for a
   whole-library collapse, **0** for a compiler-only change or a
   new-module additive change. Every DIFFER must be shown byte-only
   (same stdout, same exit code, run on both sides) or it is a
   regression, not a re-baseline.
2. **Suite goldens.** Re-record only what actually changes: 0 plain
   goldens under a faithful collapse; **0–12 `.err` goldens** depending
   on whether diagnostic strings are renamed; up to 23 goldens change
   kind (run → compile-fail) if old names are removed without rewrites.
   The 4 NO-EXPECTATION programs are a separate decision (add goldens,
   don't re-baseline).
3. **Proof files.** Rewrite call sites in the proof files that name a
   removed function (§3.2 table: 14 + 7 + 14 + 12 + 16 files, with
   overlap; 227 of 229 call some lib function). Re-record goldens only
   where output changes (0 expected under a faithful collapse). The 86
   property proofs need the same call-site edits where they name a
   removed function (5 `yoj shreni`, 12 `yoj suchi`, 2 `yoj sankhyiki`,
   14 `yoj ganita`, 2 `yoj phal`, 11 `yoj khand`, 7 `yoj varna`).
4. **Docs and indexes.** `docs/sutram-stdlib.html` (regenerate with
   `tools/gen_stdlib_ref.py`; 310 signatures on this tip),
   `src/r52_lib_index.inc` (regenerate with `tools/lib_index.py --write`;
   310 rows — the `yoj` hint reads this), the doc-signatures gate
   (whose `tools/gates.sh` comment still says 305/305), the R116 `MSG`
   dict (11 names), the R118 alias table if new rewrites are added
   (`src/sutram_compiler.asm` around line 33307), and the counts in
   `PROJECT-MASTER.md`.
5. **Other gates that compare bytes or exact text.** R28 linker
   (`--object` + link must equal the direct compile, byte for byte) and
   R31 incremental (rebuild must equal a clean build) — both should still
   hold if the same new compiler is used on both sides, but that is a
   property of the design, not something readable from the tree (see
   Could-not-determine). R111/R118 alias gates require old name = new
   name byte for byte; a generic alias must satisfy them or the gate
   fails. The codegen gate (12 tiny programs, no lib calls) is
   unaffected unless generic machinery changes codegen for ordinary
   `prakriya` — its ceilings are exact instruction counts.

### Acceptability judgement

**Not acceptable as a silent re-baseline; acceptable only as a bounded,
deliberate change done in the order below.**

Weigh it plainly. The guard is the project's strongest guarantee
precisely because it is byte-exact over 783 programs and has caught
real regressions; its standing rule, written in R175, is that a DIFFER
means the change is wrong. Re-baselining 135 programs (or 282 for the
whole library) converts the guard from a proof into a checklist for
those programs: their bytes are no longer independently verified, only
their outputs, and the next accidental codegen change inside any of
them will not be caught by byte comparison. What would have to be
re-established is the per-program output comparison on both sides for
every DIFFER (as R175 did for 38), a recorded differ-list, and a new
guard line that the next round treats as the baseline — and the R100
FIXALL precedent (549 DIFFER, accepted with a note that future runs
must expect them) shows how that debt then sits in the tree until
someone pays it down.

Against that, the benefit — by the Task 2 count, 83 definitions removed
(46 separate implementations + 37 wrappers), i.e. roughly a quarter of
the library, of which only a subset can honestly collapse, because
checked vs exact vs result-wrapped differ in refusal behaviour and
kosh-dasham vs mala-vitti stats differ in type — is a real tidying, not
a transformation: the library is already type-erased at the element
level, so generics remove duplication of *wrappers and containers*, not
of a type system.

The judgement follows from the mechanism, not from the size: the
cheapest generics that helps a beginner — one `sort` name that works on
a `mala` and on a list — can be delivered with **0 DIFFER** by doing it
compiler-side (Shape A) or in a new module no existing program imports
(Shape B's exception), keeping every old name as a rewrite. There is
therefore no need to spend the guard to get the feature. Spend the
guard only if the collapse itself is the goal, and then only one module
at a time, with old names kept as R118-style rewrites, each step's
DIFFER set proved equal to exactly that module's importers, each
program's output compared on both sides, and the checked/exact/wrapped
triples and the float/int stat pairs explicitly excluded from collapsing.
If the collapse cannot meet those conditions — in particular if it
renames diagnostic strings or merges behaviours that differ at the
boundary — the saving of 83 functions does not justify voiding the byte
guarantee over 135–282 programs. The guard's value exceeds the library's
tidiness.

---

## Task 4 — the beginner question

### The book's teaching order

Both books run the same chapter order (1–19): a beginner prints and uses
variables and arithmetic (ch. 2–4), then decisions and loops (ch. 5–6),
then `prakriya` (ch. 7), then `mala` (ch. 8), then — eleven chapters later
— the library (ch. 14). The concrete case is **sorting**.

| what a student meets | chapter | where |
|---|---|---|
| hello, numbers, strings | 1–3 | — |
| arithmetic, variables | 4 | — |
| decisions, loops | 5–6 | — |
| a function: `prakriya katha(nam) ...` | 7 | EN:187–199; SA:173–184 |
| a fixed-size array: `mala` | 8 | — |
| *first written type* `kosh dasham` | 18 | EN:691 |
| a typed parameter `prakriya mean(kosh dasham xs)` | 18 | EN:699–716 |
| the library as a bare name list | 14 | EN:437–446; SA:410–419 |

Functions are introduced **untyped**. Chapter 7 defines a function as
`prakriya` + a bare name + bare-name parameters (EN:187–199) — the same
order as a `yoj` call, with no parameter type ever shown. A beginner can
write a function before knowing any type: `prakriya mean(kosh dasham xs)`
is the *first* typed declaration in either book, eleven chapters later.

### What the library actually teaches

Chapter 14 presents the library as a bare name list — 24 modules, 310
functions — with no choosing rule, no summary, and no worked call. The
whole of the book's teaching of sorting is one row of the table
("`shreni` — 11 functions. Sort and search a list"), at EN:442. And that
row is **wrong**: `lib/shreni.smlib` defines 14 `prakriya`, not 11.

The sort family is the opposite of the brief's "one sort instead of
three": `lib/shreni.smlib` has **14 `prakriya`, all integer-only `(a, n)`**
— four sorts for one type (bubble `budbud_shreni`, shell `shankh_shreni`,
insertion `nivesh_shreni`, merge `mil_shreni`), zero sorts for `dasham`,
zero sorts for words, zero sorts that take a `kosh`. Numbers sort with one
call — `examples/83_stdlib_sort.sm` (`budbud_shreni(a, n)`) — but that
example is never mentioned in the book; words need a hand-written ~25-line
bubble sort over parallel (ptr, len) arrays
(`examples/215_r12_wordfreq.sm:9-35`, which sorts words by length, the
only way the book's word example can be done); `lib/suchi.smlib:7-8`
warns that dasham arguments are silently truncated to integers.

So a beginner who wants to sort words hits exactly the wall generics
would remove — not a "one sort instead of three" choice (they never meet
three sorts; they meet four, for one type), but "no sort for my data at
all". The concrete case is sorting words (or a `dasham` list, or a `kosh`)
with the same one call a number list gets.

### Does the book lead the student to generics?

**No.** "Generic" occurs **0 times** in either book. "Function is a value"
occurs 0 times; "comparator" 0 times. The book teaches no choosing rule
between similar functions, and it never tells the student that a function
can work on more than one kind of thing — because in the language as it
stands, no user function can. The generic *shape* already exists, but only
as user code the book never teaches: `examples/246_r23_comparator_sort.sm`
(`prakriya shreni(vibhag s, tulana)` with a comparator, and
`prakriya shreni_mukhya(vibhag s, tulana)` reading the sort direction out
of `tulana`) — and it still sorts integers, in any order, not any type,
because the comparator takes two raw values and the list is untyped.

### Which shape fits the teaching order

- **(a) Explicit type parameters — harder, worst fit.** It needs a new
  chapter 20, after chapter 18, and would be the most abstract concept in
  the book: a parameter that is not a value. It arrives after the student
  has already used the library for six chapters.
- **(b) Inferred/anonymous generics — easier, the only shape that helps a
  beginner.** The student learns nothing new: one `shreni(a, n)` that just
  works on whatever list it is given, taught as a library fact in chapter
  14 ("`shreni` sorts a list"). The student never writes a type parameter;
  the feature is invisible. The one condition: errors must name the list,
  not a type parameter — an error like "cannot sort: element type `dasham`"
  would be the first time the student met the word.
- **(c) Nothing — workable today.** The per-type functions don't exist yet,
  so there is no three-way choice to collapse; the student who never meets
  generics can still write programs, using the hand-written sort in
  `examples/215` as the pattern.

### The cost of never learning the word "generic"

Nothing breaks. The student loses only the one-call sort on non-integer
lists — and the four-sort choosing problem stays unsolved, because the
book never teaches it either. The word itself costs nothing; the *absence*
of the feature costs one concrete thing: the beginner who has a list of
words (or `dasham`, or a `kosh`) cannot sort it with the library, and must
write ~25 lines of bubble sort by hand.

**Task 4 verdict.** A generic function makes the language easier for the
beginner *only* in the inferred/anonymous shape, taught as one `shreni(a,
n)` that just works — because the book's teaching order (untyped functions
in ch. 7, first type in ch. 18, library as a name list in ch. 14) has no
place for an explicit type parameter, and the book never leads the student
to the word. The concrete need is sorting words (or a `dasham` list, or a
`kosh`) with the same one call a number list gets. Explicit type
parameters would be the hardest thing in the book; doing nothing is
workable today and costs the student exactly one thing — the one-call sort
on anything that isn't integers.

---

## Brief corrections

1. **`sort_int` / `sort_text` do not exist.** Whole-tree grep returns only
   the brief itself. The real sorts are `budbud_shreni` / `shankh_shreni` /
   `nivesh_shreni` / `mil_shreni` on `mala`, and `suchi_shreni` on lists.
   The library is already type-erased at the element level (64-bit cells);
   the duplication is per container and per wrapper, not per element type.
2. **`kosh_gan`, `kosh_iksh`, `parimana` are builtins, not library
   functions.** `kosh_gan` is the primary name of `kosh_len` (`BN_KOSHLEN`
   39); `kosh_iksh` is the primary name of `kosh_peek` (`BN_KOSHPEEK` 44);
   `parimana` is `BN_PARIMANA` 47. None is among the 310 `prakriya`
   definitions.
3. **"310 and not 150" overstates the duplication.** The counted
   duplication is 83 of 310 (46 separate implementations + 37 wrappers),
   collapsing to 227 (226 if both `maap` aliases go); keeping wrappers as
   named conveniences gives 264. The "150" would need 160 removals,
   roughly twice the counted number.
4. **"783 programs compile to identical bytes" is wrong.** The last guard
   line (v315 → v316, ELF and PE) is **587 byte-identical + 196 refused
   identically**, 0 DIFFER. Only 587 compile at all.
5. **"The library's 229 proofs" omits the second proof set.** 229
   `tests/stdlib/*.sm` files exist (recounted), but there are also **86
   property proofs** in `tools/proof_props.py`, so the proof corpus is
   **315**. `tools/guard_page.py`'s docstring still says 226/226 for the
   library proofs — stale.
6. **"327 suite tests" is the golden count, not the test count.** The suite
   runs **331** tests and **327** have goldens; the 4 without are
   `215_r12_wordfreq`, `216_r12_expr`, `217_r12_report`,
   `219_sanskrit_kosh_aliases`.
7. **"331 examples" is top level only.** Recursively there are **347**
   `.sm` files; 3 (`examples/r68/pairs/`) sit outside both the suite and
   the guard.
8. **"Deliver into: Muse-to-Saram/" is a typo** for `Muse-to-Sarvam/`; not
   followed literally.
9. **`tools/gates.sh` line 238's comment says doc signatures are "305/305"
   — stale.** The library has 310 declarations and the doc has 310
   first-column signatures by count; the gate itself compares live counts,
   so it would not fail, but the comment is out of date.
10. **R116 contracts: "sixteen vs fifteen" is unresolved.** The test
    file's docstring says sixteen contracts; the `tools/gates.sh`
    comment says fifteen. The checks are issued inside loops, so a
    call-site count is not a check count — could not be resolved by
    reading (see Could-not-determine).
11. **Book corrections, with locations.**
    - A — "one sort instead of three" doesn't match the tree: **4 sorts,
      1 type, 0 for others** (`lib/shreni.smlib` has 14 `prakriya`, all
      integer-only `(a, n)`).
    - B — EN ch. 7 says "up to three arguments" (EN:198–199) vs SA ch. 7
      "up to six" (SA:183–184) and EN:420 — the English ch. 7 is stale.
    - C — The book says `shreni` has 11 functions (EN:442) but the file
      defines **14**.
    - D — The stdlib reference claims "quick sorts"
      (`docs/sutram-stdlib-reference.html:628`) but **no quicksort
      exists** anywhere in the tree.
    - E — Module counts disagree: ch. 14 "twelve" (EN:437) vs ch. 18
      "fifteen" (EN:717, incl. `fileio`, which has no `.smlib`) vs
      **24 files in `lib/`**.
    - F — "331 examples" is top-level only; recursively there are **347**.

    One item the working notes had wrong, corrected here on verification:
    `docs/sutram-stdlib.html` **does exist** on this tip (481 lines), so
    the book's pointer to it is not a dead link; the module-count
    disagreement in E stands as written.

## Could-not-determine

- **G7 bit-identity.** `madhava_vargmool` and `sankhyiki_vargmool` differ
  by one start-guess clamp line (`v < 1.0` → start at 1.0). Whether the
  two return bit-identical results on all inputs is not established by
  reading — the clamp changes the iteration sequence, and Newton
  convergence does not guarantee the same final rounding. Not run;
  read-only.
- **The exact number of R116 contract checks** (docstring 16 vs gates
  comment 15; the file issues checks inside loops, so a call-site count
  is not a check count). Not run — read-only.
- **Whether the R28 linker and R31 incremental byte-equality gates would
  hold under a generic design** (separate-compilation paths treat module
  functions specially; the answer depends on the design, not on anything
  readable in the tree).
- **Whether collapsing a `.smlib` would shift line numbers cited in any
  compile-fail golden that references a library line.** Only 3
  compile-fail goldens name a lib function at all, and none read cites a
  library line number, but not every diagnostic's line reference was
  exhaustively checked.
- **Whether the 4 NO-EXPECTATION examples pass on this tip** — not run,
  read-only.

Resolved during verification: the two stdlib proof files that call no lib
function are `tests/stdlib/kosh_reuse.sm` and `tests/stdlib/width_repro.sm`.

## Summary

A kosh carries no element type at runtime, but the compiler tracks exactly
one element-type bit at compile time (int/raw vs binary64), while the
symbol table records no type at all and call resolution is by name plus
arity — so for user prakriyas there is no type information to build
generics on, though 46 of the 310 library functions are already generic in
effect over raw 64-bit cells; the library's duplication is 83 of 310
functions (46 separate implementations in 40 groups plus 37 wrappers),
collapsing to 227 (264 if wrappers stay as named conveniences), not the
brief's implied ~160, and the four sorts are four different algorithms
with zero per-type variants; any collapse that touches the library would
report ~135 DIFFER on the 783-program guard (282 for a whole-library
collapse), because every imported module is emitted whole into every
importer's binary — while the same beginner-facing feature can be delivered
with 0 DIFFER by a compiler-only change or a new module, keeping old names
as rewrites, and the proofs (229 + 86 = 315) and the suite's 327 goldens
would need call-site rewrites but no golden re-recording under a faithful
collapse; and for the beginner the only shape that helps is
inferred/anonymous generics — one `shreni(a, n)` that just works on words,
`dasham`, or a `kosh`, taught as a library fact in chapter 14 — since the
book never mentions the word, teaches functions untyped in chapter 7, and
only shows a first type in chapter 18, while doing nothing is workable
today and costs the student exactly one thing: the one-call sort on
anything that isn't integers.

---

*ROUND-170, read-only. Base: main at v315, tip `cb132a77`. Nothing compiled
or run. Counts re-derived on this tree; line numbers re-grepped on this
tree.*
