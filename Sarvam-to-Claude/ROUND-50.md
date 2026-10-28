# Sutram — ROUND-50: the three defects Windows found, and they do not wait on the vocabulary review

**Base:** main at **v390**, compiler **v254** · **Deliver into:** `Claude-to-Sarvam/`

## Read first
`LANGUAGE-PRIORITY.md`, `docs/OPEN-ISSUES.md`, and **`Windows-to-Sarvam/WIN-TEST-2026-10-27.md`** — the Windows run that
found these three. My answers are in `Sarvam-to-Claude/ANSWER-WIN-TEST-2026-10-27.md`.

## Why this round now
**The vocabulary review is with ChatGPT and Muse and will take time.** **These three are independent of it** — **they are
about error messages and one word's spelling, not about naming.** **So they can be fixed while the review runs.**

---

## WS1 — `Sutram Error` must be `Sutram dosh`

**74 occurrences in `src/sutram_compiler.asm`.** **The rule is no English, and the language already has the word: `dosh`
is a keyword meaning fault.**

```
Now:    Sutram Error: riktat koshat kosh_pop
After:  Sutram dosh: riktat koshat kosh_pop

Now:    Sutram Error [E_UNDEFINED_NAME]: ...
After:  Sutram dosh [E_UNDEFINED_NAME]: ...
```

**Keep every `[E_*]` code exactly as it is.** **A machine-readable symbol is not prose.**

**Then the suite, the corpus, and the guard.** **Every test that asserts on an error message needs its golden updated —
say how many, and show one before/after.** **The two negative tests I know of are `120_t18_kosh_param_mismatch` and
`121_t18_kosh_param_push_reject`; there will be more.**

**If any code matches on the literal `Sutram Error`, STOP and report before changing it.** **A test that greps for the old
string is a test that silently stops testing.**

## WS2 — one word, three forms: `प्रति`

**The owner has decided the Latin keyword stays `prati`.** **So this is not a rename — it is making the pack and the
compiler agree on one Devanagari form.**

| Where | Now | After |
|---|---|---|
| `lang/sanskrit.lang:18` | `प्रतियाति prati` | **`प्रति prati`** |
| `lang/sanskrit.lang:74` | `प॰ prati` | **`प्रति prati`** |
| `src/sutram_compiler.asm` `kw_dev_pratiyati` | bytes for `प्रत्यायति` | **bytes for `प्रति`** |

**Bytes for `प्रति`:** `0xE0,0xA4,0xAA,0xE0,0xA5,0x8D,0xE0,0xA4,0xA4,0xE0,0xA4,0xBF` — **verify that decodes before using it.**

**And list every other site in the tree that uses either old spelling** — docs, examples, tests. **Every one, not a
sample.**

## WS3 — `--lang sanskrit` should not be needed

**The compiler has 34 Devanagari keywords built in, so some Devanagari works without the flag and the rest does not.**
**That inconsistency is the defect.**

**Option A (my recommendation): make `--lang sanskrit` the default**, so the flag is only needed for the other packs.
**One default, not five more byte strings.**

**Option B: complete the built-in table** so all 39 keywords are in the compiler.

**Pick one and say why.** **If A breaks the pack mechanism, say so and do B.** **Then re-run the Devanagari test WITHOUT
the flag and report the result.**

## WS4 — the guard, the suite, the corpus, the proofs

**State every number.** **PASS / FAIL / NOT-RUN separately.** **Do not touch `backups/` or `Windows-to-Sarvam/`.**

---

## What to return
`Windows-to-Sarvam` is for the owner's machine; **deliver into `Claude-to-Sarvam/R50-00-HANDBACK.md`** with:
1. A results table — WS1 / WS2 / WS3 / WS4
2. **The golden count from WS1, with one before/after**
3. **The full `prati` site list from WS2**
4. **Which option you chose in WS3 and why**
5. **The guard numbers** — programs, byte-identical, refused, DIFFER, and every differ named
6. **Anything surprising**

**Do not touch the vocabulary.** **The 211 proposed names are with ChatGPT and Muse and the owner reviews before anything
is applied.**
