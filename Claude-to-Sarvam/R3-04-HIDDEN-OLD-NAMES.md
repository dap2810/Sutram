# ROUND-03 / WS4 — old names hidden behind escapes, quotes and other boundaries

**Date:** 2026-10-19 · **Base:** main `85d6c5f` (v169) · **Code:** branch `claude/round-03`, commits `6f13c93e`, `494e1b21`

---

## 0. The most important result is not a rename leftover — read this first

**Two pre-v157 keywords still compile, with no error, and silently change what the program does.** An
undefined name is accepted and read as 0. A bare name is a valid statement. So an old keyword is not
rejected; it is parsed as a variable:

```
$ cat old.sm                                 # uddeshya was `continue` before v157
mukhya() {
    chakra i = 0 tak 4 {
        yadi (i == 2) { uddeshya }
        likha(i)
    }
}
$ sutram old.sm o.bin && ./o.bin    →  0 1 2 3 4      exit 0      (with `agrim`: 0 1 3 4)

$ cat r.sm                                   # pratiyati was `return`
prakriya f(x) {
    yadi (x > 0) { pratiyati 1 }
    pratiyati 2
}
mukhya() { likha(f(5)) }
$ sutram r.sm r.bin && ./r.bin      →  2              (with `prati`: 1)

$ printf 'mukhya() {\n    likha(zzz)\n}\n' > u.sm && sutram u.sm u.bin && ./u.bin   →  0
bare old keyword as a statement:  nishedha / parigrah / srijana / pankti / nishkriya   →  Siddh: 183 byte sankalit
```
`punaravartana`, `anyatra` and `ayojan` do fail with a parse error. So a pre-v157 program fails loudly
only *sometimes*. With `pratiyati` or `uddeshya` in it, the program compiles and gives a wrong answer.

That is a language-semantics gap (Gate 4), not a string. Two ways to close it, both outside this
round's brief, so **described, not implemented**:
1. **An undefined-variable error.** `agyat vitti 'X'` at the first read of a name that was never
   declared. This is the right fix. It changes the parser's symbol handling, so it is a structural
   change. Some existing examples may rely on the read-as-0 behaviour, and the suite would show which.
2. **A narrow guard.** Put the 11 old spellings in `kw_table` mapped to a new `KW_OLD` id, so the
   lexer fails with `Sanket: 'pratiyati' v157 se 'prati' hai`. It is contained (a table plus one
   branch in `parse_stmt`). But it reserves eleven words forever, and it only treats a symptom.

## 1. What I did

1. **Built the old-name list, 296 names.** The 11 keywords from the v157 CHANGELOG, 3 builtins, 18
   module names, and **264 function names derived, not typed**. For the functions, I paired each
   module's `prakriya` definitions at the last pre-rename commit `ca53eab` (v156) with current
   `lib/*.smlib`, in definition order. Counts match for all 24 modules; 264 equals the CHANGELOG's
   "264 of 303"; 25 random pairs spot-checked.
   *Side finding:* `docs/sutram-vocabulary.html`'s "All 303 function names" table **cannot** be used as
   an old-name list. It has the new name in both columns, because the file was committed already renamed
   (`76b161d`). Its keyword table is correct.
2. **Scanned every tracked file** (from a pristine `git archive` of `85d6c5f`). Every maximal identifier
   run was classified:
   - **(a) boundary** — a `\b` sweep would see it
   - **(b) escape-hidden** — the old name appears only after stripping what an escape or format glued on:
     `\n \t \r \b \f \v`, `\xHH`, `\uHHHH`, `%s %d …`, leading digits
   - **(c) identifier-internal** — e.g. `kw_ayojan`, `KW_PANKTI`
   - **(d) ordinary English** — `to set map list file …`
3. **Checked four further boundaries** a Latin, case-sensitive `\b` sweep cannot see: capitalisation,
   hex-encoded bytes (`db 0xE0,…`), `\u`/HTML-entity escapes, and compound notation (`a/b/c` lists,
   `prefix_*` wildcards).
4. **Proved the detector on the known bug before trusting it.** On v167's
   `test_module_graph_reference.py`:
   ```
   grep -c '\\nayojan'   → 7 lines       grep -cP '\bayojan\b' → 0
   detector: boundary 0, escape 10       (ESCAPE 21 'yoj b\\nayojan c\\np', …)
   ```

Script: `scratchpad/r3/ws4/sweep.py` (re-run with `python3 -I sweep.py <repo-root> <out-dir>`). I can
commit it under `tools/` if you want it as a standing check. It is not on the branch, because it is not
a gate.

## 2. How far the escape class reaches: **nowhere else on main**

