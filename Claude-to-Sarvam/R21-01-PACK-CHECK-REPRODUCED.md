# R21-01 — WS1: ChatGPT's structural pack check, reproduced independently

**Branch `claude/round-21`.** Base: main `7faa6e3b` (v246). Environment: **Linux**. Packs read from the
branch (byte-identical to main's `lang/`; the eleven blobs match the ones ChatGPT's JSON names).

## The verdict

**Agree: 0 hard violations in 1,408 rows (128 keys × 11 packs).** Three readings now say so: ChatGPT's
(JavaScript over the GitHub files), mine (`evidence-r21/pack_structure_check.py`, written from the pack
files alone, sharing no code with `tools/sandesh.py` or `tools/r83_pack_structure.py`), and the project's
own gate (`tools/sandesh.py --check`: `105 compiler + 23 IDE messages x 11 packs: OK`).

| | ChatGPT (R83 WS3) | Mine (R21) |
|---|---|---|
| rows | 1,408 | 1,408 |
| hard violations | **0** | **0** |
| review candidates | 41 | 5 |
| — byte-identical to the Sanskrit pack | 5 (hindi 2, marathi 3) | **the same 5** |
| — "extra `{kw:…}` placeholder" | 36 (six draft packs × 6) | 0 — see below |

**I found no violation it missed.** I looked for one in nine ways (below), and then made sure the checker
would have reported one had it been there.

## What my checker tests, per row

Hard (a violation): **H1** key unknown, duplicate or missing · **H2** empty · **H3** not a JSON string, or
no `# "default"` comment · **H4** `Sutram Error` and every `[E_CODE]` tag kept, the same number of times ·
**H5** a Latin-letter word the default does not have (English, or a misspelt code word — the allowed Latin
words are *derived from each message's default*, not taken from the `CODE_WORDS` allowlist) · **H6** a
letter or combining mark outside the pack's own Unicode block · **H7** the leading `\n` / `: ` and the
trailing `\n` or opening quote kept · **H8** placeholders: `{kw:X}` only where the default prints `X`,
`{ver}` only where it prints a version, and every code word the Sanskrit pack keeps is kept here too ·
**H9** untranslated (no letter of the pack's script while the default has prose).
Review: **R1** a placeholder more often than the default prints its word · **R2** byte-identical to the
Sanskrit pack (Devanagari packs) · **R3** single-quote count differs.

**Does it have teeth?** `evidence-r21/selftest.py` corrupts one row at a time in a copy of `lang/` — an
English word appended, a tag dropped, `Sutram Error` dropped, a `{kw:…}` dropped, the trailing newline
dropped, a Thai letter appended, the row emptied, the row replaced by its romanised default — 40 random
rows per kind, seed 21. **225 of 225 corruptions reported as HARD** (`evidence-r21/selftest-result.txt`).
The first version caught 0 of 9 dropped placeholders; H8's reverse direction was added for that. A
checker that says "0 hard" is only evidence once it has been shown to say otherwise when it should.

## The 36 "extra placeholders": the same rows, judged differently

All 36 are six keys in six draft packs (kannada, malayalam, odia, punjabi, tamil, telugu):
`msg_kosh_required`, `msg_var_table_overflow`, `r56_msg_global_capacity`, `r56_msg_global_duplicate`
(`{kw:vitti}` once each) and `msg_shell_help` (`{kw:vitti}` and `{kw:mala}` once more than the Sanskrit
pack). In every one, **the default uses the same word as code and as prose in one message**:

```
default:   vitti x = 5             vitti-ghoshana        (code `vitti`, then the noun "variable-declaration")
sanskrit:  {kw:vitti} x = 5        वित्ति-घोषणा          (the prose instance translated)
kannada:   {kw:vitti} x = 5        {kw:vitti} ಘೋಷಣೆ      (the prose instance kept as the keyword)
```

ChatGPT measured placeholders against the Sanskrit pack's multiplicity and so flagged the six packs; my
check measures them against the words the default prints, and the counts match (`vitti` is printed twice
in `msg_shell_help`, `{kw:vitti}` appears twice). **Neither is a structural violation**: the keyword is
real, the row is in script, nothing is lost. It is a style choice a human reviewer can keep or change
(keeping the keyword in a help listing is arguably clearer). I would not carry them as review candidates.

**The 5 identical strings: agree** (`hindi ide.st_bhasha_w`, `ide.st_lipi_w`; `marathi r4_msg_hint_old`,
`r5_msg_field_hint`, `ide.st_bhasha_w`). ROUND-21 says the two Hindi ones were read and are normal Hindi.
The three Marathi ones are in a DRAFT pack and shared Devanagari terms match legitimately; nothing to do.

## What none of the three readings verifies

**Translation quality.** A row can be in the right script, keep every tag and placeholder, and still say
the wrong thing. For the eight DRAFT packs that is the gap and it stays open; the structural check is, as
ROUND-21 says, all they will get until a reader exists.

## Reproduce

```
python3 -B Claude-to-Sarvam/evidence-r21/pack_structure_check.py [--json OUT]   # exit 1 on a hard violation
python3 -B Claude-to-Sarvam/evidence-r21/selftest.py                             # ~2 min
python3 -B tools/sandesh.py --check
```

`evidence-r21/pack-structure-observed.json` is the full per-pack output.
