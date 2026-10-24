# Sutram Round 109 WS1 — Is the generated stdlib reference stale, or the generator?

**Current pinned tree:** `dfd0da5d14ef2ab51f7d74ca31193ea21bb9481b` (changelog v329, 23 Oct 2026). **Read only:** `tools/gen_stdlib_ref.py` blob `7d13129e1aba99cf62ccfe3f7ec33e45d4bbf433`, all 24 `lib/*.smlib` modules, `docs/sutram-stdlib.html` blob `a120fe5739598131dab3768655eab60620536321`, Muse R33 proposed patch, owner Round 34 brief. No source edited and **NOT RUN - no toolchain** for actual generator execution or native Sutram.

## Verdict: BOTH an old generated artifact and old SOURCE COMMENTS; not an old keyword conversion table in the generator

**The committed page is structurally stale.** It shows `brihat — 12 functions`, `samanvaya — 10 functions` and its footer `24 modules, 303 functions`; the current library has `brihat` **13**, `samanvaya` **11**, and **305 total `prakriya` declarations in 24 modules** (source-read count). The current `lib/chandas.smlib:82` defines **`meru_pankti(a, n)`**, but committed HTML `:107` lists `meru_mala(a, n)`. A new regeneration will pick up the **actual current function signature** instead of that old HTML entry. The name `meru_pankti` is an actual current FUNCTION IDENTIFIER. It is NOT evidence that the obsolete array keyword `pankti` has been reintroduced as grammar. **Do not revert `meru_pankti` to `meru_mala` without an independent API migration decision.**

**The generator's mechanism is current but has no semantic vocabulary validation:** `tools/gen_stdlib_ref.py` opens the actual `lib/*.smlib` files, takes the leading `#` comment block as each module description (except lines beginning `lib/`), takes `prakriya NAME(args)` as signatures, and concatenates `#` comments immediately preceding functions as descriptions. It sorts modules, writes `docs/sutram-stdlib.html`, and computes counts from parsed function declarations. There is **NO literal replacement table for `pankti`, `ayojan`, `meru_pankti` or `ganit_`, and no intentional old-word emission in the HTML template**. Therefore generator code itself does not need a stale-name *replacement* fix.

**BUT the current SOURCE COMMENTS are stale, so regeneration alone is insufficient for copy/paste correctness.** `lib/sadhan.smlib:1,4` still says `util.smlib` and active-looking `Usage: ayojan util`. `sadhan` is the actual module name, and `yoj` is the current include keyword; that source header will be emitted verbatim by the existing generator. A comment in `lib/suchi.smlib:211` mentions old `ayojan sort` in an explicitly historical narrative; label it historical if reproduced, not present-day guidance. Many current source comments label qword arrays `pankti`; those are obsolete terminology for the present array keyword `mala`.

## Every SOURCE COMMENT emitted by the generator that carries a suspect old-word spelling

**`pankti` as a stand-alone old array word: 16 emitted source-comment lines**, counted in all 24 actual current library files (the following line numbers are source lines, NOT HTML lines). Do not count the substring inside the legitimate function name `meru_pankti` as an array token.

| Module | Exact source comment lines containing whole-word `pankti` | Context/meaning |
|---|---|---|
| `lib/aadhar.smlib` | **5, 15, 74** | Intermediate digit array, output digit values, input digit values |
| `lib/gudh.smlib` | **12, 28** | Hash input byte array descriptions |
| `lib/nighantu.smlib` | **4** | Map storage arrays |
| `lib/phal.smlib` | **4** | Two-cell Result storage |
| `lib/roop.smlib` | **8** | Numeric formatter input-cell-array comparison |
| `lib/shreni.smlib` | **4** | In-place integer array |
| `lib/suchi.smlib` | **4, 33** | List cells and one-cell `ok` buffer |
| `lib/vakyank.smlib` | **6, 12, 81, 83, 235** | Numeric-character arrays, output padding and `ok` buffer |
| **TOTAL** | **16 source-comment locations** | Generator has **no awareness** these labels are old keyword vocabulary |

**`ayojan` and `util` source headers:**
- `lib/sadhan.smlib:1` `“Sutram Utility Library - util.smlib”` — old module file name. **Generated module heading is `sadhan`**, but this comment embeds the obsolete `util` reference.
- `lib/sadhan.smlib:4` `“Usage: ayojan util”` — **incorrect as present-day instruction**; correct syntax should mention `yoj sadhan`. If generated now, `ayojan util` will reappear even though committed HTML still shows `Usage: yoj sadhan`.
- `lib/suchi.smlib:211` `“sorting a list meant ayojan sort plus a hand-written…”` — history explicitly framed as “meant”; not an active usage instruction; can remain if unmistakably labeled history, but it **will** be emitted in a function description.

**Other apparent rename patterns that are NOT demonstrated stale generator vocabulary:**
- `meru_pankti` is **valid current function source** in `lib/chandas.smlib:82`. Its appearance in regenerated HTML is **structural correction**, not a language keyword regression; committed HTML `meru_mala` is stale.
- `ganit_yadricch` and `ganit_seemit` appear in `lib/ganit.smlib` current function declarations and comments. The prefix `ganit_` denotes actual APIs; no evidence warrants global replacement of these names. An old-word sweep that blindly changes it could break the reference.
- A literal keyword-token `pankti` and a suffix in a legitimate function **must be classified separately**; whole-word source-comment detection is a review signal, not a justified automated replace.

## Why the current generator cannot fix this by itself

`gen_stdlib_ref.parse_module` uses basic regular expressions and direct comment extraction. It **cannot validate** whether a comment's `Usage` example compiles, whether a function name was renamed, or whether source comments match the current grammar. It will faithfully expose *whatever the current library says*, correct or obsolete. This is not a stale generator's substitution logic; it is a **provenance/validation gap in comments and generated artifacts**.

**Safest sequence for Muse (owns `lib/`, `tools/`, generated `docs`)**: (1) pin clean current tree; (2) review source comments for old vocabulary, correct **active instructions only** (e.g. `sadhan` header), deciding whether obsolete `pankti` prose should say `mala` or `qword-cell array`; (3) do NOT rename actual `prakriya` identifiers such as `meru_pankti` or `ganit_*` without an API review; (4) regenerate the page from approved current source; (5) diff module/function inventory and inspect every old-word hit with whole-token and context-sensitive checks, not a global replace; (6) only then run accepted native gates under the capable partner; (7) commit regenerated artifact separately, with source hash and raw output.

## Status and evidence boundaries

- **PASS source read:** actual generator algorithm, full current library names/signatures (24 modules / 305 declarations), old committed page (303 function footer), current source comment locations.
- **PASS version-aware classification:** old committed output vs generator mechanism vs source-comment terminology, with exact exceptions for valid function names.
- **NOT RUN - no toolchain:** executing the generator, building the compiler, real Sutram sample, proof library, docs-gate, Linux/Windows acceptance. Consequently the “regenerated output would” statements are **static predictions grounded in the generator's actual code**, not a claim of a fresh generated file.
- **Files changed:** this new audit document only. No `lib/`, `src/`, `tests/`, `tools/`, generated HTML, Windows channel, language packs or `backups/` changed by ChatGPT.
