# Sutram R90 WS1 — Reconcile 36 extra keyword-placeholder candidates

**Result:** The two checkers disagree on *what merits stylistic review*, not on structural validity. R83 and Claude R21 both found **0 hard violations** in 1,408 message rows. R83 surfaced 36 optional 'extra `{kw:...}`' reviews; Claude surfaced zero because each keyword appears no more often than in the original romanized message. **For structural validity, Claude's baseline is more appropriate.** Preserve our flags as optional human-language wording suggestions, not required corrections or proven bugs.

**Sources:** `tools/r83_pack_structure.py` (R83 checker), `Claude-to-Sarvam/evidence-r21/pack_structure_check.py` (Claude checker), current `lang/*.sandesh`, and each message's adjacent `# "default"` comment. The exact decoded rows, including the full current string and old source string, are in [ROUND-90-WS1-36-PLACEHOLDERS.json](ROUND-90-WS1-36-PLACEHOLDERS.json). Original source snapshot pinned to v253 (`7ec9c9b5`); all six `.sandesh` blobs match the R83 source identities.

## Why the rules differ

1. **R83's multiplicity rule:** Count `{kw:WORD}` occurrences in the translated message and in the **Sanskrit `.sandesh` message**. When `translated > Sanskrit`, record an **optional review candidate**, *not a hard violation*. Sanskrit often translates the prose occurrence of `vitti` or `mala` into ordinary words, so it has fewer placeholders.
2. **Claude R21's rule:** Read the adjacent romanized Sanskrit **default comment**, count how often the literal `WORD` appears (including code examples and explanatory prose), and flag only when the translated `{kw:WORD}` count **exceeds the original word count**. None of these 36 exceeds the original count. Every `{kw:vitti}` and `{kw:mala}` refers to a real keyword in the target pack, independently verified in all six current `.lang` alias files.
3. **Decision:** Correctness checks should reject missing canonical tokens and invalid substitutions, but should **not** automatically treat translation into a code-keyword marker rather than a normal prose term as wrong. Our rule is more conservative as an *editorial review heuristic*, not a structural condition. Claude is right to report **0 extra-placeholder structural warnings** under its rule; our 36 count remains true relative to the Sanskrit placeholder pattern. Neither proves grammar or wording quality.

## Every flagged occurrence, grouped by language pack

Count columns show **Sanskrit markers / draft markers / original default Roman word occurrences**. The value is `0 / 1 / 1` or `1 / 2 / 2` for all 36; none exceeds the original default's word frequency.

### Punjabi (6 flags)

| # | Source line | Message key | Extra marker | Sanskrit / draft / default |
|---:|---:|---|---|---|
| 1 | 85 | `msg_kosh_required` | `{kw:vitti}` | 0 / 1 / 1 |
| 2 | 119 | `msg_shell_help` | `{kw:vitti}` | 1 / 2 / 2 |
| 3 | 119 | `msg_shell_help` | `{kw:mala}` | 1 / 2 / 2 |
| 4 | 149 | `msg_var_table_overflow` | `{kw:vitti}` | 0 / 1 / 1 |
| 5 | 181 | `r56_msg_global_capacity` | `{kw:vitti}` | 0 / 1 / 1 |
| 6 | 183 | `r56_msg_global_duplicate` | `{kw:vitti}` | 0 / 1 / 1 |

### Odia (6 flags)

| # | Source line | Message key | Extra marker | Sanskrit / draft / default |
|---:|---:|---|---|---|
| 7 | 85 | `msg_kosh_required` | `{kw:vitti}` | 0 / 1 / 1 |
| 8 | 119 | `msg_shell_help` | `{kw:vitti}` | 1 / 2 / 2 |
| 9 | 119 | `msg_shell_help` | `{kw:mala}` | 1 / 2 / 2 |
| 10 | 149 | `msg_var_table_overflow` | `{kw:vitti}` | 0 / 1 / 1 |
| 11 | 181 | `r56_msg_global_capacity` | `{kw:vitti}` | 0 / 1 / 1 |
| 12 | 183 | `r56_msg_global_duplicate` | `{kw:vitti}` | 0 / 1 / 1 |

### Tamil (6 flags)