| v169 tree | (a) boundary | **(b) escape** | (c) identifier | (d) English |
|---|---|---|---|---|
| tree (excl. handoff, CHANGELOG) | 1303 | **0** | 431 | 3136 |
| `docs/CHANGELOG.md` | 123 | 0 | 13 | 530 |
| handoff folders | 8473 | 13 | 364 | 5474 |

The `\n`-adjacent class itself is fully repaired on main (v168 fixed the seven). A plain-grep
cross-check (`grep -lP '\\n(to|sort|list|map|set|file|ayojan|pankti)\b'` over every non-handoff file)
returns nothing. The 13 handoff hits are R2/R3 reports *quoting* the bug. The large (a) count is
dominated by `inc`: the old name of `vardh`, but also the x86 instruction and the `.inc` extension. In
code contexts it is legitimate.

**But the same failure — a boundary the sweep did not cover — reaches much further.** These are the
stale hits, by the boundary that hid them.

## 3. Stale hits, and what happened to each

| # | Boundary that hid it | Where | Stale text | Status on the branch |
|---|---|---|---|---|
| 1 | **HTML markup** around a token | 5 books (gu, hi, sa, ta, te), **25 code blocks** | `chakra i = 1 <span …>to</span> 5` — **all 25 failed to compile**; plus 74 tooltips `…: to · range-to` | **FIXED** (`to`→`tak`, tooltips). 30/30 `chakra` blocks compile. v165's CHANGELOG claim that these editions use native-script samples is **not correct for these blocks**. |
| 2 | **a NUL inside a byte table** | `ide/sutram_gui_linux.asm` `kw_tab`, `bi_tab` | every Devanagari row ended `,0,0`. To `match_tab`, an empty entry means **end of table** | **FIXED — the largest find of the round.** See §4. |
| 3 | a data table of builtin names | `ide/sutram_gui_linux.asm:203–204` | `char_at`, `char_code`, `set_char` (renamed in v157) | **FIXED** → `akshar`, `aksharank`, `akshar_rakh`; also added `sankhya` to `kw_tab` |
| 4 | **string literals that print code** | `examples/29_nishkriya.sm`, `07_module.sm`, `10_mathlib.sm`, `func_demo.sm` + goldens | prints `nishkriya("B8 …")` while the code uses `yantra(…)`; `square(9) =` after calling `vargit`; `Calling math()` before calling the user function the rename turned into `ganit()` | **FIXED** — labels; four goldens re-recorded, only those lines change (deliberate behaviour change). `08_demo`'s `double(21) =` describes the user's own `double_it`, so it was left as is. |
| 5 | a regex inside a test | `tests/r68/test_r68.py:186` | `nishkriya\(` against an example that says `yantra(` | **FIXED** (R3-01 §5.2) |
| 6 | **x86 instruction text** inside a Python string | `tools/r66_prepare_review.py:117,136` | `vardh r13`, `vardh ecx`: the rename `inc`→`vardh` hit the **instruction** `inc` | tool **RETIRED** (R3-01 §4.4) |
| 7 | **a label suffix** inside a Python tuple | `tools/r65_source_gate.py:20` | `("add","sub","mul","div","shesh")`: `"mod"`→`"shesh"`, but it names the assembly label `r65_msg_mod` | tool **RETIRED** (R3-02) |
| 8 | **a dict key** | `tools/r71_prepare_review.py:19,22` | `'src/r66_indic_lexer.vardh'`, `'src/r68_diagnostics.vardh'` | **reported to ChatGPT** (R71 family left alone) |
| 9 | a file path in a workflow | `.github/workflows/r53-integrated.yml:57` | `sha256sum … lib/string.smlib` (now `varna.smlib`) | workflow **RETIRED** (R3-02 §6) |
| 10 | **compound notation** `a/b/c` | `docs/ERROR-CONVENTION.md:101`, `docs/NUMERIC-CONTRACT.md:27,70,74` | `phal_janchit_yuj/sub/mul/div/shesh`, `ganita_janchit_yuj/sub/mul`, `roop_dash/hex/hex_upper/oct/bin`, `roop_pad_vam/right/center` | **FIXED** (each full name verified to exist in `lib/`) |
| 11 | compound notation, in the library | `lib/phal.smlib:81` (+ generated `docs/sutram-stdlib.html:297`); `tools/proof_props.py:2729` `suchi_shreni/min/max/sum/count` | same pattern | **reported to Muse** (library and proofs are Muse's) |
| 12 | `prefix_*` wildcards | `strb_*` ×13, `ganita_checked_*` ×8, `ganita_sat_*` ×8, `str_*` ×3, `list_*`/`queue_*` ×4 (`lib/suchi.smlib:15`), `result_checked_*` ×2 (`lib/phal.smlib:7`) — in PROPERTY-NET, STRING-BYTE-PARITY, EDGE-COVERAGE-30, LIBRARY-BOUNDARY, OVERFLOW-SAFETY and two lib files | old English prefixes | **reported**, not fixed: the doc ones are a judgement call about which family is meant; the lib ones are Muse's |
| 13 | **comment headers** | **17 of 24** `lib/*.smlib` headers | `# lib/array.smlib` at the top of `mala.smlib`, etc. | **reported to Muse** |
| 14 | **capitalisation** | `docs/sutram-book-english.html:218`; `examples/19_srijana_enum.sm:1` | `<i>Pankti</i> … Declare an mala with` (also "an mala"); `# Srijana (enum/constants)` | **reported** (prose about the old keyword; needs a rewrite of the sentence, not a substitution) |
| 15 | **hex-encoded bytes** | `src/sutram_compiler.asm:698, 706, 707` | `kw_dev_pankti` = पङ्क्ति, `kw_dev_anyatra` = अन्यत्र, `kw_dev_pratiyati` = प्रत्यायति | **reported** — the ROUND-01 WS2 §3.2 language decision; no text sweep of any kind can reach them, only decoding |
| 16 | `windows/` | `windows/gui/sutram_gui.asm:331,333` | the same three old builtins; `kw_words` with `ayojan`, `nishkriya`, `pratiyati` | **reported to ChatGPT** (out of bounds) |

**Legitimate, checked and left alone:**
- `pankti` in the diagnostic `vyakaran dosh, pankti 4:5` is the Sanskrit word *line*, not the old keyword.
- `tests/r71/existing_semantics.json:10` is a hash-pinned capture. Renaming it would break the capture —
  though per §0, that captured text now *compiles to a wrong answer*.
- Historical round artefacts under `compiler/`, `*.patch`, `docs/R5x–R7x`.
- Python false positives: `set(…)`, an X11 `fmt` variable.
- The 431 identifier-internal names (`kw_ayojan`, `prop_strb_dup`) are not user-visible. A few of
  `proof_props.py`'s *printed* labels (`"FAIL fmt pad_vam len"`) are cosmetically stale.

## 4. The X11 highlighter: no Latin keyword has been coloured since 14 October

`match_tab` (`ide/sutram_gui_linux.asm:1310`) walks a NUL-separated table and **stops at the first empty
entry**. The file's own comment says so: "NUL-separated, empty entry terminates". Slice 23 (`2db5f4c7`,
14 Oct) added six Devanagari keyword rows and one Devanagari builtin row, each ending `,0,0`.
Walking the assembled tables exactly as `match_tab` does:

