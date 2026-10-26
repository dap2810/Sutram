# Sutram ROUND-114 WS1 — full first-token frequencies from all 305 library declarations

**Pin:** `main=df4b5237b8962adda7f0693f1fc5bb1408567798` (changelog v347). Scope: every `prakriya` declaration in **24/24** present `lib/*.smlib` source modules; no source skipped or declaration parse error. Every name is split at underscores (`_`); the first component is counted even when it is a one-word function rather than a real semantic prefix. Duplicates: **0**.

## Measured totals

- Function declarations: **305**; distinct callable names: **305**.
- Distinct first components: **91**; of those, **63 occur exactly once**.
- 45 one-component names (no underscore), 174 two-component, 81 three-component, 5 four-component (none longer).
- Names beginning with their *own module name*: **171/305** (**56.1%**); cross-module and standalone names are common.
- Current draft's eleven claimed domain tokens: **102/305** (**33.4%**), including `ganita=18`, `vartani=0`, `akshar=1`, `mala=8`, `kosh=0`, `suchi=21`, `nighantu=17`, `sangrah=0`, `shreni=0`, `phal=14`, `roop=23`. The draft's intermediate 259-item extraction and 103/259 coverage is a **different dataset** and cannot replace this source-based count.

## Actual heavily used first tokens (count >=3)

| First token | Count |
|---|---:|
| roop | 23 |
| khand | 22 |
| suchi | 21 |
| ganita | 18 |
| varna | 18 |
| nighantu | 17 |
| brihat | 15 |
| phal | 14 |
| rakh | 14 |
| asti | 13 |
| avali | 9 |
| mala | 8 |
| purna | 6 |
| ank | 5 |
| anukram | 5 |
| madhava | 5 |
| chay | 4 |
| gan | 3 |
| patra | 3 |
| yog | 3 |

The remaining **71** first-token spellings occur once or twice (28? verify: 91 - 20 = 71), with all **63** single-occurrence tokens recorded in the JSON data. Use that machine-readable JSON for the authoritative list, not the table's top subset.

## Misleading assumptions exposed

1. **A module need not prefix its own functions.** `sangrah` defines fourteen `rakh_*` functions; no `sangrah_*` first token; `shreni` module has no `shreni_*` first token; `ganita` includes `kuttaka`, `chakravala`, `samasa`, `brahmagupta_kshetr`.
2. **A first token need not equal the module.** `brihat` occurs 15 times but `lib/brihat.smlib` has 13 functions: the additional two `brihat_ank_*` are defined in `lib/aadhar.smlib`.
3. **A first token does not always denote a domain.** `asti` is a predicate prefix; `rakh` is an action; `avali` and `chay` denote queue/stack families inside `suchi`. One-word names such as `simpson` are entire function names, not productive prefixes.
4. **The last component is not always a verb.** `akshar`, `ank`, `maap`, `shesh`, `mala` and others can be objects/qualifiers rather than an action; some 45 names have no compound split at all.
5. **A useful restricted derivation exists.** Strong module-family patterns `roop_*`, `khand_*`, `suchi_*`, `ganita_janchit_*` and `ganita_paripurna_*` are independently supported; specify *these families* precisely rather than claiming a full `<domain>_<qualifier>_<action>` grammar. No Sanskrit morphological correctness follows from an underscore count.

## Raw reproducible evidence

- [Part A: 119 declarations in 12 files](ROUND-114-RAW-NAMES-A.tsv)
- [Part B: 186 declarations in 12 files](ROUND-114-RAW-NAMES-B.tsv)
- [Full ordered frequency tables and the 63 singletons](ROUND-114-WS1-MEASURED-PREFIXES.json). Includes first-token and final-token frequency tables, module counts and 305-name coverage. It is calculated from these **source-read TSVs**, not from the HTML or vocabulary draft.

**PASS — all 305 source declarations counted; 0 unparsed. NOT RUN - no toolchain (native compiler).**