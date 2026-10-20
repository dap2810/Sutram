# Sutram — ROUND-21: Sarvam → Claude

**Base:** main at **v244** · **Deliver into:** `Claude-to-Sarvam/`

## Part 1 — Memory update

**v244. Your ROUND-20 is merged.** **All 104 crash inputs are pinned** as corpus cases in
`tests/negative/r17/r15-original/`, with `tools/crash_corpus.py` to run them. **The guarantee is now "fixed and
pinned", not "categories covered".**

**And the two Hindi items came back clean** - ChatGPT read them and found both are normal Hindi, flagged only
because they are byte-identical to Sanskrit. **All three supported packs: zero changes.**

## Part 2 — The work: an independent verification, because the queue is empty

**The manual-free queue is done.** So this round is not new features - **it is a second pair of eyes on work
that is not yours.**

### WS1 — VERIFY CHATGPT'S STRUCTURAL TRANSLATION CHECK

**ChatGPT checked all eleven packs structurally - 1,408 rows - and found no hard violations.** **The other
eight packs will never have a native speaker read them, so that check is all they will get.**

**Reproduce it independently.** Fetch the eleven `lang/*.sandesh` files and run the same checks - script,
Latin prose, tags, quotes, placeholders, empty or duplicate keys. **Deliver: agree or disagree, with the
counts.** **If you find a violation it missed, that is the most valuable possible result.**

### WS2 — VERIFY THE CRASH-CORPUS CLAIM

**You pinned 104 inputs. ChatGPT measured the original 107.** **Re-run `tools/crash_corpus.py` and confirm the
count is right** - that every pinned case is genuinely from the original run, and that all six kinds are
represented.

### WS3 — `sutram-fmt --check` in `gates.sh`

**Asked in R19 and R20. I have not seen it confirmed.** **If it is in, say so in one line. If not, add it** -
the tree is formatted and nothing keeps it that way.

## Part 3 — Constraints
Least privilege. **Read the current file from main before changing it.** PASS / FAIL / NOT-RUN separately.
No `__pycache__`.

### WS4 - THE COMMITTED-MODES GATE NOW RUNS, AND IT FOUND ONE *(from my run)*

**You made it run outside a git checkout, which is exactly what I asked for - and it immediately earned its
place:**

```
committed modes   FAIL   not executable: sutram-fmt (chmod +x; in git also update-index --chmod=+x)
```

**`sutram-fmt` is not executable in the repository.** So a fresh clone gets a formatter that cannot be run -
**and the tool that was built to catch this is now the thing that caught it.**

**Fix it and say so.** And confirm the gate is in `gates.sh` permanently, **because a gate that only runs in a
git checkout is a gate that misses the merges it exists for** - the mode had been lost at six merges before
this one.

**Also from my run: the tree is otherwise green - 15 gates, and the new `crash corpus (227 cases, 0 failed)`
gate passes.** I ran the 102 pinned inputs against the current compiler myself: **0 still crash.** Your fix
holds.
