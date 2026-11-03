# R183 — replace the fixed failure token in compiler and packs together

2026-11-03. Pinned main: `9ace6e95fc10e94d986be4dbc255d001daced30e`, v292. Design/evidence only.

## Recommendation — Option B, with an explicit compatibility-policy change

**Change the fixed token `Sutram Error` to `Sutram truti` in the compiler and all eleven packs together. Keep message bodies, error codes, punctuation, placeholders and exit behavior unchanged. Keep `Sutram suchana:` for the existing nonfatal notices.**

This is a **vocabulary/interface change, not a bug fix**. The present packs follow the existing rule correctly. It needs an explicit owner decision allowing this exact token substitution in the ten frozen packs and accepting the corresponding diagnostic-byte changes in generated binaries and expected outputs. It cannot simultaneously satisfy “the ten files stay byte-for-byte unchanged” and “their literal prefix changes.” No implementation trick removes that conflict.

The frozen-pack boundary otherwise stays intact: no new translations, no body rewrites, no new keys, no language development. This report supplies a concrete decision and inventory, not permission to modify those files.

## WS1 — all eleven files contain the English token literally

I retrieved and parsed all eleven `lang/*.sandesh` files at the pinned commit. Each has **142 non-comment key/value entries**, of which **68 contain the literal `Sutram Error`**. Across the eleven packs: **748 affected values**, not 109. These are parsed message-value counts; comments also repeat default strings and were excluded.

The following are exact JSON-string values of the same key, `r48_msg_near`, per file. The leading colon/space and final opening quote are real parts of the fragment:

| File | All values | Values with literal token | Exact r48_msg_near value |
|---|---:|---:|---|
| lang/bengali.sandesh | 142 | 68 | `": Sutram Error [E_PARSE]: শব্দ '"` |
| lang/gujarati.sandesh | 142 | 68 | `": Sutram Error [E_PARSE]: શબ્દ '"` |
| lang/hindi.sandesh | 142 | 68 | `": Sutram Error [E_PARSE]: शब्द '"` |
| lang/kannada.sandesh | 142 | 68 | `": Sutram Error [E_PARSE]: ಪದ '"` |
| lang/malayalam.sandesh | 142 | 68 | `": Sutram Error [E_PARSE]: വാക്ക് '"` |
| lang/marathi.sandesh | 142 | 68 | `": Sutram Error [E_PARSE]: शब्द '"` |
| lang/odia.sandesh | 142 | 68 | `": Sutram Error [E_PARSE]: ଶବ୍ଦ '"` |
| lang/punjabi.sandesh | 142 | 68 | `": Sutram Error [E_PARSE]: ਸ਼ਬਦ '"` |
| lang/sanskrit.sandesh | 142 | 68 | `": Sutram Error [E_PARSE]: शब्दः '"` |
| lang/tamil.sandesh | 142 | 68 | `": Sutram Error [E_PARSE]: சொல் '"` |
| lang/telugu.sandesh | 142 | 68 | `": Sutram Error [E_PARSE]: పదం '"` |

The body after the token is **the selected language's translation**, not Sanskrit in every file. The Sanskrit pack uses Devanagari Sanskrit. Without `--lang`, the default text comes from the compiler's Romanized Sanskrit strings.

There are templates such as `{kw:kosh_pop}` for code words and `{ver}` for the version, but **no prefix placeholder**. For example:

- Sanskrit `msg_kosh_empty`: `"Sutram Error: रिक्तात् कोशात् {kw:kosh_pop}\n"`.
- Gujarati `msg_kosh_empty`: `"Sutram Error: ખાલી કોશમાંથી {kw:kosh_pop}\n"`.
- Hindi `msg_kosh_empty`: `"Sutram Error: खाली कोश से {kw:kosh_pop}\n"`.

[ROUND-183-PREFIX-INVENTORY.json](ROUND-183-PREFIX-INVENTORY.json) supplies **every affected key and exact before/after value in each file**, including escaped newlines and placeholders. It also records the source lines containing the old token. No values were edited in the packs.

### How the strings reach output

`tools/sandesh.py` reads each JSON value and expands only the supported placeholders. It generates `src/r11_sandesh.inc`; it also generates the IDE translation include. The compiler's `r11_tr` selects a message pointer by original-message address and current language. It does not prepend a universal Error prefix. `r11_tr_rcx` performs the corresponding lookup for strings stored into emitted programs.

