# ROUND-35 WS1 — every old-vocabulary token in lib/ (base v334, b3f8a43e)

Scope: `lib/*.smlib` only (24 modules). Classification: identifier = a name callers use;
comment/header = prose; Usage = a line a reader copies.

## A. Identifiers — the serious ones (1)

| File:Line | Old | New | Callers |
|---|---|---|---|
| `lib/chandas.smlib:82` | `meru_pankti(a, n)` | `meru_mala(a, n)` | `tests/stdlib/chandas_meru_pankti.sm:4` (updated with the fix) |

No other function definition in `lib/` uses an old module/keyword stem as a prefix
(checked all `prakriya` names against sort/list/map/set/array/string/file/hash/
result/fmt/util/serial/bigint/num/strconv/baseconv/strb/math/pankti/ayojan).

Borderline, NOT fixed (see report): `lib/sadhan.smlib:40` `util_chinha(n)` —
the name carries the old `util` stem, but `util_chinha` is also used throughout
`lib/` as the generic term for "sign" (e.g. roop comments "no util_chinha"),
and it is called by `tests/stdlib/util_sign.sm` and
`tests/stdlib/r18_sign_digits_kramgun.sm`. Renaming it is a wider API decision;
left for the owner.

## B. Headers with old file names (comments, 18 files)

| File | Header says | Current file |
|---|---|---|
| `lib/aadhar.smlib:1` | `lib/baseconv.smlib` | `aadhar.smlib` |
| `lib/ank.smlib:1` | `lib/num.smlib` | `ank.smlib` |
| `lib/anukram.smlib:1` | `lib/serial.smlib` | `anukram.smlib` |
| `lib/brihat.smlib:1` | `lib/bigint.smlib` | `brihat.smlib` |
| `lib/ganit.smlib:1` | `lib/math.smlib` | `ganit.smlib` |
| `lib/gudh.smlib:1` | `lib/hash.smlib` | `gudh.smlib` |
| `lib/khand.smlib:1` | `lib/strb.smlib` | `khand.smlib` |
| `lib/mala.smlib:1` | `lib/array.smlib` | `mala.smlib` |
| `lib/nighantu.smlib:1` | `lib/map.smlib` | `nighantu.smlib` |
| `lib/patra.smlib:1` | `lib/file.smlib` | `patra.smlib` |
| `lib/phal.smlib:1` | `lib/result.smlib` | `phal.smlib` |
| `lib/roop.smlib:1` | `lib/fmt.smlib` | `roop.smlib` |
| `lib/sadhan.smlib:1` | `util.smlib` | `sadhan.smlib` |
| `lib/sangrah.smlib:1` | `lib/set.smlib` | `sangrah.smlib` |
| `lib/shreni.smlib:1` | `lib/sort.smlib` | `shreni.smlib` |
| `lib/suchi.smlib:1` | `lib/list.smlib` | `suchi.smlib` |
| `lib/vakyank.smlib:1` | `lib/strconv.smlib` | `vakyank.smlib` |
| `lib/varna.smlib:1` | `lib/string.smlib` | `varna.smlib` |

## C. Usage lines (a reader copies these) (2)

- `lib/sadhan.smlib:4` — `# Usage: ayojan util` (current: `yoj sadhan`)
- `lib/suchi.smlib:211` — `# sorting a list meant `ayojan sort` plus a hand-written…`
  (historical aside, but uses both old tokens)

## D. `pankti` as the array keyword, in comments (19 lines)

- `lib/aadhar.smlib:5,15,74`
- `lib/ganita.smlib:188`
- `lib/gudh.smlib:12,28`
- `lib/nighantu.smlib:4`
- `lib/phal.smlib:4`
- `lib/roop.smlib:8`
- `lib/sankhyiki.smlib:120`
- `lib/shreni.smlib:4`
- `lib/suchi.smlib:4,33`
- `lib/vakyank.smlib:6,12,81,83,235`
- `lib/varna.smlib:127`

No non-comment use of `pankti` remains after the `meru_pankti` fix.

## E. Old file names referenced in comment bodies (beyond headers)

- `lib/khand.smlib:8` — `lib/string.smlib`
- `lib/nighantu.smlib:8` — `lib/hash.smlib`
- `lib/roop.smlib:8,10` — `lib/strconv.smlib`, `fmt` / `strconv` as module names
- `lib/sangrah.smlib:6` — `lib/map.smlib`
- `lib/sankhyiki.smlib:120` — `lib/sort.smlib`
- `lib/vakyank.smlib:8` — `lib/baseconv.smlib`
- `lib/varna.smlib` body — `baseconv`, `strconv`, `strb.smlib` references in history notes

## F. Other pre-rename keywords checked — zero in lib/

`punaravartana`, `pratiyati`, `uddeshya`, `anytra`, `nishedha`, `parigrah`,
`nishkriya`, `srijana`: 0 occurrences each. (`anyatra` in
`lib/kalana.smlib:64` is the current keyword, not the listed old `anytra`.)
`to` as a Sutram keyword: 0 in code; English "to" in prose is not old vocabulary
and is excluded.

## G. Excluded (generic English, not old vocabulary)

`list`, `map`, `set`, `array`, `string`, `file`, `hash`, `result`, `sort`
used as ordinary English nouns/verbs in comments (e.g. "a list", "map it to a
range", "set all n digits to 0") are not module references and are not listed
above, except where they appear as `lib/<old>.smlib` (sections B/E).