| # | Source line | Message key | Extra marker | Sanskrit / draft / default |
|---:|---:|---|---|---|
| 13 | 85 | `msg_kosh_required` | `{kw:vitti}` | 0 / 1 / 1 |
| 14 | 119 | `msg_shell_help` | `{kw:vitti}` | 1 / 2 / 2 |
| 15 | 119 | `msg_shell_help` | `{kw:mala}` | 1 / 2 / 2 |
| 16 | 149 | `msg_var_table_overflow` | `{kw:vitti}` | 0 / 1 / 1 |
| 17 | 181 | `r56_msg_global_capacity` | `{kw:vitti}` | 0 / 1 / 1 |
| 18 | 183 | `r56_msg_global_duplicate` | `{kw:vitti}` | 0 / 1 / 1 |

### Telugu (6 flags)

| # | Source line | Message key | Extra marker | Sanskrit / draft / default |
|---:|---:|---|---|---|
| 19 | 85 | `msg_kosh_required` | `{kw:vitti}` | 0 / 1 / 1 |
| 20 | 119 | `msg_shell_help` | `{kw:vitti}` | 1 / 2 / 2 |
| 21 | 119 | `msg_shell_help` | `{kw:mala}` | 1 / 2 / 2 |
| 22 | 149 | `msg_var_table_overflow` | `{kw:vitti}` | 0 / 1 / 1 |
| 23 | 181 | `r56_msg_global_capacity` | `{kw:vitti}` | 0 / 1 / 1 |
| 24 | 183 | `r56_msg_global_duplicate` | `{kw:vitti}` | 0 / 1 / 1 |

### Kannada (6 flags)

| # | Source line | Message key | Extra marker | Sanskrit / draft / default |
|---:|---:|---|---|---|
| 25 | 85 | `msg_kosh_required` | `{kw:vitti}` | 0 / 1 / 1 |
| 26 | 119 | `msg_shell_help` | `{kw:vitti}` | 1 / 2 / 2 |
| 27 | 119 | `msg_shell_help` | `{kw:mala}` | 1 / 2 / 2 |
| 28 | 149 | `msg_var_table_overflow` | `{kw:vitti}` | 0 / 1 / 1 |
| 29 | 181 | `r56_msg_global_capacity` | `{kw:vitti}` | 0 / 1 / 1 |
| 30 | 183 | `r56_msg_global_duplicate` | `{kw:vitti}` | 0 / 1 / 1 |

### Malayalam (6 flags)

| # | Source line | Message key | Extra marker | Sanskrit / draft / default |
|---:|---:|---|---|---|
| 31 | 85 | `msg_kosh_required` | `{kw:vitti}` | 0 / 1 / 1 |
| 32 | 119 | `msg_shell_help` | `{kw:vitti}` | 1 / 2 / 2 |
| 33 | 119 | `msg_shell_help` | `{kw:mala}` | 1 / 2 / 2 |
| 34 | 149 | `msg_var_table_overflow` | `{kw:vitti}` | 0 / 1 / 1 |
| 35 | 181 | `r56_msg_global_capacity` | `{kw:vitti}` | 0 / 1 / 1 |
| 36 | 183 | `r56_msg_global_duplicate` | `{kw:vitti}` | 0 / 1 / 1 |

## Example showing why both measurements are correct

```text
romanized original:
  vitti x = 5             vitti-ghoshana
Sanskrit translation:
  {kw:vitti} x = 5        वित्ति-घोषणा
Tamil draft:
  {kw:vitti} x = 5        {kw:vitti} அறிவிப்பு
```
The romanized original writes `vitti` **twice**. Sanskrit translates the second occurrence into Devanagari prose and retains **one** keyword marker; Tamil uses **two** markers. The extra marker expands to the selected language's `vitti` keyword and is not inherently malformed. A Tamil speaker might prefer ordinary prose rather than a pasted keyword; a compiler parser cannot determine that.

## Sarvam recommendation

**Adopt Claude's printed-default frequency rule for automatic structural severity.** Reclassify R83's 36 occurrences as permitted differences / **OPTIONAL EDITORIAL REVIEW**, not hard defects and not blockers for the eight DRAFT packs. Retain the historical R83 and R87 JSON audits unchanged; add this reconciliation so nobody mistakes 41 historical review candidates for 41 errors. The five identical short-string candidates remain a separate stylistic heuristic; the two Hindi examples were deemed natural and left unchanged.

**Tests actually performed:** fetched and decoded all six current draft `.sandesh` sources, canonical Sanskrit, R83 inventory, and both checker implementations; matched 36/36 flags, source line numbers, and per-marker counts; confirmed all six `.lang` keyword alias files contain `vitti` and `mala`. **Native compiler, translation quality, Windows acceptance: NOT_RUN.** No source or accepted pack changes.