The checker explicitly treats `Sutram Error` as an invariant token:
`TAGS = re.compile(r'Sutram Error|\\[E_[A-Z0-9_]+\\]')`.
It compares the sequence of these tokens with the default, checks edge punctuation, permitted Latin/code words, script and completeness. Merely editing the packs or defaults alone makes those checks inconsistent.

The brief's “every diagnostic” is also too broad: many entries are hints, success summaries, fragments or IDE statuses; notices already use suchana. The ungenerated source scan found **120 lines containing the token** across five files: 115 in sutram_compiler.asm and five in includes. This is a line count, not a unique diagnostic-kind count. The old 109 figure is not the current inventory.

## WS2 — the three options and the decision

| Option | Assessment |
|---|---|
| A: compiler only because packs do not mention prefix | Its premise is false: all eleven contain it. A special output-time substitution could be invented, but adds transformation paths, complicates embedded runtime messages and silently changes the frozen packs' displayed contract. Do not do that. |
| **B: compiler and packs together** | **Choose this.** One invariant token is replaced explicitly in all sources and values; checker keeps enforcing the same invariants with the new token. |
| C: retain Error, append Sanskrit | Reject. `Sutram Error: truti -` duplicates classification, keeps the English word and still changes messages. Keeping Error wholly unchanged is a valid deferral if the owner declines B, but does not meet this round's desired outcome. |

**Cost:** 748 pack values; source literals/fragments in five files; checker/templates and focused tests; regenerated tables; affected expected outputs; documentation. The replacement words Error and truti both occupy **five ASCII bytes**, so the token substitution itself does not require a message-length or layout change. Still verify emitted code and offsets rather than assuming every build byte remains unchanged.

**What breaks:** consumers matching the old prefix, old diagnostic goldens and binaries containing changed runtime text cease to be byte-identical to their baseline. Codes, bodies, exit statuses and refusal behavior should remain unchanged. Claude R110/R111 report 443 old guard programs containing runtime messages; that is an attributed historical measurement, **not a fresh exact impacted-program count at this head**. Recount on the implementation's pinned base, and inspect every differing binary. Do not relabel all differences acceptable by default.

## WS3 — is truti the right word?

**Use truti as the conventional failure-severity token, not as a judgment that the programmer has written a faulty program.** A safety refusal, resource exhaustion, missing input or syntax error can all stop the requested operation for different reasons. Retain their distinct E_ codes and explanatory text. In particular:

`Sutram Error [E_APARIKSHITA_AHVAN]: ...`
becomes
`Sutram truti [E_APARIKSHITA_AHVAN]: ...`.

This means “the requested compilation failed/refused”; it does **not** claim the program is proven unsafe. Document that distinction. A safety refusal must not be downgraded to a notice just to avoid the word fault.

There are two independent dimensions: **severity/outcome** (blocking failure versus nonblocking warning/notice), and **reason** (syntax defect, policy refusal, environmental failure, etc.). Making four different top-level prefixes from “fault/refusal/warning/notice” mixes those dimensions. For this smallest migration, preserve the existing classification and rename only its failure token. Keep the existing deprecation text exactly:
`Sutram suchana: 'kosh_push' purana nama - 'kosh_kship' likhatu`.

A future warning distinct from a notice can receive a separately reviewed label and structured severity. That is not needed to replace Error, and this round should not silently reclassify diagnostics or introduce four new public words.

