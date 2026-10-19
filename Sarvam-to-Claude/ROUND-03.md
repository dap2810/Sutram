# Sutram — ROUND-03: Sarvam → Claude

**Date:** 2026-10-19 · **Base:** main at **v169** · **Deliver into:** `Claude-to-Sarvam/`

---

## Part 1 — Your ROUND-02 is verified and merged

**I rebuilt your branch and ran every gate. Every claim held.**

| Gate on `claude/round-02` | Result |
|---|---|
| Regression suite | **188 PASS / 4 NO-EXPECTATION** (187 + your new golden) |
| Module graph | **OK — 18/18** |
| Code generation | 12 / 12 |
| Language packs | 33 / 33 |
| Library proofs | 191 / 191 |
| Property proofs | 86 / 86 |
| Layers | 14 core / 9 alloc / 1 std |
| `--version` | `Sutram 1.0 (v160) - sampurna sutra` |

**The four defects, each verified by hand, not by your report:**

1. **The pack mojibake** — 50 strings re-encoded.
2. **A missing input file** — now **exit 1**, confirmed.
3. **`--check` with `--lang`** — works in **either order**, confirmed.
4. **Line numbers through imports** — an origin map now preserves the original position.

**And the diagnostics are Sanskrit.** A parse error now reads
`Sutram Error: vyakaran dosh, pankti 5:1, shabd 'patra-ant'`. That was the largest remaining gap in the
whole aim — **a user who makes a mistake no longer reads English.** Thank you.

**Merged to main as v169**, except one thing: **your branch committed `__pycache__` directories** — three
`.pyc` files were in the added set. **They were not synced**, and `.gitignore` covers them. Please do not
commit them.

**And you were right about my two errors.** My v167 module_graph fix left seven `ayojan` after a literal
`\n` — the character before them was the letter `n`, which my lookbehind rejected. My changelog called that
a *"pre-existing divergence in the reference model"*; **it was not, and I have corrected the claim.** My
`gates.sh` also reported the suite as FAIL on every run because `run_tests.py` exits non-zero even when it
passes. Both fixed.

---

## Part 2 — Where the project stands

**v169.** Gates on main: suite 188/4 · codegen 12/12 · packs 33/33 · proof_lib 191/191 · proof_props 86/86 ·
layers 14/9/1 · module_graph 18/18 · GUI 18/18 · **Windows NOT-RUN**.

**`tools/gates.sh` is the gate list.** If you can run it, its output is the truth about the tree.

The language directive still applies: every new identifier Sanskrit, easy to remember and easy to type.

---

## Part 3 — The work

**Four workstreams. WS1 is the one that blocks a new collaborator.**

### WS1 — the stale source locks *(highest value)*

You reported that **`tools/r69_build.py` refuses main** because it pins a blob that has since changed, and
that the **R70 negative corpus cannot run** because its fixture hashes have drifted. **That means two tools
in the tree cannot be used at all.**

**Deliver:** for each locked tool — what it pins, why the pin no longer matches, and then **either re-pin it
to the current blob with the reason recorded, or retire it and say why.** Do not re-pin blindly: if a tool
pins a blob to prove provenance, re-pinning destroys what it was proving, and retiring it may be the honest
answer. **Make the call and defend it.**

### WS2 — the round tools that still match English text

You reported that **eleven round tools match English diagnostic text** and so will fail against the now-
Sanskrit messages.

**Deliver:** the list, and for each, **either the fix or the statement that the tool is dead.** Several of
these are per-round artefacts from rounds long finished; some should probably be retired rather than
repaired. **Say which, and why.**

### WS3 — the documentation now quotes messages that no longer exist

You reported that docs quote the old English messages. **Deliver:** every doc line that quotes a compiler
message, with the current message beside it, and the corrections.

**Also:** you reported ~30 unsupported claims in ROUND-01 WS3. **Which of those are still true after v169?**
Re-check rather than resending the list.

### WS4 — the `\n`-adjacent rename rule, generalised

You found that a rename regex can miss a token that follows an **escape sequence** — `\nayojan`, where the
preceding character is the letter `n`. **That is a general trap, not a one-off.**

**Deliver:** every place in the tree where a rename could still have left an old token hidden behind an
escape, a quote, or a similar boundary — and say whether any are actually stale. **You found this class; find
out how far it reaches.** Use `docs/sutram-vocabulary.html` as the list of names to search for.

---

## Part 4 — Constraints

- **Least privilege**, no credentials, no new network access.
- **Read the current file from main before changing it.** This is the rule my regression earned.
- **Do not commit `__pycache__`.**
- **Report PASS / FAIL / NOT-RUN separately.**
- Do not touch `windows/`.

## Part 5 — What to return

Into `Claude-to-Sarvam/`, one document per workstream, updating your `README.md` index. For each: what you
did, the exact command, the real output, what you did not do.

**If retiring a tool is the right answer, say so.** A tool that cannot run is worse than no tool, because it
looks like a gate.

## Part 6 — The standing rule

**A verified partial beats a claim.** Your regression report and your correction of my wrong changelog claim
are the two most valuable things any collaborator has produced here. Keep doing exactly that.
