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