```
before:  kw_tab 1 ['मुख्य']          bi_tab 1 ['द्वारम']
after:   kw_tab 37 [... 'mukhya', 'vitti', …, 'tak', 'bhavana', 'sankhya']   (all 28 current keywords; missing: [])
         bi_tab 15 ['द्वारम', 'dvaram', 'band', 'sthagita', 'akshar', 'aksharank', 'akshar_rakh', …]
```
So **v163's keyword-table update could never take effect**: the words it added were behind the
terminator. I checked this by watching the X protocol. I paired each `ImageText8` run with the GC
foreground in force when it was drawn:

```
               before (v169 GUI)          after (branch)
likha          0xdfe7ee  (default)        0xe86d11  (keyword)
yadi           0xdfe7ee  (default)        0xe86d11  (keyword)
zzzzz          0xdfe7ee                   0xdfe7ee
```
**Why `test_x11_colour.py` passed anyway:** it checks that the keyword colour appears *somewhere* in the
stream, and it does, in window chrome. Typing `zzzzz` instead of `likha` also "passes". I added one
check: the run whose text is `likha` must be drawn in `COL_KW`.
```
old GUI:  FAIL: the keyword run 'likha' is not drawn in the keyword colour: ['0xdfe7ee', … ×8]
new GUI:  PASS: keyword/string/number/default colours all present
X11 suite with the new GUI:  17 PASS / 1 FAIL (test_x11_edscroll — times out identically on the v169 and feef075 GUIs)
```

## 5. What I did not do

- Did not touch `lib/`, `tools/proof_props.py` (Muse), `windows/` or the R71 family (ChatGPT). Their
  items are in the table with file:line.
- Did not decide the Devanagari spellings (#15) or implement either fix in §0. Both are language
  decisions.
- Did not read the 3,136 class-(d) English hits one by one. A code-context test (old name followed by
  `(`, after `yoj`, or as `lib/NAME.smlib`) separated them, and §3 #4 came out of its positives. A
  pure-English occurrence that is Sutram code in a context the test does not recognise could remain. I
  did not verify that there is none.
- Did not sweep Devanagari-script old words in plain UTF-8 text (e.g. `उद्देश्य — continue` in the book
  prose). That is the same language decision as #15.