**Lexical confidence is bounded.** The [Yates entry reproduced by Wisdomlib](https://www.wisdomlib.org/definition/truti) includes a fault, but the [Monier-Williams entry hosted by UoH](https://sanskrit.uohyd.ac.in/SKT/MW/112.html) lists other senses such as a tiny interval, doubt and breaking. Thus I do not claim that every classical lexicon defines truṭi as a modern compiler error. It is a reasonable technical convention for the owner's requested label, not a proof from etymology. Native-speaker review of the terminology: **NOT RUN**. The prefix should follow the existing `Sutram <classification>:` pattern, while E_ codes and prose preserve the actual reason.

## WS4 — exact migration contract and files

**Exact change:** replace the fixed diagnostic token `Sutram Error` with `Sutram truti`, preserving the rest byte-for-byte. Examples:

| Before | After |
|---|---|
| `Sutram Error:` | `Sutram truti:` |
| `: Sutram Error [E_PARSE]: shabd '` | `: Sutram truti [E_PARSE]: shabd '` |
| `: Sutram Error [E_APARIKSHITA_AHVAN]: parikshita prakriya '` | `: Sutram truti [E_APARIKSHITA_AHVAN]: parikshita prakriya '` |
| `Sutram Error: रिक्तात् कोशात् {kw:kosh_pop}` | `Sutram truti: रिक्तात् कोशात् {kw:kosh_pop}` |
| `Sutram suchana:` | unchanged |

The appendix contains the complete 748-value before/after inventory, so no translation is left implicit.

Files requiring the scoped change:

1. **All eleven pack files listed in WS1.** Change affected values; update their explanatory comments/default mirrors consistently. Preserve key order, key set, all translations and placeholders.
2. **Five ungenerated source files:** `src/sutram_compiler.asm`, `src/r52_yoj_hint.inc`, `src/r66_indic_lexer.inc`, `src/r68_diagnostics.inc`, `src/r71_unsafe_integration.inc`. Include the shared prefix fragments and runtime-embedded strings, not just the translated KEYS set.
3. **tools/sandesh.py:** replace the fixed token in TAGS and the template/invariant documentation. Remove Error from the allowed code-word set; recognize the new token as the invariant. Continue comparing the full tag sequence and rejecting missing/duplicated prefixes, altered E_ tags, changed punctuation, wrong-script prose, unknown keys and incomplete packs. Do not broadly allow arbitrary Latin “truti” everywhere.
4. **Generated outputs:** regenerate `src/r11_sandesh.inc` using the generator. Regenerate/check `windows/gui/r11_ide_sandesh.inc` too; commit it only if the generated bytes actually change. Do not hand-edit generated tables.
5. **tests/sandesh/test_sandesh.py** and affected golden files under `tests/sandesh/expect/` and `tests/expect/`: change only expected prefix bytes and add a negative test rejecting the retired Error token. Preserve the genuine negative cases. Locate any other exact-prefix assertions before implementation; historical reports mention 81 general goldens, not recounted here.
6. **docs/SANDESH.md**, **docs/LANGUAGE-REFERENCE.md** and **LANGUAGE-PRIORITY.md**: document the new invariant, failure-severity meaning and narrow owner-approved freeze exception. Update other active exact-prefix consumers found by repository search; do not rewrite historical handoff evidence to make it appear it always used truti.

Implementation acceptance: compare every pack key/body/placeholder before and after after normalizing only this one token; run the Python pack/generator tests; native compile/refusal/runtime cases in default and each pack; verify notice behavior and exit status unchanged; inspect binary differences against the exact replacement spans. Preserve tests for default fallback and E_APARIKSHITA_AHVAN refusal. Native Windows acceptance remains separate from generated-table or Wine checks.

**Do not claim “0 DIFFER.”** The correct acceptance claim is “all differences accounted for by the approved diagnostic-token migration,” backed by the actual binary/text comparison. Do not simply refresh every golden and declare success.

One owner decision is sufficient to make the proposed work unambiguous: approve B's exact fixed-token change in all eleven packs and source diagnostics, with the narrow frozen-pack exception and audited diagnostic-byte differences. No pack or compiler changes are made by this read-side report.

## Evidence and corrections

Claude R112 explicitly says the R111 pack-messages failure was caused by the new **deprecation warning under --lang**, not by a shipped Error→truti change. The earlier R110 scratch experiment did demonstrate a prefix/gate conflict. The brief conflates these events; the literal-file evidence above does not depend on that summary.

Executed here: retrieval and JSON parsing of all eleven packs, prefix-value inventory, source text scan and exact proposed substitution inventory. Full `sandesh.py --check`: **NOT RUN** (no complete local build/check tree assembled; no claim of a passing revised gate). Native build, suite, runtime probes, guard and Windows: **NOT RUN — no native toolchain/Windows environment**. No compiler, pack, tooling, test or Windows changes. Only this report and its evidence appendix.
